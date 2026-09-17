from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 
from dotenv import load_dotenv 
import os
load_dotenv(override=True)

# Support both GEMINI_API_KEY and GOOGLE_API_KEY
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Model setup 
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=api_key,
    temperature=0
)

#1st agent 
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

#2nd agent 

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


#writer chain 

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

#critic_chain 

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

