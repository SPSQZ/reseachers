from agents import build_reader_agent , build_search_agent , writer_chain , critic_chain

# -----------------------------------------------------------------------------
# PROJECT TRACE: This file is the command-line execution engine for the
# research workflow. It orchestrates the stages in serial order, passing the
# current "research state" from one step to the next.
# -----------------------------------------------------------------------------


def run_research_pipeline(topic : str) -> dict:
    # Validate the topic before doing any work.
    topic = topic.strip()
    if not topic:
        raise ValueError("A non-empty research topic is required.")

    # Shared state object. Each stage stores a result in this dictionary.
    # This acts like a temporary workflow memory for the whole research run.
    state = {}

    # -------------------------------------------------------------------------
    # STEP 1: Search Agent
    # Input: topic from user
    # Output: search_results string containing titles/urls/snippets
    # -------------------------------------------------------------------------
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result['messages'][-1].content

    print("\n search result ",state['search_results'])

    # -------------------------------------------------------------------------
    # STEP 2: Reader Agent
    # Input: topic + search_results
    # Output: scraped_content from the top chosen URL
    # -------------------------------------------------------------------------
    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nscraped content: \n", state['scraped_content'])

    # -------------------------------------------------------------------------
    # STEP 3: Writer Chain
    # Input: search_results + scraped_content
    # Output: final research report
    # -------------------------------------------------------------------------
    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])

    # -------------------------------------------------------------------------
    # STEP 4: Critic Chain
    # Input: topic + generated report
    # Output: critic review / quality evaluation
    # -------------------------------------------------------------------------
    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "topic": topic,
        "report":state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    # CLI entry point. This lets us run the full pipeline in a terminal session.
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)

