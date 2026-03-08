"""
Streamlit deployment of the RAG backend.
Run from repo root: streamlit run streamlit_app.py
Deploy on Streamlit Cloud: connect this repo and set Main file path to streamlit_app.py.
"""
import sys
import os

# Run from repo root so Phase_3 and Phase_2 paths resolve
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import streamlit as st

# Lazy-load RAG to avoid slow startup on Streamlit Cloud
@st.cache_resource
def get_rag_agent():
    from Phase_3_Query_Generation.rag_agent import MutualFundRAG
    return MutualFundRAG()

st.set_page_config(
    page_title="MF Genie — HDFC Mutual Fund AI",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("🏦 Mutual Fund Genie — HDFC Mutual Fund AI Assistant")
st.caption("Facts-only. No investment advice. Answers use Backend API (RAG) with citations.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Suggested questions
SUGGESTED = [
    "What is the exit load for HDFC Flexi Cap?",
    "What is a mutual fund?",
    "What is the AUM of the HDFC Liquid Fund?",
]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📎 Sources"):
                for src in msg["sources"]:
                    st.markdown(f"- [{src}]({src})")

# Suggested question buttons
st.markdown("**Suggested questions:**")
cols = st.columns(min(3, len(SUGGESTED)))
for i, q in enumerate(SUGGESTED):
    if cols[i % len(cols)].button(q[:40] + "…" if len(q) > 40 else q, key=f"faq_{i}"):
        st.session_state.user_query = q
        st.rerun()

# Chat input
if prompt := (st.session_state.pop("user_query", None) or st.chat_input("Ask about HDFC Mutual Fund schemes…")):
    if not prompt.strip():
        st.warning("Please enter a question.")
        st.stop()

    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt.strip(), "sources": None})

    # Generate response using Backend (RAG agent)
    with st.chat_message("assistant"):
        try:
            rag = get_rag_agent()
            answer, sources = rag.generate_answer(prompt.strip())
            st.markdown(answer)
            if sources:
                with st.expander("📎 Sources"):
                    for src in sources:
                        st.markdown(f"- [{src}]({src})")
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources or [],
            })
        except Exception as e:
            err_msg = str(e) or "Server error. Please try again."
            st.error("⚠️ " + err_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": err_msg,
                "sources": None,
            })

st.divider()
st.caption("For educational purposes only. Not SEBI-registered. No financial advice.")
