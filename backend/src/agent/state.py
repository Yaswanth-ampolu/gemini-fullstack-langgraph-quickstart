from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, Dict, Any, List, Optional

from langgraph.graph import add_messages
from typing_extensions import Annotated

# Removed pydantic Field import, it's not used here.
from .tools_and_schemas import McpServerInfo, McpToolRequest, McpToolResponse


import operator
from dataclasses import dataclass, field # This field is from dataclasses, not pydantic. Retained for SearchStateOutput
from typing_extensions import Annotated


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    available_mcp_servers: List[McpServerInfo]
    active_mcp_configurations: Dict[str, dict]
    current_mcp_tool_request: Optional[McpToolRequest]
    target_mcp_server_qualified_name: Optional[str]
    mcp_tool_response: Optional[McpToolResponse]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    images: Annotated[list, operator.add]  # Added for image gallery support
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str


class ReflectionState(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int


class Query(TypedDict):
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    query_list: list[Query]


class WebSearchState(TypedDict):
    search_query: str
    id: str


@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: str = field(default=None)  # Final report
