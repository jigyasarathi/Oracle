from google.adk.agents import LlmAgent

from oracle.config import get_settings
from oracle.observability import CALLBACKS
from oracle.tools.retrieval import search_documents

DOC_INSTRUCTION = """You are the document specialist for ORACLE.
You answer questions about company policies and data definitions using ONLY text returned by search_documents.

Process:
1. Call search_documents with a focused query. Try a second, differently worded query if the first finds nothing useful.
2. Answer using only the retrieved passages.
3. Cite every claim with its source in square brackets, for example [returns_policy.md#0].
4. If the passages do not answer the question, say "Not found in the documents." Do not guess.
"""

doc_agent = LlmAgent(
    name="doc_agent",
    model=get_settings().model,
    description="Answers questions about policies and definitions by retrieving and citing company documents.",
    instruction=DOC_INSTRUCTION,
    tools=[search_documents],
    **CALLBACKS,
)
