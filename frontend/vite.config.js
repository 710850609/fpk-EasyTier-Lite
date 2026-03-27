import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// 生产环境配置
const BASE = '/cgi/ThirdParty/EasyTier-Lite/index.cgi'
const API_BASE = '/cgi/ThirdParty/EasyTier-Lite/api.cgi'

export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? BASE : './',
  plugins: [vue()],
  define: {
    // 注入 API 基础路径（统一使用生产路径）
    __API_BASE__: JSON.stringify(API_BASE)
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      '/cgi': {
        target: 'https://192.168.220.3:5667',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            proxyReq.setHeader('authorization', 'trim HA/SV4nYxWnIkgA9DkT9GOfSjgfL/z5VLfqyEbGChac=')
            console.log('Proxying to:', options.target + req.url)
          })
          proxy.on('error', (err, req, res) => {
            console.log('Proxy error:', err)
          })
        },
      },
    },
  }
}))
