import { InputForm } from "./InputForm";
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
        return 'Powered by Pinnacle AI ';
    }
  };

  return (
    <div className="flex flex-col items-center justify-center text-center px-6 flex-1 w-full max-w-4xl mx-auto">
      {/* Background Orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl float-animation"></div>
        <div className="absolute top-1/3 right-1/4 w-48 h-48 bg-blue-500/20 rounded-full blur-3xl float-animation animation-delay-400"></div>
        <div className="absolute bottom-1/3 left-1/3 w-32 h-32 bg-cyan-500/20 rounded-full blur-2xl float-animation animation-delay-800"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 w-full space-y-8 animate-fadeInUp">
        {/* Hero Section */}
        <div className="space-y-4">
          <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent leading-tight">
            Welcome.
          </h1>
          <p className="text-xl md:text-2xl text-white/70 font-light">
            How can I help you today?
          </p>
        </div>
        
        {/* Input Form with Controls */}
        <div className="w-full max-w-2xl mx-auto animate-fadeInUp animation-delay-200">
          <InputForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            onCancel={onCancel}
            hasHistory={false}
          />
        </div>
        
        {/* Footer */}
        <div className="animate-fadeInUp animation-delay-600">
          <p className="text-sm text-white/50 font-light">
            {getPoweredByText()}
          </p>
        </div>
      </div>
    </div>
  );
};
