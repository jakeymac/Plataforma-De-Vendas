import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: resolve(__dirname, '../Plataforma_de_Vendas/core/static/core/js/react'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: '/src/main.jsx',
      output: {
        entryFileNames: 'index.js',
        assetFileNames: 'assets/[name][extname]',
      }
    },
  },
  server: {
    port: 5173,
    open: false,
  },
})