# BI Agent — monday.com Business Intelligence

A production-ready AI agent that answers founder-level business intelligence queries using live data from monday.com.

## Live Demo
[[[https://biagent.streamlit.app](https://biagent-biagent.streamlit.app/

## GitHub
[github.com/razalkapat/BI.agent](https://github.com/razalkapat/BI.agent)

## Features
- Live monday.com GraphQL API — zero caching, every query is fresh
- Natural language questions → plain English business insights
- ReAct agent loop — up to 5 tool calls per query
- 🔬 Tool trace panel — see every API call, board queried, records returned
- 5 specialized BI tools covering pipeline, revenue, and sector analysis
- Ambiguous query detection — asks clarifying questions when needed
  

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/razalkapat/BI.agent
cd BI.agent
```

### 2. Install dependencies
```bash
pip install streamlit groq requests python-dotenv
```

### 3. Configure environment
Create a `.env` file:
```
MONDAY_API_KEY=your_monday_api_key
GROQ_API_KEY=your_groq_api_key
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
DEALS_BOARD_ID=your_deals_board_id
```

### 4. Run
```bash
streamlit run app.py
```

## File Structure
```
BI.agent/
├── app.py          # Streamlit chat UI
├── agent.py        # Groq AI ReAct agent loop
├── tools.py        # 5 BI tool functions
├── monday_api.py   # monday.com GraphQL API layer
├── config.py       # Environment config
├── requirements.txt
└── .env            # API keys (not committed)
```

## Tools
| Tool | Description |
|---|---|
| `pipeline_summary` | Full overview — deals, work orders, revenue |
| `revenue_analysis` | Billing, collection rate, receivables by sector |
| `sector_analysis(sector)` | Deep dive into one sector |
| `get_deals(filters)` | Filtered deal list |
| `get_work_orders(filters)` | Filtered work order list |

## Sample Queries
- "What's our overall pipeline?"
- "Show revenue and billing analysis"
- "Mining sector performance"
- "Where are we losing the most deals?"
- "Which sector generates the most revenue?"
- "What should we focus on to improve cash flow?"

## Tech Stack
- **UI**: Streamlit
- **AI**: Groq — Llama 3.3 70B
- **Data**: monday.com GraphQL API v2024-01
- **Deployment**: Streamlit Cloud
