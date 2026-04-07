"""
models.py
---------
Pydantic schema for the structured news article output.
"""

from pydantic import BaseModel, Field
from typing import List
import json


class NewsArticle(BaseModel):
    """Structured representation of a generated news article."""

    headline: str = Field(
        ...,
        description="A concise, attention-grabbing headline for the article.",
    )
    lead_paragraph: str = Field(
        ...,
        description=(
            "The opening paragraph (lede) summarising the who, what, when, "
            "where, why, and how of the story."
        ),
    )
    body: List[str] = Field(
        ...,
        description=(
            "A list of body paragraphs expanding on the story with details, "
            "quotes, and context. Minimum 3 paragraphs."
        ),
    )
    sources: List[str] = Field(
        ...,
        description="A list of URLs used as sources for this article.",
    )


def article_json_schema() -> str:
    """Return the JSON schema of NewsArticle as a formatted string."""
    return json.dumps(NewsArticle.model_json_schema(), indent=2)
