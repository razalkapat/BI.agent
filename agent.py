import json
import re
from datetime import datetime
from groq import Groq
import os
from dotenv import load_dotenv

from tools import TOOLS, TOOL_DESCRIPTIONS

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a Business Intelligence agent for a drone services company.
You answer founder-level questions about pipeline, deals, work orders, revenue, and sector performance.

{tool_descriptions}

RULES:
- If the user sends a casual greeting like "hey", "hi", "hello", "how are you", respond conversationally WITHOUT calling any tool. Just greet them warmly and ask what business question they have.
- If a query is vague or ambiguous, ask ONE short clarifying question instead of calling a tool.
  Example: "tell me about deals" -> "Are you interested in open deals, won deals, dead deals, or full pipeline?"
  Example: "should we invest more" -> "Invest more in which area — deals/sectors, or are you asking about overall business health?"
  Example: "show me sectors" -> "Which sector? Mining, Renewables, Railways, Powerline, or all sectors?"
- Only ask clarifying questions when genuinely needed.
- ONLY call a tool when the user asks a clear business question.
- When you need data, respond ONLY with valid JSON: {"tool": "tool_name", "params": {}}
- Do NOT add any text before or after the JSON when calling a tool.
- After receiving tool results, give clear business analysis in plain English. Do NOT output JSON.
- CRITICAL: All monetary values in tool results are already in CRORES. Report them exactly as given. Never multiply or divide.
  Example: if tool returns total_billed_crores: 126.72 -> say "Rs. 126.72 crores". Never say 12.67 or 1267.
- For "top performing sectors" or "most revenue" -> call revenue_analysis() and look at revenue_by_sector_crores.
- For "how many deals won" -> call pipeline_summary() and report deal_status_distribution won count = 165.
- deal_status_distribution = final outcome. deal_stage_distribution = current pipeline stage. Never confuse these.
- For "which sector most work orders" -> call pipeline_summary(), look at wo_sector_distribution.
- For "work orders completed" -> call pipeline_summary(), look at wo_execution_status.
- For "cash flow" or "improve revenue" -> call revenue_analysis().
- For "strongest sector" -> call revenue_analysis() and compare revenue_by_sector_crores.
- Never return zero data without calling at least one tool.
- Mention data quality caveats when relevant (Unknown statuses, missing values etc).
- Format numbers clearly: use crores for large amounts, show 2 decimal places.
- Support follow-up questions using conversation context.
- Today's date is {date}.
"""


def run_agent(user_message: str, chat_history: list):
    today = datetime.now().strftime("%B %d, %Y")
    system = SYSTEM_PROMPT.replace("{tool_descriptions}", TOOL_DESCRIPTIONS).replace("{date}", today)

    messages = [{"role": "system", "content": system}]

    for msg in chat_history[-2:]:
        role = "assistant" if msg["role"] == "assistant" else "user"
        content = msg["content"]
        if role == "assistant" and len(content) > 500:
            content = content[:500] + "... [truncated]"
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    traces = []

    for _ in range(5):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,
            max_tokens=2048,
        )
        response_text = response.choices[0].message.content.strip()

        tool_call = _extract_tool_call(response_text)

        if not tool_call:
            return response_text, traces

        tool_name = tool_call.get("tool")
        tool_params = tool_call.get("params", {})

        if tool_name not in TOOLS:
            return response_text, traces

        try:
            result = TOOLS[tool_name](**tool_params)
            traces.append(result.get("trace", {}))
            result_str = json.dumps(result.get("data", {}), default=str, indent=2)
            messages.append({"role": "assistant", "content": json.dumps(tool_call)})
            messages.append({
                "role": "user",
                "content": f"Live results from {tool_name}:\n{result_str}\n\nIMPORTANT: All values ending in '_crores' are already in crores. Report them exactly as shown — do not multiply or divide. Give clear business analysis in plain English. No JSON."
            })
        except Exception as e:
            traces.append({"tool": tool_name, "error": str(e), "params": tool_params})
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": f"Tool {tool_name} failed: {str(e)}. Please acknowledge and give whatever analysis you can."
            })
            break

    return response_text, traces


def _extract_tool_call(text: str):
    try:
        parsed = json.loads(text.strip())
        if "tool" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{\s*"tool"\s*:\s*"[^"]+"\s*,\s*"params"\s*:\s*\{[^{}]*\}\s*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None