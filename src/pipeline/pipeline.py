from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from collections.abc import Callable


def run_research_pipeline(
    topic: str,
    progress_callback: Callable[[dict], None] | None = None,
) -> dict:

    """
    Run the research pipeline for a given topic.

    Args:
        topic (str): The research topic.
    Returns:
        dict: A dictionary containing the research report and critique."""

    state = {}

    def emit(stage: str, status: str, message: str, output: str = "") -> None:
        if progress_callback:
            progress_callback({
                "stage": stage,
                "status": status,
                "message": message,
                "output": output,
            })

    # Step 1: Use the search agent to gather research
    print("\n"+" ="*50)
    print(f"step 1 - search agent is working ...")
    print("="*50)
    emit("search", "running", "Searching for recent, reliable sources")
    
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about the topic: {topic}")]
    })
    state["search_result"] = search_result['messages'][-1].content
    emit("search", "complete", "Research sources gathered", state["search_result"])

    print("\nsearch result: ", state["search_result"])

    # Step 2: Use the reader agent to gather content
    print("\n"+" ="*50)
    print(f"step 2 - reader agent is scraping top resources ...")
    print("="*50)
    emit("reader", "running", "Reading the most relevant source in depth")

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages" : [("user", 
                       f"Based on the following research results about: {topic}, "
                       f"pick the most relevant URL and scrape it for deeper content.\n\n"
                       f"Search Results:\n{state['search_result'][:800]}"
                       )]
    })

    state["scraped_content"] = reader_result['messages'][-1].content
    emit("reader", "complete", "Source content extracted", state["scraped_content"])

    print("\nscraped content: ", state["scraped_content"])

    # Step 3: Writer chain
    print("\n"+" ="*50)
    print(f"step 3 - Writer chain is drafting the report ...")
    print("="*50)
    emit("writer", "running", "Synthesizing the research into a report")

    research_combined = (
                        f"SEARCH RESULTS:\n{state['search_result']} \n\n"
                        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
                        )
    

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })
    emit("writer", "complete", "Report drafted", state["report"])

    print("\nFinal Report\n", state["report"])

    # Step 4: Critic chain
    print("\n"+" ="*50)
    print(f"step 4 - Critic chain is reviewing the report ...")
    print("="*50)
    emit("critic", "running", "Checking accuracy, structure, and clarity")

    state["feedback"] = critic_chain.invoke({
        "report" : state["report"]
        
    })
    emit("critic", "complete", "Review complete", state["feedback"])

    print("\nCritic Report\n", state["feedback"])

    return state

