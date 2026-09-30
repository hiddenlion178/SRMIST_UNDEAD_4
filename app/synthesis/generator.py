"""Provider-neutral answer synthesis for the demo."""


async def synthesize(query: str, evidence: list[dict]) -> str:
    """Build a concise answer from retrieved evidence.

    Replace with the project's actual LLM call and prompt pipeline.
    """
    if not evidence:
        return "No supporting evidence was retrieved."

    snippets = " ".join(item.get("content", "") for item in evidence)
    return f"Answer for '{query}': {snippets}"
