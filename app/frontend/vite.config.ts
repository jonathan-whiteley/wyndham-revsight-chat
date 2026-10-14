import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // If the backend dies mid-stream, tear down the client response so the
        // browser sees a network failure instead of a hung SSE connection.
        configure: proxy => {
          proxy.on('proxyRes', (proxyRes, _req, res) => {
            const teardown = () => {
              if (!proxyRes.complete) res.destroy()
            }
            proxyRes.on('aborted', teardown)
            proxyRes.on('error', teardown)
            proxyRes.on('close', teardown)
          })
        },
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})





