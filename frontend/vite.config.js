import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { VarletUIResolver } from 'unplugin-vue-components/resolvers'

// 生产环境配置
const BASE = '/cgi/ThirdParty/EasyTier-Lite/index.cgi'
const API_BASE = '/cgi/ThirdParty/EasyTier-Lite/api.cgi'
const fnosToken = 'k/8Qbvscxmlur9xYlceJUssSS7ho0AM7CN4r/qM6p9U='

export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? BASE : './',
  plugins: [
    vue(),
    // 自动导入 Vue 相关 API
    AutoImport({
      imports: [
        'vue'
      ],
      dts: 'src/auto-imports.d.ts'
    }),
    // 自动导入组件
    Components({
      resolvers: [VarletUIResolver()],
      dts: 'src/components.d.ts'
    })
  ],
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
    watch: {
      usePolling: true,
      interval: 1000
    },
    proxy: {
      '/cgi': {
        // target: 'http://192.168.220.3:5666',
        target: 'http://localhost:5666',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            proxyReq.setHeader('authorization', `trim ${fnosToken}`)
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
