"""
agent.py
--------
Core ReAct (Reason + Act) agent loop.

NewsAgent.generate(topic) drives a local llama3.1 model via the Ollama
Python SDK.  When the model requests a tool call the agent executes the
corresponding function from tools.py, appends the result to the message
history, and continues looping until the model emits a final JSON answer
that is parsed into a NewsArticle.
"""

import json
import re
import logging
from typing import Generator

import ollama

from models import NewsArticle, article_json_schema
from tools import TOOLS_SCHEMA, TOOL_REGISTRY

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL = "llama3.1"
MAX_ITERATIONS = 10  # safety cap to avoid infinite loops

SYSTEM_PROMPT = f"""You are an elite investigative journalist with decades of \
experience writing for world-class publications.

Your task is to research and write a high-quality, factually grounded news \
article on the topic provided by the user.

## Your workflow
1. Carefully analyse the topic.
2. Use the `search_web` tool to retrieve recent, relevant information. \
   You MUST call the tool at least once — do not rely solely on training data.
3. Read the search snippets carefully and identify key facts, dates, figures, \
   and sources.
4. Write a comprehensive news article using ONLY the information you found.

## Output format (CRITICAL)
When you are ready to deliver the final article you MUST respond with a \
**single, raw JSON object** — no markdown fences, no extra text — that \
strictly matches this schema:

{article_json_schema()}

Rules:
- `headline`:      One compelling sentence.
- `lead_paragraph`: Covers the 5 Ws in 2-3 sentences.
- `body`:          A JSON array of at least 3 strings (paragraphs).
- `sources`:       A JSON array of the URL strings you found during search.

Do NOT wrap the JSON in ```json blocks.  Output ONLY the raw JSON object.
"""


# ---------------------------------------------------------------------------
# Helper — extract the first JSON object from a string
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    """
    Attempt to extract a JSON object from the model's response text.
    Tries three strategies in order of preference:
      1. Direct parse (model returned clean JSON).
      2. Extract from ```json ... ``` fences.
      3. Regex hunt for the first {...} block.
    """
    text = text.strip()

    # Strategy 1 — direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2 — strip markdown fences
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3 — find first balanced brace block
    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"Could not extract JSON from model response:\n{text[:500]}")


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class NewsAgent:
    """
    Single-agent ReAct loop that generates a structured NewsArticle.
    """

    def __init__(self, model: str = MODEL) -> None:
        self.model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, topic: str) -> NewsArticle:
        """
        Run the ReAct loop for the given topic and return a NewsArticle.

        Args:
            topic: The news topic to research and write about.

        Returns:
            A validated NewsArticle Pydantic model instance.

        Raises:
            RuntimeError: If the agent exceeds MAX_ITERATIONS or fails to
                          produce a valid article.
        """
        messages = self._build_initial_messages(topic)
        iteration = 0

        while iteration < MAX_ITERATIONS:
            iteration += 1
            logger.info("ReAct iteration %d", iteration)

            response = ollama.chat(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
            )

            msg = response.message

            # ---- Tool call branch ----------------------------------------
            if msg.tool_calls:
                # Append the assistant's tool-calling message
                messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": msg.tool_calls})

                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments  # dict

                    logger.info("Tool call → %s(%s)", tool_name, tool_args)

                    if tool_name not in TOOL_REGISTRY:
                        tool_result = f"Error: unknown tool '{tool_name}'"
                    else:
                        try:
                            tool_result = TOOL_REGISTRY[tool_name](**tool_args)
                        except Exception as exc:  # noqa: BLE001
                            tool_result = f"Tool execution error: {exc}"

                    logger.info("Tool result (first 300 chars): %s", str(tool_result)[:300])

                    messages.append(
                        {
                            "role": "tool",
                            "content": tool_result,
                        }
                    )
                # Loop back so the model can process the tool result
                continue

            # ---- Final answer branch -------------------------------------
            content = msg.content or ""
            if not content.strip():
                logger.warning("Empty response from model at iteration %d", iteration)
                continue

            try:
                raw = _extract_json(content)
                article = NewsArticle(**raw)
                logger.info("Article parsed successfully after %d iteration(s)", iteration)
                return article
            except Exception as exc:
                # Model returned text but not yet the final JSON — feed it back
                logger.warning("Could not parse article (iter %d): %s", iteration, exc)
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous response could not be parsed as a valid "
                            "NewsArticle JSON.  Please try again and respond with ONLY "
                            "the raw JSON object matching the schema — no markdown, "
                            "no explanation."
                        ),
                    }
                )
                continue

        raise RuntimeError(
            f"Agent did not produce a valid article within {MAX_ITERATIONS} iterations."
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_initial_messages(self, topic: str) -> list:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Please research and write a comprehensive news article "
                    f"about the following topic:\n\n**{topic}**"
                ),
            },
        ]
