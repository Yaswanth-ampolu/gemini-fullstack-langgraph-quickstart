import os

from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig

from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    reflection_instructions,
    answer_instructions,
    generic_web_search_instructions,
)
from agent.models import get_llm
from agent.web_search import perform_web_search_with_llm
from agent.utils import (
    get_research_topic,
)

load_dotenv()


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph node that generates a search queries based on the User's question.

    Uses the configured LLM to create optimized search queries for web research based on
    the User's question. Supports both Gemini and Ollama providers.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated query
    """
    configurable = Configuration.from_runnable_config(config)

    # Get provider and model from state or config
    provider = state.get("provider") or configurable.provider
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    # init LLM with the specified provider
    llm = get_llm(
        model_name=reasoning_model,
        provider=provider,
        temperature=1.0,
        max_retries=2,
    )
    structured_llm = llm.with_structured_output(SearchQueryList)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    # Generate the search queries
    result = structured_llm.invoke(formatted_prompt)
    return {"query_list": result.query}


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


async def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph node that performs web research using DuckDuckGo search.

    Uses free DuckDuckGo search for all providers - no API keys required!
    This provides consistent search experience across Gemini and Ollama.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including sources_gathered, search_query, and web_research_result
    """
    configurable = Configuration.from_runnable_config(config)
    provider = state.get("provider") or configurable.provider
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    print(f"🔍 Using DuckDuckGo search for: {state['search_query']}")

    # Get the appropriate LLM for web research processing
    llm = get_llm(
        model_name=reasoning_model,
        provider=provider,
        temperature=0,
        max_retries=2,
    )

    # Perform web search with DuckDuckGo
    search_results = await perform_web_search_with_llm(
        search_query=state["search_query"],
        llm=llm,
        search_prompt_template=generic_web_search_instructions,
        max_results=5
    )

    return {
        "sources_gathered": search_results["sources_gathered"],
        "search_query": [search_results["search_query"]],
        "web_research_result": [search_results["web_research_result"]],
    }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count and get the reasoning model
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    provider = state.get("provider") or configurable.provider
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # Check if we're done with research
    if state["research_loop_count"] >= configurable.max_research_loops:
        return {"is_sufficient": True, "follow_up_queries": []}

    # Get reflection model
    reflection_llm = get_llm(
        model_name=reasoning_model,
        provider=provider,
        temperature=0.3,
        max_retries=2,
    )
    
    structured_reflection_llm = reflection_llm.with_structured_output(Reflection)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        current_summary="\n".join(state["web_research_result"]),
    )
    # Generate the reflection
    reflection_result = structured_reflection_llm.invoke(formatted_prompt)
    return reflection_result.model_dump()


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph node that evaluates if more research is needed.

    Based on the reflection output, determines whether to continue research
    or finalize the answer.

    Args:
        state: Current graph state containing reflection results
        config: Configuration for the runnable

    Returns:
        Dictionary with state update, potentially including additional search queries
    """
    print(f"🤔 Research sufficient: {state['is_sufficient']}")

    if state["is_sufficient"]:
        # Sufficient research, move to finalize_answer
        return {"is_sufficient": True}
    else:
        # Continue research with follow-up queries
        print(f"🔄 Continuing research with: {state['follow_up_queries']}")
        return {
            "is_sufficient": False,
            "query_list": state["follow_up_queries"],
        }


def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph node that creates the final answer from research.

    Synthesizes all gathered information into a comprehensive final answer
    using the configured LLM provider.

    Args:
        state: Current graph state containing all research results
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including the final answer message
    """
    configurable = Configuration.from_runnable_config(config)
    provider = state.get("provider") or configurable.provider
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # Get answer model
    answer_llm = get_llm(
        model_name=reasoning_model,
        provider=provider,
        temperature=0.3,
        max_retries=2,
    )

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        current_summary="\n".join(state["web_research_result"]),
    )

    # Generate the final answer
    final_answer = answer_llm.invoke(formatted_prompt)
    return {
        "messages": [AIMessage(content=final_answer.content)],
    }


# Create the agent graph
def create_agent() -> StateGraph:
    """Create and return the configured agent graph."""
    # Create the graph
    workflow = StateGraph(OverallState)

    # Add nodes
    workflow.add_node("generate_query", generate_query)
    workflow.add_node("web_research", web_research)
    workflow.add_node("reflection", reflection)
    workflow.add_node("evaluate_research", evaluate_research)
    workflow.add_node("finalize_answer", finalize_answer)

    # Add edges
    workflow.add_edge(START, "generate_query")
    workflow.add_conditional_edges(
        "generate_query",
        continue_to_web_research,
        ["web_research"],
    )
    workflow.add_edge("web_research", "reflection")
    workflow.add_edge("reflection", "evaluate_research")
    workflow.add_conditional_edges(
        "evaluate_research",
        lambda state: "finalize_answer" if state["is_sufficient"] else "generate_query",
        ["generate_query", "finalize_answer"],
    )
    workflow.add_edge("finalize_answer", END)

    return workflow.compile()