"""
app.py
------
Streamlit frontend for the Local AI News Generator.
Simple and crisp — no heavy styling.
"""

import streamlit as st

from agent import NewsAgent
from models import NewsArticle

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Local AI News Generator",
    page_icon="📰",
    layout="centered",
)

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.title("📰 Local AI News Generator")
st.caption("Powered by llama3.1 via Ollama · Search via DuckDuckGo · 100% local")

st.divider()

topic = st.text_input(
    label="Enter a news topic",
    placeholder="e.g. Latest developments in quantum computing",
    help="Be as specific or as broad as you like.",
)

generate_btn = st.button("Generate News", type="primary", disabled=not topic.strip())

# ---------------------------------------------------------------------------
# Generation logic
# ---------------------------------------------------------------------------

if generate_btn and topic.strip():
    with st.spinner("Local agent is researching and writing..."):
        try:
            agent = NewsAgent()
            article: NewsArticle = agent.generate(topic.strip())
        except Exception as exc:
            st.error(f"❌ Agent error: {exc}")
            st.stop()

    # -----------------------------------------------------------------------
    # Render the article
    # -----------------------------------------------------------------------

    st.divider()

    # Headline — H1
    st.markdown(f"# {article.headline}")

    # Lead paragraph — bold
    st.markdown(f"**{article.lead_paragraph}**")

    st.write("")  # spacer

    # Body paragraphs
    for paragraph in article.body:
        st.markdown(paragraph)
        st.write("")

    # Sources
    if article.sources:
        st.divider()
        st.markdown("### Sources")
        for url in article.sources:
            st.markdown(f"- {url}")
