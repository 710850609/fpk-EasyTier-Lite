/**
 * API 请求封装
 * 统一管理 HTTP 请求和基础路径
 */
import toast from '../components/toast.js'

// 使用 Vite 注入的环境变量
const API_BASE = typeof __API_BASE__ !== 'undefined' ? __API_BASE__ : '/'
// console.log(API_BASE)

function getFulllUrl(url) {
  return url.startsWith('http') ? url : `${API_BASE}${url}`
}

/**
 * 发送 HTTP 请求
 * @param {string} url - 请求路径（会自动拼接 API_BASE）
 * @param {Object} options - fetch 选项
 * @returns {Promise} - 返回响应数据
 */
async function request(url, options = {}, otherOptions = {}) {
  const toastError = (otherOptions.toastError === undefined || otherOptions.toastError == null) ? true : options.toastError
  const fullUrl = getFulllUrl(url)
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  }
  try {
    const response = await fetch(fullUrl, { ...defaultOptions, ...options })
    
    if (!response.ok) {
      throw new Error(`HTTP status: ${response.status}\n${fullUrl}`)
    }    
    // 根据响应类型解析数据
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json().then(data => {
        if (data.code === 0) {
          return data
        }
        throw new Error(data.data || 'API error')
      })
    }
    return await response.text()
  } catch (error) {
    console.error('API request failed:', error)
    if (toastError) {
      toast.error(error.message)
    }
    throw error
  }
}

/**
 * GET 请求
 * @param {string} url - 请求路径
 * @param {Object} params - URL 参数
 * @returns {Promise}
 */
export function get(url, params = {}, otherOptions = {}) {
  const queryString = new URLSearchParams(params).toString()
  const fullUrl = queryString ? `${url}?${queryString}` : url
  return request(fullUrl, { ...params, method: 'GET' }, otherOptions)
}

/**
 * POST 请求
 * @param {string} url - 请求路径
 * @param {Object} data - 请求体数据
 * @returns {Promise}
 */
export function post(url, data = {}, options = {}, otherOptions = {}) {
  return request(url, {
    method: 'POST',
    body: JSON.stringify(data),
    ...options
  }, otherOptions)
}

/**
 * PUT 请求
 * @param {string} url - 请求路径
 * @param {Object} data - 请求体数据
 * @returns {Promise}
 */
export function put(url, data = {}, options = {}, otherOptions = {}) {
  return request(url, {
    method: 'PUT',
    body: JSON.stringify(data),
    ...options  
  }, otherOptions)
}

/**
 * DELETE 请求
 * @param {string} url - 请求路径
 * @returns {Promise}
 */
export function del(url, options = {}, otherOptions = {}) {
  return request(url, { method: 'DELETE', ...options }, otherOptions) 
}

// API 接口定义
export const api = {
  // 节点相关
  nodes: {
    getList: () => get('/peers/list', {}, {toastError: false}),
  },
  
  // 配置相关
  configs: {
    needSetting: () => get('/configs/need_setting'),
    publicPeers: () => get('/configs/public_peers'),
    save: (data) => post('/configs/save', data),
    saveToml: (data) => post('/configs/save_toml', {toml: data}),
    get: () => get('/configs/get'),
    getToml: () => get('/configs/get_toml'),
    getDownloadUrl: () => getFulllUrl('/configs/download')
  },
  // 服务相关
  services: {
    status: () => get('/services/status'),
    restart: () => get('/services/restart'),
  },
  
  // 窗口相关
  windows: {
    getDownloadUrl: () => getFulllUrl('/windows/download')
  },
  // ET 核心相关
  etCore: {
    getVersion: () => get('/et_core/version'),
    install: (data) => post('/et_core/install', data),
  },
  // 设置相关
  settings: {
    getGithubMirrors: () => get('/settings/github_mirrors'),
    saveGithubMirror: (data) => post('/settings/save_github_mirror', data),
  }
}

// 导出基础配置
export { API_BASE }
export default api
