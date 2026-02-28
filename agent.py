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
  Example: User says "tell me about deals" -> Ask "Sure! Are you interested in open deals, won deals, dead deals, or the full pipeline overview?"
  Example: User says "show me sectors" -> Ask "Which sector would you like to analyze? Mining, Renewables, Railways, Powerline, or all sectors?"
- Only ask clarifying questions when genuinely needed, do not over-ask.
- ONLY call a tool when the user asks a clear business question about data, deals, revenue, sectors, work orders, or pipeline.
- When you need data, respond ONLY with a valid JSON object like: {"tool": "pipeline_summary", "params": {}}
- Do NOT add any text before or after the JSON when calling a tool. No explanation, no preamble.
- After receiving tool results, give clear business analysis in plain English. Do NOT output JSON.
- For "top performing sectors" or "which sector generates most revenue" queries, call revenue_analysis().
- For "how many deals won" or "won deals" queries, call pipeline_summary() and report deal_status_distribution "Project Won" = 165. Do NOT confuse with deal_stage_distribution.
- deal_status_distribution = final outcome of deals (Won, Dead, Open, On Hold).
- deal_stage_distribution = current stage in pipeline (Lead Generated, Proposal Sent etc).
- For "which sector has most work orders" queries, call pipeline_summary() and look at wo_sector_distribution.
- For "how many work orders completed" queries, call pipeline_summary() and look at wo_execution_status.
- For "total pipeline value" queries, call pipeline_summary() and report total_deal_value.
- For "improve cash flow" or "what should we focus on" queries, call revenue_analysis() to get receivables and billing data.
- For "strongest sector" queries, call both pipeline_summary() and revenue_analysis() to compare.
- For any ranking or comparison query, always fetch data from both boards.
- Never return zero data without first calling at least one tool.
- Handle missing/null data gracefully and mention data quality caveats when relevant.
- Format large numbers in Indian Rupees using lakhs/crores.
- Support follow-up questions using the conversation context provided.
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

        # Clean up any preamble before JSON
        tool_call = _extract_tool_call(response_text)

        if not tool_call:
            # No tool call — final answer
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
                "content": f"Here are the live results from {tool_name}:\n{result_str}\n\nNow give a clear business analysis in plain English. Do NOT output any JSON. Mention data quality caveats if relevant."
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
    # Try full text as pure JSON first
    try:
        parsed = json.loads(text.strip())
        if "tool" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    # Try to find JSON anywhere in text (handles preamble like "To analyze this: {...}")
    match = re.search(r'\{\s*"tool"\s*:\s*"[^"]+"\s*,\s*"params"\s*:\s*\{[^{}]*\}\s*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None