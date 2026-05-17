import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: process.env.VUE_APP_BASE_API || '',
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const timestamp = new Date().toISOString()
    console.log(`[${timestamp}] API请求 | ${config.method.toUpperCase()} ${config.url}`)
    
    if (config.data && !config.url.includes('upload')) {
      const safeData = { ...config.data }
      if (safeData.password) safeData.password = '***'
      if (safeData.token) safeData.token = '***'
      console.log(`请求数据:`, safeData)
    }
    
    config.metadata = { startTime: Date.now() }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    const duration = Date.now() - response.config.metadata?.startTime || 0
    const timestamp = new Date().toISOString()
    
    console.log(`[${timestamp}] API响应 | ${response.config.method?.toUpperCase()} ${response.config.url} | 状态: ${response.status} | 耗时: ${duration}ms`)
    
    // 如果是blob类型（文件下载），直接返回响应数据
    if (response.config.responseType === 'blob') {
      return response.data
    }
    
    const res = response.data
    
    if (res.code !== 200) {
      console.error(`API错误 | URL: ${response.config.url} | Code: ${res.code} | Message: ${res.message}`)
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  error => {
    const timestamp = new Date().toISOString()
    const duration = Date.now() - error.config?.metadata?.startTime || 0
    
    let errorMsg = '网络错误'
    let errorDetail = ''
    
    if (error.response) {
      const status = error.response.status
      const url = error.config?.url || 'unknown'
      
      console.error(`[${timestamp}] HTTP错误 | ${error.config?.method?.toUpperCase()} ${url} | 状态码: ${status} | 耗时: ${duration}ms`)
      
      switch (status) {
        case 400:
          errorMsg = '请求参数错误'
          errorDetail = error.response.data?.detail || error.response.data?.message || ''
          break
        case 401:
          errorMsg = '未授权，请重新登录'
          break
        case 403:
          errorMsg = '拒绝访问'
          break
        case 404:
          errorMsg = `请求的资源不存在 (${url})`
          console.error(`404错误详情 | URL: ${url} | 完整路径: ${error.config?.baseURL}${url}`)
          break
        case 500:
          errorMsg = '服务器内部错误'
          errorDetail = error.response.data?.detail || error.response.data?.message || ''
          console.error(`500错误详情:`, error.response.data)
          break
        case 502:
        case 503:
        case 504:
          errorMsg = `服务不可用 (${status})`
          break
        default:
          errorMsg = `请求失败 (${status})`
          errorDetail = error.response.data?.detail || error.message
      }
      
      console.error(`错误详情:`, {
        url,
        status,
        message: errorDetail,
        responseData: error.response.data,
        duration: `${duration}ms`
      })
      
    } else if (error.request) {
      console.error(`[${timestamp}] 网络错误 | 无响应 | URL: ${error.config?.url} | 耗时: ${duration}ms`)
      console.error('请求对象:', error.request)
      errorMsg = '网络连接失败，请检查网络或服务器状态'
      
      if (error.code === 'ECONNABORTED') {
        errorMsg = '请求超时，请稍后重试'
      }
    } else {
      console.error(`[${timestamp}] 未知错误 | ${error.message}`)
      errorMsg = error.message || '未知错误'
    }
    
    ElMessage.error(errorMsg)
    
    const errorObj = new Error(errorMsg)
    errorObj.originalError = error
    errorObj.detail = errorDetail
    errorObj.timestamp = timestamp
    errorObj.duration = duration
    
    return Promise.reject(errorObj)
  }
)

export default request
