import type React from "react";
import type { Message } from "@langchain/langgraph-sdk";
import { Loader2, Copy, CopyCheck, User, Bot } from "lucide-react";
import { InputForm } from "@/components/InputForm";
import { Button } from "@/components/ui/button";
import { useState, ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  ActivityTimeline,
  ProcessedEvent,
} from "@/components/ActivityTimeline"; // Assuming ActivityTimeline is in the same dir or adjust path

// Markdown component props type from former ReportView
type MdComponentProps = {
  className?: string;
  children?: ReactNode;
  [key: string]: any;
};

// Enhanced Markdown components with better visibility
const mdComponents = {
  h1: ({ className, children, ...props }: MdComponentProps) => (
    <h1 className={cn("text-2xl font-bold mt-4 mb-2 text-white", className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: MdComponentProps) => (
    <h2 className={cn("text-xl font-bold mt-3 mb-2 text-white", className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: MdComponentProps) => (
    <h3 className={cn("text-lg font-bold mt-3 mb-1 text-white", className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: MdComponentProps) => (
    <p className={cn("mb-3 leading-7 text-gray-100", className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }: MdComponentProps) => (
    <Badge className="text-xs mx-0.5 bg-blue-500/20 border-blue-400/30 hover:bg-blue-500/30">
      <a
        className={cn("text-blue-300 hover:text-blue-200 text-xs font-medium", className)}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    </Badge>
  ),
  ul: ({ className, children, ...props }: MdComponentProps) => (
    <ul className={cn("list-disc pl-6 mb-3 text-gray-100", className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: MdComponentProps) => (
    <ol className={cn("list-decimal pl-6 mb-3 text-gray-100", className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: MdComponentProps) => (
    <li className={cn("mb-1 text-gray-100", className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }: MdComponentProps) => (
    <blockquote
      className={cn(
        "border-l-4 border-blue-400 pl-4 italic my-3 text-sm bg-blue-500/10 py-2 rounded-r-lg text-blue-100",
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }: MdComponentProps) => (
    <code
      className={cn(
        "bg-gray-800 text-green-300 rounded px-2 py-1 font-mono text-sm border border-gray-600",
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }: MdComponentProps) => (
    <pre
      className={cn(
        "bg-gray-900 text-green-300 p-4 rounded-lg overflow-x-auto font-mono text-sm my-3 border border-gray-700",
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }: MdComponentProps) => (
    <hr className={cn("border-gray-600 my-4", className)} {...props} />
  ),
  table: ({ className, children, ...props }: MdComponentProps) => (
    <div className="my-3 overflow-x-auto">
      <table className={cn("border-collapse w-full bg-gray-800/50 rounded-lg overflow-hidden", className)} {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ className, children, ...props }: MdComponentProps) => (
    <th
      className={cn(
        "border border-gray-600 px-3 py-2 text-left font-bold bg-gray-700 text-white",
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }: MdComponentProps) => (
    <td
      className={cn("border border-gray-600 px-3 py-2 text-gray-100", className)}
      {...props}
    >
      {children}
    </td>
  ),
};

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  message: Message;
  mdComponents: typeof mdComponents;
}

// Modern HumanMessageBubble Component with better visibility
const HumanMessageBubble: React.FC<HumanMessageBubbleProps> = ({
  message,
  mdComponents,
}) => {
  return (
    <div className="flex items-start gap-3 justify-end">
      <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl rounded-br-md p-4 max-w-[80%] shadow-lg border border-blue-500/30">
        <div className="text-white">
          <ReactMarkdown components={mdComponents}>
            {typeof message.content === "string"
              ? message.content
              : JSON.stringify(message.content)}
          </ReactMarkdown>
        </div>
      </div>
      <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center shadow-lg">
        <User className="h-4 w-4 text-white" />
      </div>
    </div>
  );
};

// Props for AiMessageBubble
interface AiMessageBubbleProps {
  message: Message;
  historicalActivity: ProcessedEvent[] | undefined;
  liveActivity: ProcessedEvent[] | undefined;
  isLastMessage: boolean;
  isOverallLoading: boolean;
  mdComponents: typeof mdComponents;
  handleCopy: (text: string, messageId: string) => void;
  copiedMessageId: string | null;
}

// Modern AiMessageBubble Component with better visibility
const AiMessageBubble: React.FC<AiMessageBubbleProps> = ({
  message,
  historicalActivity,
  liveActivity,
  isLastMessage,
  isOverallLoading,
  mdComponents,
  handleCopy,
  copiedMessageId,
}) => {
  // Determine which activity events to show and if it's for a live loading message
  const activityForThisBubble =
    isLastMessage && isOverallLoading ? liveActivity : historicalActivity;
  const isLiveActivityForThisBubble = isLastMessage && isOverallLoading;

  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center shadow-lg">
        <Bot className="h-4 w-4 text-white" />
      </div>
      <div className="bg-gray-800/90 backdrop-blur-sm rounded-2xl rounded-bl-md p-5 max-w-[85%] shadow-xl border border-gray-700/50 space-y-4">
        {activityForThisBubble && activityForThisBubble.length > 0 && (
          <div className="bg-gray-900/60 rounded-xl p-4 border border-gray-600/30">
            <ActivityTimeline
              processedEvents={activityForThisBubble}
              isLoading={isLiveActivityForThisBubble}
            />
          </div>
        )}
        
        <div className="prose prose-invert max-w-none">
          <ReactMarkdown components={mdComponents}>
            {typeof message.content === "string"
              ? message.content
              : JSON.stringify(message.content)}
          </ReactMarkdown>
        </div>
        
        <div className="flex justify-end pt-2 border-t border-gray-700/30">
          <Button
            size="sm"
            className="bg-gray-700/50 hover:bg-gray-600/50 rounded-lg px-3 py-1.5 text-gray-300 hover:text-white border border-gray-600/30 hover:border-gray-500/50 transition-all duration-200"
            onClick={() =>
              handleCopy(
                typeof message.content === "string"
                  ? message.content
                  : JSON.stringify(message.content),
                message.id!
              )
            }
          >
            {copiedMessageId === message.id ? (
              <>
                <CopyCheck className="h-3 w-3 mr-1.5 text-green-400" />
                <span className="text-xs font-medium text-green-400">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3 mr-1.5" />
                <span className="text-xs font-medium">Copy</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

interface ChatMessagesViewProps {
  messages: Message[];
  isLoading: boolean;
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
  onSubmit: (inputValue: string, effort: string) => void;
  onCancel: () => void;
  liveActivityEvents: ProcessedEvent[];
  historicalActivities: Record<string, ProcessedEvent[]>;
}

export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  liveActivityEvents,
  historicalActivities,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Modern Header Panel */}
      <div className="bg-gray-800/80 backdrop-blur-sm rounded-t-2xl border border-gray-700/50 p-4 mb-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse shadow-lg shadow-green-400/50"></div>
            <span className="text-white font-medium text-sm">
              Chat Active
            </span>
          </div>
          <div className="text-gray-400 text-xs font-medium bg-gray-700/50 px-2 py-1 rounded-full">
            {messages.length} messages
          </div>
        </div>
      </div>

      {/* Scrollable Messages Area with better contrast */}
      <div className="flex-1 min-h-0 relative">
        <div 
          ref={scrollAreaRef}
          className="h-full overflow-y-auto messages-scroll px-4"
        >
          <div className="space-y-6 pb-6">
            {messages.map((message, index) => {
              const isLast = index === messages.length - 1;
              return (
                <div key={message.id || `msg-${index}`} className="animate-fadeInUpSmooth">
                  {message.type === "human" ? (
                    <HumanMessageBubble
                      message={message}
                      mdComponents={mdComponents}
                    />
                  ) : (
                    <AiMessageBubble
                      message={message}
                      historicalActivity={historicalActivities[message.id!]}
                      liveActivity={liveActivityEvents}
                      isLastMessage={isLast}
                      isOverallLoading={isLoading}
                      mdComponents={mdComponents}
                      handleCopy={handleCopy}
                      copiedMessageId={copiedMessageId}
                    />
                  )}
                </div>
              );
            })}
            
            {/* Enhanced Loading State */}
            {isLoading &&
              (messages.length === 0 ||
                messages[messages.length - 1].type === "human") && (
                <div className="flex items-start gap-3 animate-fadeInUpSmooth">
                  <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center shadow-lg">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                  <div className="bg-gray-800/90 backdrop-blur-sm rounded-2xl rounded-bl-md p-5 border border-gray-700/50 w-full max-w-2xl shadow-xl">
                    {liveActivityEvents.length > 0 ? (
                      <div className="text-sm">
                        <ActivityTimeline
                          processedEvents={liveActivityEvents}
                          isLoading={true}
                        />
                      </div>
                    ) : (
                      <div className="flex items-center space-x-3">
                        <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
                        <span className="text-gray-200 font-medium">AI is thinking...</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
          </div>
        </div>
      </div>

      {/* Modern Input Form */}
      <div className="bg-gray-800/80 backdrop-blur-sm rounded-b-2xl border border-gray-700/50 p-4 mt-4 shadow-lg">
        <InputForm
          onSubmit={onSubmit}
          isLoading={isLoading}
          onCancel={onCancel}
          hasHistory={messages.length > 0}
        />
      </div>
    </div>
  );
}
