"""Optional, metric-controlled stakeholder-brief generator.

The quantitative workflow never depends on this module. With an HF_TOKEN, the
function attempts a Hugging Face chat-completion request. Without a token, or
if the request fails, it returns a deterministic analyst-authored template.
"""
from __future__ import annotations

import os

import requests

DEFAULT_MODEL = "google/gemma-2-2b-it"
HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"


def _get_token() -> str | None:
    """Read a local environment token or a Streamlit Community Cloud secret."""
    token = os.getenv("HF_TOKEN")
    if token:
        return token
    try:
        import streamlit as st

        return st.secrets.get("HF_TOKEN")
    except Exception:
        return None


def _hf_generate(prompt: str, token: str, model: str = DEFAULT_MODEL) -> str | None:
    """Call Hugging Face's OpenAI-compatible chat endpoint, failing closed."""
    try:
        response = requests.post(
            HF_CHAT_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={
                "model": os.getenv("HF_MODEL", model),
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a data analyst writing a concise stakeholder brief. "
                            "Use only facts supplied by the user. Do not invent results."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 260,
                "temperature": 0.2,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        return None


def _template(metrics: dict) -> str:
    """Create the predictable no-token version of the brief."""
    drivers = metrics.get("drivers", [])
    lines = [
        "## What the data says",
        metrics.get("headline", "The analysis produced a decision-relevant signal."),
        "",
        "## Factors to review",
    ]
    lines.extend(f"- {driver}" for driver in drivers)
    if not drivers:
        lines.append("- Review the project diagnostics and assumptions.")
    lines.extend(
        [
            "",
            "## Recommended action",
            metrics.get(
                "recommendation",
                "Use the result as one input to a measured pilot and monitor the outcome.",
            ),
        ]
    )
    return "\n".join(lines)


def generate_insights(metrics: dict, use_llm: bool = True) -> str:
    """Return a brief from approved metrics, with a deterministic fallback."""
    fallback = _template(metrics)
    token = _get_token() if use_llm else None
    if not token:
        return fallback

    prompt = (
        "Write a stakeholder brief under 160 words with headings for finding, "
        "business implication, recommendation, and limitation. Here are the only "
        f"approved facts and context: {metrics!r}"
    )
    generated = _hf_generate(prompt, token)
    return generated or fallback
