import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { McpServerInfo } from '../lib/types'; // Adjust path as necessary

interface McpContextType {
  mcpServers: McpServerInfo[];
  selectedMcpServer: McpServerInfo | null;
  mcpServerConfig: Record<string, any>;
  isLoading: boolean;
  selectServer: (server: McpServerInfo | null) => void;
  updateServerConfigValue: (key: string, value: any) => void;
  fetchServers: () => Promise<void>; // Allow manual refetch if needed
}

const McpContext = createContext<McpContextType | undefined>(undefined);

export const McpProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [mcpServers, setMcpServers] = useState<McpServerInfo[]>([]);
  const [selectedMcpServer, setSelectedMcpServer] = useState<McpServerInfo | null>(null);
  const [mcpServerConfig, setMcpServerConfig] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchServers = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/mcp/servers');
      if (!response.ok) {
        throw new Error(`Failed to fetch MCP servers: ${response.statusText}`);
      }
      const data: McpServerInfo[] = await response.json();
      setMcpServers(data);
    } catch (error) {
      console.error("Error fetching MCP servers:", error);
      setMcpServers([]); // Set to empty array on error
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
  }, []);

  const selectServer = (server: McpServerInfo | null) => {
    setSelectedMcpServer(server);
    // Reset config when server changes
    setMcpServerConfig({});
  };

  // This function will be passed as updateServerConfigValue
  const handleUpdateServerConfigValue = (key: string, value: any) => {
    setMcpServerConfig(prevConfig => ({
      ...prevConfig,
      [key]: value,
    }));
  };

  return (
    <McpContext.Provider value={{
      mcpServers,
      selectedMcpServer,
      mcpServerConfig,
      isLoading,
      selectServer,
      updateServerConfigValue: handleUpdateServerConfigValue, // Correctly named function passed
      fetchServers
    }}>
      {children}
    </McpContext.Provider>
  );
};

export const useMcp = (): McpContextType => {
  const context = useContext(McpContext);
  if (context === undefined) {
    throw new Error('useMcp must be used within an McpProvider');
  }
  return context;
};
