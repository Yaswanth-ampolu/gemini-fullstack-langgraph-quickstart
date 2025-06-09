import { InputForm } from "./InputForm";
import { ProviderSelector } from "./ProviderSelector";
import { useLlmContext } from "@/contexts/LlmContext";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
}) => {
  const { provider } = useLlmContext();
  
  const getPoweredByText = () => {
    switch (provider.toLowerCase()) {
      case 'ollama':
        return 'Powered by Ollama and LangChain LangGraph.';
      case 'gemini':
        return 'Powered by Google Gemini and LangChain LangGraph.';
      default:
        return 'Powered by LangChain LangGraph.';
    }
  };

  return (
    <div className="flex flex-col items-center justify-center text-center px-4 flex-1 w-full max-w-3xl mx-auto gap-6">
      <div>
        <h1 className="text-5xl md:text-6xl font-semibold text-neutral-100 mb-3">
          Welcome.
        </h1>
        <p className="text-xl md:text-2xl text-neutral-400">
          How can I help you today?
        </p>
      </div>
      
      <div className="w-full max-w-md">
        <ProviderSelector />
      </div>
      
      <div className="w-full mt-4">
        <InputForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          onCancel={onCancel}
          hasHistory={false}
        />
      </div>
      
      <p className="text-xs text-neutral-500">
        {getPoweredByText()}
      </p>
    </div>
  );
};
