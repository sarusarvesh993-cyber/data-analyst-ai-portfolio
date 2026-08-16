"""
Free, key-optional AI insight layer for the portfolio.

generate_insights(metrics) -> natural-language stakeholder brief.

- If HF_TOKEN is set in the environment, it calls a FREE HuggingFace
  inference model to write the brief live.
- Otherwise (default) it returns a metric-driven narrative authored in
  _template(). This keeps every project runnable with ZERO cost and no
  external dependency, so nothing breaks in interviews or deployment.
"""
import os
import textwrap


def _hf_generate(prompt: str, token: str, model: str = "HuggingFaceH4/zephyr-7b-beta") -> str | None:
    try:
        import requests
        url = f"https://api-inference.huggingface.co/models/{model}"
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json={"inputs": prompt, "parameters": {"max_new_tokens": 350}},
            timeout=30,
        )
        if resp.status_code == 200:
            out = resp.json()
            if isinstance(out, list) and out:
                return out[0].get("generated_text", "")
            return str(out)
    except Exception:
        return None
    return None


def _template(metrics: dict) -> str:
    drivers = metrics.get("drivers", [])
    lines = [
        "## What the data says",
        metrics.get("headline", "The model finds a clear, actionable signal in the data."),
        "",
        "## Top drivers",
    ]
    if drivers:
        lines += [f"- {d}" for d in drivers]
    else:
        lines.append("- (see model importance)")
    lines += [
        "",
        "## Recommended action",
        metrics.get("recommendation", "Use the model score to prioritize the highest-risk / highest-value actions first."),
        "",
        "## Why this matters",
        "This turns raw records into a ranked, decision-ready brief — exactly the loop a data analyst owns: "
        "question -> data -> model -> plain-English recommendation.",
    ]
    return "\n".join(lines)


def generate_insights(metrics: dict, use_llm: bool = True) -> str:
    """Return a natural-language insight brief from a metrics dict."""
    narrative = _template(metrics)
    if use_llm and os.getenv("HF_TOKEN"):
        prompt = (
            "You are a senior data analyst. Write a concise, business-friendly insight summary "
            f"(under 150 words) for a portfolio project. Facts: {metrics}. Be specific and avoid fluff."
        )
        llm = _hf_generate(prompt, os.getenv("HF_TOKEN"))
        if llm:
            return llm.strip()
    return narrative
