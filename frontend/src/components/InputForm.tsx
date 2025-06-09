import { useState } from "react";
import { Button } from "@/components/ui/button";
import { SquarePen, Send, StopCircle } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useLlmContext } from "@/contexts/LlmContext";
import { ProviderSelector } from "./ProviderSelector";

// Updated InputFormProps
interface InputFormProps {
  onSubmit: (inputValue: string, effort: string) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
  hasHistory,
}) => {
  const { effort, updateEffort } = useLlmContext();
  const [internalInputValue, setInternalInputValue] = useState("");

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim()) return;
    onSubmit(internalInputValue, effort);
    setInternalInputValue("");
  };

  const handleInternalKeyDown = (
    e: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleInternalSubmit();
    }
  };

  const isSubmitDisabled = !internalInputValue.trim() || isLoading;

  return (
    <div className="container-responsive space-y-4">
      {/* Main Input Container */}
      <div className="glass-enhanced rounded-2xl p-1 border-white/30 focus-within:border-white/50 transition-all duration-300">
        <form onSubmit={handleInternalSubmit} className="flex items-end gap-3 p-4">
          <div className="flex-1 min-w-0">
            <Textarea
              value={internalInputValue}
              onChange={(e) => setInternalInputValue(e.target.value)}
              onKeyDown={handleInternalKeyDown}
              placeholder="Ask me anything... What's on your mind?"
              className="w-full bg-transparent text-enhanced placeholder-white/60 resize-none border-0 focus:outline-none focus:ring-0 outline-none focus-visible:ring-0 shadow-none text-base leading-6 min-h-[24px] max-h-[120px] font-medium clean-text"
              rows={1}
            />
          </div>
          
          {/* Action Button - Standardized */}
          <div className="flex-shrink-0">
            {isLoading ? (
              <Button
                type="button"
                className="btn-standard glass-enhanced rounded-xl px-4 text-red-400 border-red-400/40 hover:border-red-400/60 hover:bg-red-500/15 font-semibold transition-all duration-300 clean-text"
                onClick={onCancel}
              >
                <StopCircle className="h-4 w-4 mr-2" />
                <span className="text-responsive">Stop</span>
              </Button>
            ) : (
              <Button
                type="submit"
                disabled={isSubmitDisabled}
                className={`btn-standard glass-enhanced rounded-xl px-4 sm:px-6 transition-all duration-300 font-semibold clean-text ${
                  isSubmitDisabled
                    ? "text-white/50 border-white/25 cursor-not-allowed"
                    : "text-blue-400 border-blue-400/40 hover:border-blue-400/60 hover:bg-blue-500/15 glow-blue"
                }`}
              >
                <Send className="h-4 w-4 mr-2" />
                <span className="text-responsive">Search</span>
              </Button>
            )}
          </div>
        </form>
      </div>

      {/* Control Bar - All Horizontal */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        {/* All Controls - Horizontal Layout */}
        <div className="flex items-center gap-2 flex-wrap">
          <ProviderSelector />
          
          {/* Effort Selector - Wider for Full Text */}
          <div className="glass-control clean-text">
            <Select value={effort} onValueChange={updateEffort}>
            <SelectTrigger className="min-w-fit h-6 bg-transparent border-none text-enhanced focus:ring-0 text-sm font-semibold clean-text">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glass-enhanced border-white/30 rounded-xl">
                <SelectItem value="low" className="text-enhanced hover:bg-white/15 focus:bg-white/15 rounded-lg cursor-pointer clean-text">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full bg-green-400"></div>
                    <span className="font-semibold">Low</span>
                  </div>
                </SelectItem>
                <SelectItem value="medium" className="text-enhanced hover:bg-white/15 focus:bg-white/15 rounded-lg cursor-pointer clean-text">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
                    <span className="font-semibold">Medium</span>
                  </div>
                </SelectItem>
                <SelectItem value="high" className="text-enhanced hover:bg-white/15 focus:bg-white/15 rounded-lg cursor-pointer clean-text">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full bg-red-400"></div>
                    <span className="font-semibold">High</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Right Side Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* New Search Button - Standardized */}
          {hasHistory && (
            <Button
              className="btn-standard glass-enhanced rounded-lg px-3 text-enhanced border-white/40 hover:border-white/50 hover:bg-white/15 font-semibold transition-all duration-300 clean-text"
              onClick={() => window.location.reload()}
            >
              <SquarePen className="h-4 w-4 mr-2" />
              <span className="text-responsive">New</span>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
