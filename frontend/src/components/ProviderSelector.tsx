import { useLlmContext } from "@/contexts/LlmContext";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2 } from "lucide-react";

export function ProviderSelector() {
  const { 
    provider, 
    model, 
    llmProviders, 
    updateProvider, 
    updateModel, 
    isLoading 
  } = useLlmContext();

  if (isLoading) {
    return (
      <div className="glass-control clean-text">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-4 w-4 animate-spin text-white/70" />
          <span className="text-sm text-white/70 font-medium">Loading...</span>
        </div>
      </div>
    );
  }

  const currentProvider = llmProviders.find(p => p.provider === provider);
  const availableModels = currentProvider?.models || [];

  const getProviderDescription = (providerName: string) => {
    switch (providerName.toLowerCase()) {
      case 'ollama':
        return 'Local AI models (Free, Private)';
      case 'gemini':
        return 'Google Gemini';
      default:
        return 'Cloud AI service';
    }
  };

  const getProviderColor = (providerName: string) => {
    switch (providerName.toLowerCase()) {
      case 'ollama':
        return 'text-green-400';
      case 'gemini':
        return 'text-blue-400';
      default:
        return 'text-white/70';
    }
  };

  return (
    <>
      {/* Provider Selection - Clean Text Only */}
      <div className="glass-control clean-text">
        <Select value={provider} onValueChange={updateProvider}>
          <SelectTrigger className="w-auto min-w-[80px] h-6 bg-transparent border-none text-enhanced focus:ring-0 text-sm font-semibold clean-text">
            <SelectValue placeholder="Provider" />
          </SelectTrigger>
          <SelectContent className="glass-enhanced border-white/30 rounded-xl min-w-[280px]">
            {llmProviders.map((p) => (
              <SelectItem 
                key={p.provider} 
                value={p.provider}
                className="text-enhanced hover:bg-white/15 focus:bg-white/15 rounded-lg my-1 cursor-pointer clean-text"
              >
                <div className="flex flex-col py-2">
                  <span className={`capitalize font-bold text-sm ${getProviderColor(p.provider)}`}>{p.provider}</span>
                  <span className="text-xs text-white/70 font-medium">
                    {getProviderDescription(p.provider)}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Model Selection - Clean Text Only */}
      {availableModels.length > 0 && (
        <div className="glass-control clean-text">
          <Select value={model} onValueChange={updateModel}>
            <SelectTrigger className="w-auto min-w-[100px] max-w-[160px] h-6 bg-transparent border-none text-enhanced focus:ring-0 text-sm font-semibold clean-text">
              <SelectValue placeholder="Model" />
            </SelectTrigger>
            <SelectContent className="glass-enhanced border-white/30 rounded-xl min-w-[200px]">
              {availableModels.map((m) => (
                <SelectItem 
                  key={m.name} 
                  value={m.name}
                  className="text-enhanced hover:bg-white/15 focus:bg-white/15 rounded-lg my-1 cursor-pointer clean-text"
                >
                  <div className="flex flex-col py-1">
                    <span className="font-bold text-enhanced text-sm">{m.displayName}</span>
                    <span className="text-xs text-white/70 font-mono font-medium truncate-responsive">{m.name}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}
    </>
  );
} 