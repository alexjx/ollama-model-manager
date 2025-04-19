import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  base: (() => {
    if (typeof process.env.VITE_BASE_PATH === 'undefined') {
      throw new Error('VITE_BASE_PATH must be defined in environment')
    }
    return process.env.VITE_BASE_PATH
  })(),
  plugins: [
    vue(),
    tailwindcss(),
  ],
  resolve: {
    alias: [
      { find: '@', replacement: path.resolve(__dirname, 'src') },
    ]
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
