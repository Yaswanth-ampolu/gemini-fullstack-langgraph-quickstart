import React from 'react';
import { useMcp } from '../contexts/McpContext'; // Adjust path as necessary
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input'; // Added for dynamic form
import { Checkbox } from '@/components/ui/checkbox'; // Added for dynamic form
import { McpServerInfo } from '../lib/types';

export const McpServerSelector: React.FC = () => {
  const {
    mcpServers,
    selectedMcpServer,
    mcpServerConfig, // Added to get current config values
    isLoading,
    selectServer,
    updateServerConfigValue, // Added to update config
  } = useMcp();

  const handleSelectionChange = (value: string) => {
    const server = mcpServers.find(s => s.qualified_name === value) || null;
    selectServer(server);
  };

  if (isLoading && mcpServers.length === 0) {
    return <p>Loading MCP Servers...</p>;
  }

  if (!isLoading && mcpServers.length === 0) {
    return <p>No MCP Servers available or failed to load.</p>;
  }

  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="mcp-server-select">Select MCP Server:</Label>
        <Select
          value={selectedMcpServer?.qualified_name || ''}
          onValueChange={handleSelectionChange}
        >
          <SelectTrigger id="mcp-server-select" className="w-full">
            <SelectValue placeholder="Choose an MCP Server" />
          </SelectTrigger>
          <SelectContent>
            {mcpServers.map((server: McpServerInfo) => (
              <SelectItem key={server.qualified_name} value={server.qualified_name}>
                {server.display_name} ({server.qualified_name})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedMcpServer && (
        <div className="mt-4 p-4 border rounded-md bg-gray-50 dark:bg-gray-800">
          <h3 className="text-lg font-semibold">{selectedMcpServer.display_name}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
            {selectedMcpServer.description}
          </p>
          <div className="mt-3">
            <h4 className="text-md font-medium">Available Tools:</h4>
            {selectedMcpServer.tools.length > 0 ? (
              <ul className="list-disc list-inside text-sm ml-4 mt-1">
                {selectedMcpServer.tools.map(tool => (
                  <li key={tool}>{tool}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">No tools listed for this server.</p>
            )}
          </div>
          {/* Placeholder for future dynamic form based on config_schema */}
          {selectedMcpServer.config_schema && selectedMcpServer.config_schema.properties && (
            <div className="mt-6">
              <h4 className="text-md font-medium mb-2">Configure Server:</h4>
              <div className="space-y-3">
                {Object.entries(selectedMcpServer.config_schema.properties).map(([key, schema]: [string, any]) => {
                  const fieldLabel = schema.title || key;
                  const currentValue = mcpServerConfig[key] ?? schema.default ?? '';

                  return (
                    <div key={key} className="flex flex-col space-y-1">
                      <Label htmlFor={`config-${key}`}>{fieldLabel}:</Label>
                      {schema.type === 'string' && (
                        <Input
                          id={`config-${key}`}
                          type="text"
                          value={currentValue}
                          onChange={(e) => updateServerConfigValue(key, e.target.value)}
                          placeholder={schema.description || ''}
                        />
                      )}
                      {schema.type === 'number' && (
                        <Input
                          id={`config-${key}`}
                          type="number"
                          value={currentValue}
                          onChange={(e) => updateServerConfigValue(key, parseFloat(e.target.value) || 0)}
                          placeholder={schema.description || ''}
                        />
                      )}
                      {schema.type === 'boolean' && (
                        <div className="flex items-center space-x-2">
                           <Checkbox
                            id={`config-${key}`}
                            checked={!!currentValue}
                            onCheckedChange={(checked: boolean) => updateServerConfigValue(key, !!checked)}
                          />
                          <Label htmlFor={`config-${key}`} className="font-normal">
                            {schema.description || fieldLabel}
                          </Label>
                        </div>
                      )}
                      {/* Add more types as needed e.g. 'integer', 'array', 'object' (more complex) */}
                      {!['string', 'number', 'boolean'].includes(schema.type) && (
                        <p className="text-xs text-red-500">Unsupported schema type: {schema.type}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
