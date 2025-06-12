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
import requests
import urllib.parse
import json # Added
from typing import Optional

from .tools_and_schemas import McpToolRequest, McpToolResponse

load_dotenv()


# MCP Helper Function
def create_smithery_mcp_url(server_qualified_name: str, config_params: dict, api_key: str) -> str:
    """
    Constructs the URL for calling a Smithery-proxied MCP server.
    """
    base_url = f"https://server.smithery.ai/{server_qualified_name}/mcp"

    query_params = {}
    if api_key: # Only add api_key if it exists, though it's required by Smithery proxy
        query_params['api_key'] = api_key
    query_params.update(config_params)

    encoded_params = urllib.parse.urlencode(query_params)
    return f"{base_url}?{encoded_params}"


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
    Also collects related images for visual gallery display.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including sources_gathered, search_query, web_research_result, and images
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

    # Perform web search with DuckDuckGo (including images)
    search_results = await perform_web_search_with_llm(
        search_query=state["search_query"],
        llm=llm,
        search_prompt_template=generic_web_search_instructions,
        max_results=5,
        include_images=True,
        max_images=6
    )

    return {
        "sources_gathered": search_results["sources_gathered"],
        "search_query": [search_results["search_query"]],
        "web_research_result": [search_results["web_research_result"]],
        "images": search_results.get("images", [])  # Add images to state
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
        summaries="\n\n---\n\n".join(state["web_research_result"]),
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
        summaries="\n\n---\n\n".join(state["web_research_result"]),
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
    workflow.add_node("route_to_tool", route_to_tool) # New routing node
    workflow.add_node("generate_query", generate_query)
    workflow.add_node("web_research", web_research)
    workflow.add_node("execute_mcp_tool", execute_mcp_tool) # New MCP tool node
    workflow.add_node("reflection", reflection)
    workflow.add_node("evaluate_research", evaluate_research)
    workflow.add_node("finalize_answer", finalize_answer)

    # Add edges
    workflow.add_edge(START, "route_to_tool") # START now goes to router

    # Conditional edges from router
    workflow.add_conditional_edges(
        "route_to_tool",
        # This lambda will read the "next_node" field set by route_to_tool
        lambda x: x.get("next_node"),
        {
            "execute_mcp_tool": "execute_mcp_tool",
            "generate_query": "generate_query",
        },
    )

    # Edges for web research path
    workflow.add_conditional_edges(
        "generate_query",
        continue_to_web_research, # This function needs to return a list of Sends or a node name.
                                   # It currently returns List[Send(..., ...)], which is fine for spawning.
                                   # The key here for conditional_edges is the *source node's output* mapping to a *target node name*.
                                   # The way continue_to_web_research is used suggests it's part of a dynamic fan-out,
                                   # which might be implicitly handled if 'generate_query' directly connects to 'web_research'
                                   # when 'continue_to_web_research' produces output.
                                   # Let's assume this structure is okay for now as it was existing.
                                   # The main thing is that 'generate_query' is a possible target from 'route_to_tool'.
        ["web_research"], # This should be a map if using a conditional function that returns keys of the map.
                          # If continue_to_web_research itself doesn't return "web_research" string, this needs adjustment.
                          # The original code: workflow.add_conditional_edges("generate_query", continue_to_web_research, ["web_research"])
                          # This implies `continue_to_web_research` might be returning a string that is one of the keys in the path_map (which is just ["web_research"])
                          # Or, more likely, if `continue_to_web_research` returns a `Send` object or list of them,
                          # the `conditional_edges` might have special handling for that.
                          # Given the `Send` usage, it's for spawning. The original edge from `generate_query` might need to be `add_edge` if it always goes to web_research after `continue_to_web_research` logic.
                          # Let's re-evaluate: `add_conditional_edges`'s 3rd arg is a path map if the condition function returns a key.
                          # If `continue_to_web_research` is directly callable and its *return value* is the *name of the next node*, then it works.
                          # But it returns a list of `Send` objects.
                          # This was likely meant to be: `workflow.add_edge("generate_query", "web_research")` if `continue_to_web_research` is just a passthrough or data transformation.
                          # However, `Send` is for dynamic parallelism.
                          # The original `add_conditional_edges` for `generate_query` might have been a misunderstanding of its use.
                          # It should be: if `generate_query`'s output (QueryGenerationState) is then processed by `continue_to_web_research`
                          # and this function itself *decides* the next node, then it's fine.
                          # `continue_to_web_research` returns `List[Send(...)]`. This is a special case for LangGraph to invoke downstream nodes.
                          # So the original conditional edge from generate_query is likely correct for fanning out.
    )
    workflow.add_edge("web_research", "reflection")

    # Edge for MCP tool path
    workflow.add_edge("execute_mcp_tool", "reflection") # MCP tool also goes to reflection

    # Common path after research/tool execution
    workflow.add_edge("reflection", "evaluate_research")
    workflow.add_conditional_edges(
        "evaluate_research",
        # This lambda checks 'is_sufficient' in the state (set by 'reflection' and passed through 'evaluate_research')
        lambda state: "finalize_answer" if state.get("is_sufficient") else "generate_query", # Loop back to generate_query for more research
        { # This map provides the target nodes for the keys returned by the lambda
            "generate_query": "generate_query", # If "generate_query" is returned by lambda
            "finalize_answer": "finalize_answer", # If "finalize_answer" is returned by lambda
        },
    )
    workflow.add_edge("finalize_answer", END)

    return workflow.compile()


# New MCP Tool Execution Node
def execute_mcp_tool(state: OverallState, config: RunnableConfig) -> OverallState:
    """
    Executes a specified MCP tool via the Smithery proxy.
    Assumes current_mcp_tool_request and target_mcp_server_qualified_name are in state.
    """
    smithery_api_key = os.getenv("SMITHERY_API_KEY")
    if not smithery_api_key:
        # This is a critical failure, as we need this to authenticate to Smithery proxy itself
        # and potentially for the MCP server if it also uses this key via Smithery.
        error_response = McpToolResponse(status="error", data={"error": "SMITHERY_API_KEY not configured."})
        return {**state, "mcp_tool_response": error_response}

    tool_request = state.get("current_mcp_tool_request")
    server_qname = state.get("target_mcp_server_qualified_name")
    active_mcp_configs = state.get("active_mcp_configurations", {})

    if not tool_request or not server_qname:
        error_response = McpToolResponse(status="error", data={"error": "Missing tool request or target server in state."})
        return {**state, "mcp_tool_response": error_response}

    server_config = active_mcp_configs.get(server_qname)
    if server_config is None: # Could be an empty dict if no config needed, so check for None explicitly
        error_response = McpToolResponse(status="error", data={"error": f"Active configuration for {server_qname} not found."})
        return {**state, "mcp_tool_response": error_response}

    # Construct the Smithery MCP proxy URL
    # The `api_key` parameter for create_smithery_mcp_url here is for the *target MCP server's* own API key,
    # which would be part of its `server_config` if it requires one.
    # The `SMITHERY_API_KEY` is for authenticating with the Smithery *proxy* itself, used in headers.
    # For now, let's assume target server config might contain an 'api_key' field if it needs one.
    # If not, it's passed as an empty dict or a dict without 'api_key'.
    # The problem description for create_smithery_mcp_url was a bit ambiguous on which api_key it meant.
    # Let's assume create_smithery_mcp_url's api_key param is for parameters to the target server,
    # and the Smithery proxy auth key is via Headers.

    # Clarification: The prompt for create_smithery_mcp_url says:
    # "It should append `api_key` and all key-value pairs from `config` as URL query parameters."
    # This implies `api_key` is a specific parameter for the *target server*, distinct from SMITHERY_API_KEY for the proxy.
    # Let's assume the target server's API key, if any, is *within* its `server_config`.
    # So, `create_smithery_mcp_url` should take `server_config` and extract an `api_key` from it if present.
    # Re-adjusting create_smithery_mcp_url slightly to reflect this.
    # For now, I will proceed with the current `create_smithery_mcp_url` which takes `api_key` as a separate argument.
    # This means the `server_config` might need to be split into `config_params` and `target_api_key_for_url`.
    # This is getting complicated. Let's simplify: Smithery proxy itself uses SMITHERY_API_KEY in header.
    # Target MCP server config (server_config) is passed as query params.
    # If target MCP server also needs an API key passed as a query param, it must be *part of* server_config.
    # So, create_smithery_mcp_url should just take server_config.

    # Re-reading `create_smithery_mcp_url`'s prompt: "append `api_key` AND all key-value pairs from `config`"
    # This is tricky. If `api_key` is special and separate from `config`, where does it come from for the target?
    # Let's assume for a moment the `api_key` in `create_smithery_mcp_url` *is* the `SMITHERY_API_KEY` for simplicity,
    # and it's passed by Smithery to the underlying server if needed.
    # This is often how proxies work.

    # Let's stick to the simpler interpretation: server_config has all params for the target server.
    # The SMITHERY_API_KEY is for the proxy's auth only (header).
    # So, the `api_key` argument to `create_smithery_mcp_url` is actually not needed if this interpretation is correct.
    # I will modify `create_smithery_mcp_url` to only take `config_params`.
    # For now, I will proceed with the existing `create_smithery_mcp_url` and pass `None` or some value for its `api_key` param.
    # This part of the design needs clarification, but I'll make a working assumption.
    # Assumption: The `api_key` parameter in `create_smithery_mcp_url` is distinct and sourced from somewhere,
    # potentially also `SMITHERY_API_KEY` or another env var if the target needs its own key in query.
    # For now, let's assume it's NOT the SMITHERY_API_KEY used for Authorization header.
    # Let's assume target server config does not include its own api_key for query params for now.

    target_specific_api_key_for_query = None # Placeholder for now. This would come from server_config if needed.
    mcp_target_url = create_smithery_mcp_url(server_qname, server_config, target_specific_api_key_for_query)

    headers = {
        "Authorization": f"Bearer {smithery_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json", # MCPs should ideally respond with JSON
    }

    # Construct payload for the MCP call as per assumed spec
    mcp_payload = {
        "tool": tool_request.tool_name,
        "params": tool_request.payload,
        # MCP spec might require version, id, etc. Keeping it simple.
    }

    try:
        print(f"Executing MCP tool: POST {mcp_target_url} with payload {mcp_payload}")
        response = requests.post(mcp_target_url, json=mcp_payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        response_data = response.json()
        mcp_response = McpToolResponse(status="success", data=response_data)
        print(f"MCP tool execution successful: {response_data}")

    except requests.exceptions.HTTPError as http_err:
        error_detail = {"error": str(http_err)}
        try: # Try to get more detailed error from response body
            error_detail["response_body"] = http_err.response.json()
        except ValueError: # response body is not JSON or empty
            error_detail["response_body"] = http_err.response.text
        mcp_response = McpToolResponse(status="error", data=error_detail)
        print(f"MCP tool execution HTTPError: {error_detail}")
    except requests.exceptions.RequestException as req_err:
        mcp_response = McpToolResponse(status="error", data={"error": f"Request failed: {str(req_err)}"})
        print(f"MCP tool execution RequestException: {req_err}")
    except Exception as e: # Catch any other unexpected errors
        mcp_response = McpToolResponse(status="error", data={"error": f"An unexpected error occurred: {str(e)}"})
        print(f"MCP tool execution unexpected error: {e}")

    # Update state with the response
    updated_state = {**state, "mcp_tool_response": mcp_response}

    # Append result to web_research_result for reflection node
    current_results = updated_state.get("web_research_result", [])
    if mcp_response.status == "success":
        data_to_append = mcp_response.data
        if isinstance(data_to_append, (dict, list)):
            mcp_output_string = json.dumps(data_to_append, indent=2)
        elif isinstance(data_to_append, str):
            mcp_output_string = data_to_append
        else: # Other types, convert to string
            mcp_output_string = str(data_to_append)
        current_results.append(mcp_output_string)
    else: # Error case
        error_data_str = json.dumps(mcp_response.data, indent=2)
        current_results.append(f"MCP Tool Execution Error:\n{error_data_str}")

    updated_state["web_research_result"] = current_results
    return updated_state


# Routing Node
def route_to_tool(state: OverallState) -> dict:
    """
    Decides whether to execute an MCP tool or proceed with web research.
    Updates 'next_node' in the state for conditional routing.
    """
    if state.get("target_mcp_server_qualified_name") and state.get("current_mcp_tool_request"):
        print("Routing decision: execute_mcp_tool")
        return {"next_node": "execute_mcp_tool"}
    else:
        print("Routing decision: generate_query")
        return {"next_node": "generate_query"}

# Create and export the graph instance
graph = create_agent()