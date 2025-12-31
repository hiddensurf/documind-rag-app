import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      ignored: [
        '**/backend/**',           // Ignore entire backend folder
        '**/venv/**',              // Ignore Python virtual env
        '**/.git/**',              // Ignore git
        '**/node_modules/**'       // Already ignored by default
      ]
    }
  }
})
