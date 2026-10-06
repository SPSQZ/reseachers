from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
from rich import print

# -----------------------------------------------------------------------------
# PROJECT TRACE: This file is the external I/O layer of the application.
# It translates live internet sources into a text representation the LLM can reason
# over. The tools here are intentionally simple but highly important, because the
# entire research system depends on having trustworthy information to read.
# -----------------------------------------------------------------------------

load_dotenv()

# Initialize Tavily search client using the environment key.
# In practice, this is the search engine behind the "Find sources" step.
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# -----------------------------------------------------------------------------
# TOOL TRACE: web_search(query)
# Data flow:
#   query -> Tavily API -> array of result objects -> formatted string of titles/urls/snippets
# This output is then fed into the search agent's prompt, which decides which
# source is relevant enough to scrape deeper.
# -----------------------------------------------------------------------------
@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query,max_results=5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    
    return "\n----\n".join(out)

# -----------------------------------------------------------------------------
# TOOL TRACE: scrape_url(url)
# Data flow:
#   URL -> HTTP request -> HTML -> BeautifulSoup parse -> remove junk tags
#   -> get visible text -> return cleaned article content
# This is the deep-reading phase. It takes a candidate source and converts web
# content into a manageable text blob for the final synthesis stage.
# -----------------------------------------------------------------------------
@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        # Request the page with a browser-like user-agent to reduce bot blocking.
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        # Strip non-content containers that usually add noise.
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        # Extract visible text and keep only a limited slice for model context efficiency.
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"