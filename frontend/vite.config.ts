import { appendFileSync } from 'node:fs'
import { resolve } from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'

// #region agent log
const DEBUG_LOG = resolve(__dirname, '..', 'debug-4eb7cd.log')

function debugListenPlugin(): Plugin {
  return {
    name: 'debug-listen-address',
    configureServer(server) {
      server.httpServer?.once('listening', () => {
        const addr = server.httpServer?.address()
        try {
          appendFileSync(
            DEBUG_LOG,
            `${JSON.stringify({
              sessionId: '4eb7cd',
              hypothesisId: 'H2',
              location: 'vite.config.ts:configureServer',
              message: 'Vite listening',
              data: { address: addr },
              timestamp: Date.now(),
            })}\n`,
          )
        } catch {
          /* ignore */
        }
      })
    },
  }
}
// #endregion

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), debugListenPlugin()],
  server: {
    // Bind IPv4 as well as IPv6 so http://127.0.0.1:5173 works (QR join URLs use 127.0.0.1).
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
