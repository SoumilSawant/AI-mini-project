"""
tools.py
--------
Tool definitions for the ReAct agent.

search_web  — DuckDuckGo-powered web search (no API key required).
TOOLS_SCHEMA — Ollama-compatible tool definition list.
"""

from duckduckgo_search import DDGS


# ---------------------------------------------------------------------------
# Tool implementation
# ---------------------------------------------------------------------------

def search_web(query: str) -> str:
    """
    Search the web using DuckDuckGo and return the top-5 results as a
    single plain-text string containing each result's title, snippet,
    and URL.

    Args:
        query: The search query string.

    Returns:
        A concatenated string of result snippets and their source URLs.
    """
    results_text = []

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
    except Exception as exc:  # noqa: BLE001
        return f"Search failed: {exc}"

    if not results:
        return "No results found for this query."

    for i, r in enumerate(results, start=1):
        title = r.get("title", "No title")
        body = r.get("body", "No snippet available.")
        url = r.get("href", "No URL")
        results_text.append(
            f"Result {i}:\n"
            f"  Title   : {title}\n"
            f"  Snippet : {body}\n"
            f"  URL     : {url}\n"
        )

    return "\n".join(results_text)


# ---------------------------------------------------------------------------
# Ollama tool schema (OpenAI-compatible function-calling format)
# ---------------------------------------------------------------------------

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for recent information on a given topic using "
                "DuckDuckGo. Returns the top-5 result snippets and their URLs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The search query to look up. Be specific for "
                            "better results."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    }
]


# ---------------------------------------------------------------------------
# Tool dispatcher — maps tool name → callable
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict = {
    "search_web": search_web,
}
