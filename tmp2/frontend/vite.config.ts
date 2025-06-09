import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";

// Cross-platform fix for path resolution
// The usual `new URL(".", import.meta.url).pathname` breaks on Windows
// (e.g., "C:\path" turns into "/C:/path" and causes issues)
// This approach works reliably on all platforms

function resolveSrcPath(): string {
  try {
    // Modern ESM approach (preferred for Linux/Mac)
    const esmPath = new URL(".", import.meta.url).pathname;
    // On Windows, pathname might have issues, so we validate it
    const resolvedPath = path.resolve(esmPath, "./src");
    
    // Quick validation - if the path looks wrong (common on Windows), use fallback
    if (process.platform === "win32" && esmPath.startsWith("/C:")) {
      throw new Error("Windows path issue detected");
    }
    
    return resolvedPath;
  } catch {
    // Fallback for Windows or any environment where ESM URL handling fails
    return path.resolve(__dirname, "./src");
  }
}

const srcPath = resolveSrcPath();

// Debug log for development (can be removed in production)
console.log(`[Vite Config] Resolved src path: ${srcPath}`);

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/app/",
  resolve: {
    alias: {
      "@": srcPath,
    },
  },
  server: {
    proxy: {
      // Proxy API requests to the backend server
      "/api": {
        target: "http://127.0.0.1:8000", // Default backend address
        changeOrigin: true,
        // Optionally rewrite path if needed (e.g., remove /api prefix if backend doesn't expect it)
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
