// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/assets/Common.scss";`
        // 경로는 src 기준 (@ 별칭 사용)
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')  // @ → src 경로 설정
    }
  }
})
