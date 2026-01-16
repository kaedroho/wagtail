import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';

// https://vitejs.dev/config/
export default defineConfig({
  base: '/static/',
  build: {
    manifest: true,
    rollupOptions: {
      input: '/src/main.tsx',
    },
  },
  plugins: [react()],
  server: {
    cors: {
      origin: 'http://192.168.122.58:8000',
    },
  },
});
