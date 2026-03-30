/**
 * API 请求封装
 * 统一管理 HTTP 请求和基础路径
 */

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
async function request(url, options = {}) {
  const fullUrl = getFulllUrl(url)
  
  // 调试日志
//   console.log('API Request:', { API_BASE, url, fullUrl })
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  }
  
  try {
    const response = await fetch(fullUrl, { ...defaultOptions, ...options })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    // 根据响应类型解析数据
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    }
    return await response.text()
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

/**
 * GET 请求
 * @param {string} url - 请求路径
 * @param {Object} params - URL 参数
 * @returns {Promise}
 */
export function get(url, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const fullUrl = queryString ? `${url}?${queryString}` : url
  return request(fullUrl, { method: 'GET' })
}

/**
 * POST 请求
 * @param {string} url - 请求路径
 * @param {Object} data - 请求体数据
 * @returns {Promise}
 */
export function post(url, data = {}) {
  return request(url, {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

/**
 * PUT 请求
 * @param {string} url - 请求路径
 * @param {Object} data - 请求体数据
 * @returns {Promise}
 */
export function put(url, data = {}) {
  return request(url, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

/**
 * DELETE 请求
 * @param {string} url - 请求路径
 * @returns {Promise}
 */
export function del(url) {
  return request(url, { method: 'DELETE' })
}

// API 接口定义
export const api = {
  // 节点相关
  nodes: {
    getList: () => get('/peers/list'),
    getDetail: (id) => get(`/nodes/${id}`),
    create: (data) => post('/nodes', data),
    update: (id, data) => put(`/nodes/${id}`, data),
    delete: (id) => del(`/nodes/${id}`)
  },
  
  // 配置相关
  configs: {
    needSetting: () => get('/configs/need_setting'),
    publicPeers: () => get('/configs/public_peers'),
    save: (data) => post('/configs/save', data),
    get: () => get('/configs/get')
  },
  
  // 窗口相关
  windows: {
    getDownloadUrl: () => getFulllUrl('/windows/download')
  },
  
  // 系统相关
  system: {
    getInfo: () => get('/system/info'),
    getStatus: () => get('/system/status'),
    restart: () => post('/system/restart')
  },
  
  // 日志相关
  logs: {
    getList: (params) => get('/logs', params),
    clear: () => post('/logs/clear')
  }
}

// 导出基础配置
export { API_BASE }
export default api
