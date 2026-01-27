import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  root: 'templates',
  base: '/projetDevMLOps/',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    minify: 'terser',
    sourcemap: false
  },
  publicDir: '../static',
  server: {
    port: 3000,
    open: true
  }
})
