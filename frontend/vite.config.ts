import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite' // 引入这个

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(), // 启用这个
  ],
})