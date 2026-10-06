from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 
from dotenv import load_dotenv 
import os

# -----------------------------------------------------------------------------
# PROJECT TRACE: agents.py is the orchestration layer for the AI reasoning flow.
# It is not the user interface and not the scraping code itself. Instead, it
# defines the LLMs, tool-enabled agents, and prompt-based chains that convert raw
# web evidence into a final report and quality review.
# -----------------------------------------------------------------------------

load_dotenv(override=True)

# Support both GEMINI_API_KEY and GOOGLE_API_KEY for compatibility;
# the app uses the Gemini model, so this is the authentication gate for all
# report generation and critique phases.
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Model setup.
# temperature=0 keeps the LLM deterministic, which is desirable for research
# synthesis and critiquing because we want grounded, consistent outputs rather
# than exploratory or speculative writing.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=api_key,
    temperature=0
)

# -----------------------------------------------------------------------------
# AGENT TRACE: build_search_agent()
# Data flow:
#   user topic -> search agent -> web_search tool -> list of sources/titles/snippets
# This agent is intentionally limited to the search capability so it stays
# focused on source discovery rather than reading/rewriting.
# -----------------------------------------------------------------------------
def build_search_agent():
    return create_agent(
        model = llm,
        tools= [web_search],
        system_prompt=(
            "You are a research search agent. Preserve the user's exact topic and "
            "search for sources that directly address it. If the topic is empty, "
            "do not search; report that the topic is missing."
        )
    )

# -----------------------------------------------------------------------------
# AGENT TRACE: build_reader_agent()
# Data flow:
#   source URLs + topic -> reader agent -> scrape_url tool -> cleaned article text
# This step converts found links into raw evidence that can be used for report
# writing. It narrows the task to extracting relevant content from a chosen page.
# -----------------------------------------------------------------------------
def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url],
        system_prompt=(
            "You are a research source reader. Extract evidence relevant to the "
            "user's exact topic. Do not replace a missing or unclear topic with a "
            "generic subject."
        )
    )


# -----------------------------------------------------------------------------
# CHAIN TRACE: writer_prompt + writer_chain
# Data flow:
#   topic + research bundle -> writer prompt -> LLM -> final report text
# This chain is responsible for turning noisy search snippets and scraped content
# into a structured, readable research document.
# -----------------------------------------------------------------------------
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Answer the exact topic directly, distinguish established facts from uncertainty, and never invent sources or claims."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

    Be detailed, factual and professional. If the gathered research does not answer the topic, say so clearly instead of substituting a different topic."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# -----------------------------------------------------------------------------
# CHAIN TRACE: critic_prompt + critic_chain
# Data flow:
#   topic + generated report -> critic prompt -> LLM -> score + strengths + flaws
# This acts as a factuality gate. It reviews whether the report truly answers the
# exact user request and whether the evidence is sufficiently relevant and honest.
# -----------------------------------------------------------------------------
critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below against the requested topic and evaluate it strictly.

Requested topic:
{topic}

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

Check especially whether the report answers the requested topic, uses relevant evidence, and avoids unsupported claims.

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()

