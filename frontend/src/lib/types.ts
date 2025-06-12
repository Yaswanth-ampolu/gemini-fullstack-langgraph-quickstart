// Defines the structure for MCP Server Information, mirroring the backend Pydantic model.
export interface McpServerInfo {
  qualified_name: string;
  display_name: string;
  description: string;
  tools: string[]; // List of tool names offered by the server
  config_schema: Record<string, any>; // JSON schema for the server's configuration
}

// You can add other frontend-specific types here as needed.
// For example, if you had McpToolRequest or McpToolResponse types for frontend state:
// export interface McpToolRequest {
//   tool_name: string;
//   payload: Record<string, any>;
// }
// export interface McpToolResponse {
//   status: 'success' | 'error';
//   data: Record<string, any> | string;
// }
