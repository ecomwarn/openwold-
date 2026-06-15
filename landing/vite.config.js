import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// `base` is set so the built assets resolve correctly when hosted under
// a subpath (e.g. GitHub Pages at /<repo>/). Override with VITE_BASE.
const base = process.env.VITE_BASE || '/';

export default defineConfig({
  base,
  plugins: [react()],
  server: { port: 5173, host: true },
});
