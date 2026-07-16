import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const configPath = resolve(
  root,
  "node_modules/@hexlet/project-devops-deploy-crud-frontend/vite.config.ts",
);

let source = readFileSync(configPath, "utf8");
if (!source.includes("preview:") || source.includes("preview: {\n    port: 5173,\n    host: \"0.0.0.0\",\n    proxy:")) {
  // already patched or unexpected format — try idempotent replace
}

const unpatched = `  preview: {
    port: 5173,
    host: "0.0.0.0",
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      '/api': {
        target: API_URL,
        changeOrigin: true,
        secure: false,
      },
    },
  },`;

const patched = `  preview: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: API_URL,
        changeOrigin: true,
        secure: false,
      },
      "/r": {
        target: API_URL,
        changeOrigin: true,
        secure: false,
      },
    },
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: API_URL,
        changeOrigin: true,
        secure: false,
      },
      "/r": {
        target: API_URL,
        changeOrigin: true,
        secure: false,
      },
    },
  },`;

if (source.includes(unpatched)) {
  writeFileSync(configPath, source.replace(unpatched, patched));
  console.log("Patched frontend vite.config.ts (preview/server proxy)");
} else if (source.includes('"/r"') || source.includes("'/r'")) {
  console.log("Frontend vite.config.ts already has /r proxy");
} else {
  console.warn("Could not patch frontend vite.config.ts — check format");
}
