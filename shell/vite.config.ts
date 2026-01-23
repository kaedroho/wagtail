import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import wyw from '@wyw-in-js/vite';

// https://vitejs.dev/config/
export default defineConfig({
  base: '/static/',
  build: {
    manifest: true,
    rollupOptions: {
      input: '/src/main.tsx',
    },
  },
  plugins: [
    react(),
    wyw({
      babelOptions: {
        presets: ['@babel/preset-typescript'],
      },
    }),
  ],
  server: {
    cors: {
      origin: 'http://192.168.122.58:8000',
    },
  },
  resolve: {
    alias: {
      '@django-bridge/react':
        '/home/karl/projects/wagtaildev/django-bridge/packages/react/src/index.tsx',
      '@common':
        '/home/karl/projects/wagtaildev/django-bridge/packages/common/index.ts',
    },
  },
});
