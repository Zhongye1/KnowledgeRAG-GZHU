// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import svgLoader from 'vite-svg-loader'
import vueDevTools from 'vite-plugin-vue-devtools'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue(), svgLoader(), vueDevTools()],
  server: {
    // 确保开发服务器配置正确
    hmr: true,
    host: '0.0.0.0', // 允许外部访问
    port: 5173,      // 端口号
    watch: {
      usePolling: true // 在Docker中启用文件监听
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/lens-api': {
        target: 'https://api.lens.org',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/lens-api/, '')
      }
    }
  },
  resolve: {
    alias: {
      // 使用新的方式来设置别名
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
