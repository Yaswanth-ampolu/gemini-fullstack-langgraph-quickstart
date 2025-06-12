from typing import List
from pydantic import BaseModel, Field


class SearchQueryList(BaseModel):
    query: List[str] = Field(
        description="A list of search queries to be used for web research."
    )
    rationale: str = Field(
        description="A brief explanation of why these queries are relevant to the research topic."
    )


class Reflection(BaseModel):
    is_sufficient: bool = Field(
        description="Whether the provided summaries are sufficient to answer the user's question."
    )
    knowledge_gap: str = Field(
        description="A description of what information is missing or needs clarification."
    )
    follow_up_queries: List[str] = Field(
        description="A list of follow-up queries to address the knowledge gap."
    )


class McpServerInfo(BaseModel):
    qualified_name: str
    display_name: str
    description: str
    tools: List[str]  # names of tools offered
    config_schema: dict  # JSON schema for configuration


class McpToolRequest(BaseModel):
    tool_name: str
    payload: dict


class McpToolResponse(BaseModel):
    status: str  # e.g., "success", "error"
    data: dict | str
