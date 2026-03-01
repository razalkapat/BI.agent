import streamlit as st
from config import validate_config
from agent import run_agent

st.set_page_config(page_title="BI Agent", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

#MainMenu {visibility: hidden;}
header[data-testid="stHeader"] {display: none !important;}
footer {visibility: hidden;}
.block-container {padding: 0 !important; max-width: 100% !important;}
* { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: #f0ede8; color: #1c1917; }
.stApp { background: #f0ede8; }

/* SIDEBAR */
section[data-testid="stSidebar"] { background: #1c1917; }
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; color: #57534e !important;
    border: 1px solid #2c2825 !important; font-size: 0.74rem !important;
    padding: 8px 10px !important; border-radius: 4px !important;
    width: 100% !important; text-align: left !important;
    transition: all 0.15s !important; margin-bottom: 4px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2c2825 !important; border-color: #ef4444 !important; color: #f0ede8 !important;
}
.sb-logo { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #f0ede8; display: flex; align-items: center; gap: 8px; padding: 24px 20px 4px; }
.sb-logo-dot { width: 8px; height: 8px; background: #ef4444; border-radius: 50%; display: inline-block; animation: blink 2s infinite; }
.sb-tagline { font-size: 0.62rem; color: #44403c; letter-spacing: 2px; text-transform: uppercase; font-family: 'DM Mono', monospace; padding: 0 20px 16px; border-bottom: 1px solid #2c2825; }
.sb-section { font-size: 0.6rem; color: #44403c; text-transform: uppercase; letter-spacing: 2px; font-family: 'DM Mono', monospace; padding: 14px 20px 8px; font-weight: 600; }
.sb-source { display: flex; align-items: center; gap: 8px; padding: 6px 20px; font-size: 0.76rem; color: #78716c; border-bottom: 1px solid #2c2825; }
.source-dot { width: 6px; height: 6px; background: #22c55e; border-radius: 50%; display: inline-block; animation: blink 3s infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.2;} }

/* TOP BAR */
.top-bar { background: #1c1917; padding: 0 32px; height: 52px; display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #ef4444; }
.top-bar-left { font-family: 'Syne', sans-serif; font-size: 0.72rem; font-weight: 600; color: #57534e; letter-spacing: 3px; text-transform: uppercase; }
.top-bar-right { display: flex; align-items: center; gap: 20px; }
.top-bar-item { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #44403c; letter-spacing: 1px; }
.top-bar-live { display: flex; align-items: center; gap: 6px; font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #22c55e; letter-spacing: 1px; }
.live-dot { width: 6px; height: 6px; background: #22c55e; border-radius: 50%; animation: blink 1.5s infinite; display: inline-block; }

/* HERO */
.hero { padding: 28px 32px 20px; background: #f0ede8; border-bottom: 1px solid #ddd8d0; }
.hero-title { font-family: 'Syne', sans-serif; font-size: 2.4rem; font-weight: 800; color: #1c1917; line-height: 0.95; letter-spacing: -2px; margin-bottom: 8px; }
.hero-title span { color: #ef4444; }
.hero-desc { font-size: 0.8rem; color: #78716c; line-height: 1.6; }

/* CHAT MESSAGES */
.chat-wrap { padding: 20px 32px 8px; }
.msg-user-label { font-family: 'DM Mono', monospace; font-size: 0.58rem; color: #a8a29e; letter-spacing: 1.5px; text-transform: uppercase; text-align: right; margin-bottom: 5px; }
.msg-user { background: #1c1917; color: #f0ede8; border-radius: 16px 16px 4px 16px; padding: 12px 18px; margin: 0 0 20px 25%; font-size: 0.9rem; line-height: 1.6; }
.msg-agent-label { font-family: 'DM Mono', monospace; font-size: 0.58rem; color: #ef4444; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; font-weight: 600; }
.msg-agent { background: #fff; border: 1px solid #ddd8d0; border-left: 4px solid #ef4444; border-radius: 0 16px 16px 16px; padding: 16px 20px; margin: 0 25% 8px 0; font-size: 0.9rem; line-height: 1.8; color: #1c1917; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }

.empty-state { text-align: center; padding: 48px 20px; }
.empty-big { font-family: 'Syne', sans-serif; font-size: 3.5rem; font-weight: 800; color: #e8e4de; letter-spacing: -3px; line-height: 1; margin-bottom: 10px; }
.empty-sub { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #c4bdb5; letter-spacing: 1.5px; text-transform: uppercase; }

/* TRACE */
.trace-card { background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 3px solid #22c55e; border-radius: 4px; padding: 10px 14px; font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #15803d; margin: 6px 0; }
.streamlit-expanderHeader { background: #fafaf9 !important; border: 1px solid #e8e4de !important; border-left: 3px solid #22c55e !important; color: #78716c !important; font-family: 'DM Mono', monospace !important; font-size: 0.68rem !important; }

/* CHAT INPUT — UPDATED ONLY as per your requirement:
   - red outline for input
   - red outline for button
   - custom send icon (no emoji)
*/
.stChatInput { background: #f0ede8 !important; padding: 12px 32px !important; border-top: 1px solid #ddd8d0 !important; }

.stChatInput textarea {
    background: #fff !important;
    border: 2px solid #ef4444 !important;  /* red outline */
    border-radius: 6px !important;
    color: #1c1917 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
}
.stChatInput textarea:focus {
    border-color: #ef4444 !important;
    box-shadow: none !important;
    outline: none !important;
}

/* black send button + red outline */
.stChatInput button {
    background: #1c1917 !important;
    border-radius: 6px !important;
    border: 2px solid #ef4444 !important; /* red outline */
    position: relative !important;
}

/* hide Streamlit default send icon */
.stChatInput button svg { display: none !important; }

/* NEW send icon: minimal arrow triangle (no emoji) */
.stChatInput button::before {
    content: "" !important;
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    border-top: 8px solid transparent !important;
    border-bottom: 8px solid transparent !important;
    border-left: 14px solid #ffffff !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-40%, -50%) !important;
}

.stChatInput button:hover { background: #2c2825 !important; }

hr { border-color: #2c2825 !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "traces" not in st.session_state:
    st.session_state.traces = []  # list of lists: one list of trace-dicts per assistant reply


def submit_query(query: str):
    """Run agent and store message + traces atomically."""
    st.session_state.messages.append({"role": "user", "content": query})
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]
    try:
        response_text, trace_list = run_agent(query, history)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        # trace_list is already a list of trace dicts from agent.py
        st.session_state.traces.append(trace_list if trace_list else [])
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})
        st.session_state.traces.append([])


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo"><span class="sb-logo-dot"></span> BI Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-tagline">monday.com intelligence</div>', unsafe_allow_html=True)

    missing = validate_config()
    if missing:
        st.error(f"⚠️ Missing: {', '.join(missing)}")
    else:
        st.markdown('<div class="sb-section">Live Sources</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-source"><span class="source-dot"></span> Work Orders Board</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-source"><span class="source-dot"></span> Deals Board</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Quick Queries</div>', unsafe_allow_html=True)
    queries = [
        "📈 Overall pipeline summary",
        "💰 Revenue & billing analysis",
        "⛏️ Mining sector performance",
        "☀️ Renewables sector analysis",
        "🤝 Open deals overview",
        "📋 Work orders in progress",
        "💳 Collection rate analysis",
        "🏆 Top performing sectors",
    ]
    for q in queries:
        if st.button(q, key=f"sq_{q}", use_container_width=True):
            with st.spinner("Fetching live data..."):
                submit_query(q)
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.messages = []
        st.session_state.traces = []
        st.rerun()

# ── TOP BAR ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div class="top-bar-left">Business Intelligence Platform</div>
    <div class="top-bar-right">
        <span class="top-bar-item">monday.com</span>
        <span class="top-bar-item">·</span>
        <span class="top-bar-item">Groq AI</span>
        <span class="top-bar-item">·</span>
        <span class="top-bar-live"><span class="live-dot"></span> Live</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Ask your data <span>anything.</span></div>
    <div class="hero-desc">Live business intelligence · monday.com · No caching · Every query is fresh</div>
</div>
""", unsafe_allow_html=True)

# ── CHAT MESSAGES ─────────────────────────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-big">READY.</div>
        <div class="empty-sub">type below · press enter · get live insights</div>
    </div>
    """, unsafe_allow_html=True)

# Build parallel lists: one entry per assistant reply
trace_idx = 0
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-user-label">You</div>'
            f'<div class="msg-user">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="msg-agent-label">● BI Agent</div>'
            f'<div class="msg-agent">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
        # Show trace for this assistant reply
        if trace_idx < len(st.session_state.traces):
            trace_list = st.session_state.traces[trace_idx]
            if trace_list:
                with st.expander(f"🔬 {len(trace_list)} live API call(s)"):
                    for trace in trace_list:
                        params_str = (
                            ", ".join(f"{k}={v}" for k, v in trace.get("params", {}).items() if v)
                            or "no filters"
                        )
                        error_html = (
                            f'<br><span style="color:#ef4444;">⚠ {trace["error"]}</span>'
                            if trace.get("error") else ""
                        )
                        st.markdown(f"""
                        <div class="trace-card">
                            <span style="font-weight:600;">▶ {trace.get('tool','unknown')}</span>({params_str})<br>
                            board    : {trace.get('board','N/A')}<br>
                            returned : {trace.get('records_returned',0)} records{error_html}
                        </div>
                        """, unsafe_allow_html=True)
        trace_idx += 1

st.markdown('</div>', unsafe_allow_html=True)

# ── CHAT INPUT ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask a business question...")
if user_input and user_input.strip():
    with st.spinner("⚡ Fetching live data from monday.com..."):
        submit_query(user_input)
    st.rerun()