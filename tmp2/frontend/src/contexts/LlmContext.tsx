import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type LlmProvider = {
  provider: string;
  models: {
    name: string;
    displayName: string;
  }[];
};

interface LlmContextType {
  effort: string;
  provider: string;
  model: string;
  llmProviders: LlmProvider[];
  updateEffort: (effort: string) => void;
  updateProvider: (provider: string) => void;
  updateModel: (model: string) => void;
  isLoading: boolean;
}

const LlmContext = createContext<LlmContextType | undefined>(undefined);

const apiUrl = import.meta.env.DEV
  ? "http://localhost:2024"
  : "http://localhost:8123";

interface LlmProviderProps {
  children: ReactNode;
}

const DEFAULT_EFFORT = 'medium'; // Default effort level
const DEFAULT_PROVIDER = 'gemini';
const DEFAULT_MODEL = 'gemini-2.0-flash-exp';

export const LlmProvider: React.FC<LlmProviderProps> = ({ children }) => {
  const [effort, setEffort] = useState<string>(DEFAULT_EFFORT);
  const [provider, setProvider] = useState<string>(DEFAULT_PROVIDER);
  const [model, setModel] = useState<string>(DEFAULT_MODEL);
  const [llmProviders, setLlmProviders] = useState<LlmProvider[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchLlmProviders = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`${apiUrl}/api/providers`);
        if (!response.ok) {
          throw new Error("Failed to fetch LLM providers");
        }
        const providers = await response.json() as LlmProvider[];
        setLlmProviders(providers);

        if (providers.length > 0) {
          // Try to find the default provider, otherwise use the first available
          const defaultProvider = providers.find(p => p.provider === DEFAULT_PROVIDER) || providers[0];
          setProvider(defaultProvider.provider);
          
          if (defaultProvider.models.length > 0) {
            // Try to find the default model, otherwise use the first available
            const defaultModel = defaultProvider.models.find(m => m.name === DEFAULT_MODEL) || defaultProvider.models[0];
            setModel(defaultModel.name);
          }
        }

      } catch (error) {
        console.error("Error fetching LLM providers:", error);
        // Fallback to default values if API fails
        setLlmProviders([{
          provider: DEFAULT_PROVIDER,
          models: [{
            name: DEFAULT_MODEL,
            displayName: "Gemini 2.0 Flash"
          }]
        }]);
        setProvider(DEFAULT_PROVIDER);
        setModel(DEFAULT_MODEL);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLlmProviders();
  }, []);

  useEffect(() => {
    // Ensure the model is set to a valid one when the provider changes
    const currentProvider = llmProviders.find(p => p.provider === provider);
    
    if (currentProvider && currentProvider.models.length > 0) {
      // Check if current model is valid for the new provider
      const isCurrentModelValid = currentProvider.models.some(m => m.name === model);
      if (!isCurrentModelValid) {
        // Set to the first available model for this provider
        setModel(currentProvider.models[0].name);
      }
    }
  }, [provider, llmProviders]);

  const contextValue: LlmContextType = {
    effort,
    provider,
    model,
    llmProviders,
    updateEffort: setEffort,
    updateProvider: setProvider,
    updateModel: setModel,
    isLoading,
  };

  return (
    <LlmContext.Provider value={contextValue}>
      {children}
    </LlmContext.Provider>
  );
};

export const useLlmContext = (): LlmContextType => {
  const context = useContext(LlmContext);
  if (context === undefined) {
    throw new Error('useLlmContext must be used within an LlmProvider');
  }
  return context;
}; 