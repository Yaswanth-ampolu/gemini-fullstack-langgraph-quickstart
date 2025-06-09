import { useLlmContext } from "@/contexts/LlmContext";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, Cpu, Cloud } from "lucide-react";

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
      <Card className="bg-neutral-700 border-neutral-600">
        <CardContent className="p-4">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm text-neutral-300">Loading providers...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const currentProvider = llmProviders.find(p => p.provider === provider);
  const availableModels = currentProvider?.models || [];

  const getProviderIcon = (providerName: string) => {
    switch (providerName.toLowerCase()) {
      case 'ollama':
        return <Cpu className="h-4 w-4" />;
      case 'gemini':
        return <Cloud className="h-4 w-4" />;
      default:
        return <Cloud className="h-4 w-4" />;
    }
  };

  const getProviderDescription = (providerName: string) => {
    switch (providerName.toLowerCase()) {
      case 'ollama':
        return 'Local AI models (Free, Private)';
      case 'gemini':
        return 'Google AI (Requires API key)';
      default:
        return 'Cloud AI service';
    }
  };

  return (
    <Card className="bg-neutral-700 border-neutral-600">
      <CardContent className="p-4 space-y-4">
        <div className="space-y-2">
          <Label htmlFor="provider-select" className="text-sm font-medium text-neutral-200">
            AI Provider
          </Label>
          <Select value={provider} onValueChange={updateProvider}>
            <SelectTrigger id="provider-select" className="bg-neutral-600 border-neutral-500 text-neutral-100">
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent className="bg-neutral-600 border-neutral-500">
              {llmProviders.map((p) => (
                <SelectItem 
                  key={p.provider} 
                  value={p.provider}
                  className="text-neutral-100 focus:bg-neutral-500"
                >
                  <div className="flex items-center space-x-2">
                    {getProviderIcon(p.provider)}
                    <div className="flex flex-col">
                      <span className="capitalize font-medium">{p.provider}</span>
                      <span className="text-xs text-neutral-400">
                        {getProviderDescription(p.provider)}
                      </span>
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {availableModels.length > 0 && (
          <div className="space-y-2">
            <Label htmlFor="model-select" className="text-sm font-medium text-neutral-200">
              Model
            </Label>
            <Select value={model} onValueChange={updateModel}>
              <SelectTrigger id="model-select" className="bg-neutral-600 border-neutral-500 text-neutral-100">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-600 border-neutral-500">
                {availableModels.map((m) => (
                  <SelectItem 
                    key={m.name} 
                    value={m.name}
                    className="text-neutral-100 focus:bg-neutral-500"
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">{m.displayName}</span>
                      <span className="text-xs text-neutral-400">{m.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {provider === 'ollama' && (
          <div className="text-xs text-neutral-400 bg-neutral-800 p-2 rounded">
            <strong>Note:</strong> Using Ollama with free DuckDuckGo search. 
            Make sure Ollama is running locally with the selected model.
          </div>
        )}

        {provider === 'gemini' && (
          <div className="text-xs text-neutral-400 bg-neutral-800 p-2 rounded">
            <strong>Note:</strong> Using Google Search API with Gemini. 
            Requires GEMINI_API_KEY and GOOGLE_SEARCH_API_KEY.
          </div>
        )}
      </CardContent>
    </Card>
  );
} 