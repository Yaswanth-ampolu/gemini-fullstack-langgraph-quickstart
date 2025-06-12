import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./global.css";
import App from "./App.tsx";
import { LlmProvider } from "./contexts/LlmContext.tsx";
import { McpProvider } from "./contexts/McpContext.tsx"; // Added McpProvider

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <LlmProvider>
        <McpProvider> {/* Added McpProvider */}
          <App />
        </McpProvider>
      </LlmProvider>
    </BrowserRouter>
  </StrictMode>
);
