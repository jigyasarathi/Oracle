"""ORACLE pipeline: analyst (router + specialists as tools) -> critic (self-reflection)."""
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool

from oracle.agents.doc_agent import doc_agent
from oracle.agents.sql_agent import sql_agent
from oracle.config import get_settings
from oracle.observability import CALLBACKS

_cfg = get_settings()

ANALYST_INSTRUCTION = """You are the lead analyst for ORACLE. Decide how to answer each business question:
- Numbers, counts, trends, rankings -> call the sql_agent tool.
- Policies, definitions, rules, "what does the document say" -> call the doc_agent tool.
- Questions needing both -> call both, then combine the results.
Pass each specialist a clear, self-contained question. Do not answer from your own knowledge.

Write a draft answer with these parts:
Answer: a short direct answer.
Evidence: the SQL that was run and/or the document sources cited, copied from the specialists.
"""

CRITIC_INSTRUCTION = """You are the critic for ORACLE. Review the draft answer below before it reaches the user.

Draft answer:
{draft_answer}

Check:
1. Every number is backed by SQL shown in the Evidence section.
2. Every policy claim has a document citation.
3. The draft actually answers the user's question and does not contradict itself.

Output the final answer in this format:
Answer: (fix or remove any unsupported claim)
Evidence: (SQL and/or sources)
Confidence: High, Medium or Low, plus one sentence explaining why.
"""

analyst = LlmAgent(
    name="analyst",
    model=_cfg.model,
    description="Routes questions to the SQL and document specialists and drafts an answer.",
    instruction=ANALYST_INSTRUCTION,
    tools=[AgentTool(agent=sql_agent), AgentTool(agent=doc_agent)],
    output_key="draft_answer",
    **CALLBACKS,
)

critic = LlmAgent(
    name="critic",
    model=_cfg.critic_model,
    description="Checks the draft answer for unsupported claims and assigns a confidence level.",
    instruction=CRITIC_INSTRUCTION,
    output_key="final_answer",
    **CALLBACKS,
)

root_agent = SequentialAgent(
    name="oracle",
    description="Multi-agent enterprise data analyst over BigQuery and company documents.",
    sub_agents=[analyst, critic],
)
