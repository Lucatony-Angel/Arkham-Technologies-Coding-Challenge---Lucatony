import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/data": "http://127.0.0.1:8000",
      "/refresh": "http://127.0.0.1:8000",
      "/analytics": "http://127.0.0.1:8000",
    },
  },
});
