import request from './request'

export function getAiConfig() {
  return request({ url: '/api/ai/config', method: 'get' })
}

export function getAiConfigs() {
  return request({ url: '/api/ai/configs', method: 'get' })
}

export function getAiConfigDetail(id) {
  return request({ url: `/api/ai/config/${id}`, method: 'get' })
}

export function saveAiConfig(data) {
  return request({ url: '/api/ai/config', method: 'post', data })
}

export function updateConfig(id, data) {
  return request({ url: `/api/ai/config/${id}`, method: 'put', data })
}

export function deleteConfig(id) {
  return request({ url: `/api/ai/config/${id}`, method: 'delete' })
}

export function activateConfig(id) {
  return request({ url: `/api/ai/config/${id}/activate`, method: 'post' })
}

export function testAiConnection(configId) {
  if (typeof configId === 'object') {
    return request({ url: '/api/ai/test', method: 'post', data: configId })
  }
  return request({ url: `/api/ai/config/${configId}/test`, method: 'post' })
}

export function getAiModels() {
  return request({ url: '/api/ai/models', method: 'get' })
}

export function createAiDetectionTask(data) {
  return request({ url: '/api/ai/detect', method: 'post', data })
}

export function getAiDetectionTasks() {
  return request({ url: '/api/ai/detect/tasks', method: 'get' })
}

export function getAiDetectionTaskDetail(id) {
  return request({ url: `/api/ai/detect/tasks/${id}`, method: 'get' })
}

export function cancelAiDetectionTask(id) {
  return request({ url: `/api/ai/detect/tasks/${id}/cancel`, method: 'post' })
}

export function clearAiDetectionTasks() {
  return request({ url: '/api/ai/detect/tasks/clear', method: 'delete' })
}

export function deleteAiDetectionTask(taskId) {
  return request({ url: `/api/ai/detect/tasks/${taskId}`, method: 'delete' })
}

export function clearAiDesensitizationTasks() {
  return request({ url: '/api/ai/desensitize/tasks/clear', method: 'delete' })
}

export function deleteAiDesensitizationTask(taskId) {
  return request({ url: `/api/ai/desensitize/tasks/${taskId}`, method: 'delete' })
}

export function exportAiDetectionResults(id) {
  return request({ url: `/api/ai/detect/results/${id}/export`, method: 'get' })
}

export function generateHtmlReport(id) {
  return request({ url: `/api/ai/detect/tasks/${id}/report/html`, method: 'get' })
}

export function generateMarkdownReport(id) {
  return request({ url: `/api/ai/detect/tasks/${id}/report/markdown`, method: 'get' })
}

export function reviewDetectionResult(resultId, data) {
  return request({ url: `/api/ai/detect/results/${resultId}/review`, method: 'post', data })
}

export function getReviewStats(taskId) {
  return request({ url: `/api/ai/detect/tasks/${taskId}/review/stats`, method: 'get' })
}

export function generateDesensitizationHtmlReport(id) {
  return request({ url: `/api/ai/desensitize/tasks/${id}/report/html`, method: 'get' })
}

export function generateDesensitizationMarkdownReport(id) {
  return request({ url: `/api/ai/desensitize/tasks/${id}/report/markdown`, method: 'get' })
}

export function previewReport(filePath) {
  const fname = filePath.replace(/\\/g, '/').split('/').pop()
  return `/api/ai/report/${fname}/preview`
}

export function downloadReport(filePath, label) {
  const a = document.createElement('a')
  a.href = '/' + filePath.replace(/\\/g, '/')
  a.download = label || filePath.replace(/\\/g, '/').split('/').pop() || 'report'
  a.click()
}

export function createAiDesensitizationTask(data) {
  return request({ url: '/api/ai/desensitize', method: 'post', data })
}

export function getAiDesensitizationTasks() {
  return request({ url: '/api/ai/desensitize/tasks', method: 'get' })
}

export function getAiDesensitizationTaskDetail(id) {
  return request({ url: `/api/ai/desensitize/tasks/${id}`, method: 'get' })
}
