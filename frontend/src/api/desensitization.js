import request from './request'

export function getDesensitizationRules(params) {
  return request.get('/api/desensitization/rules', { params })
}

export function createDesensitizationRule(data) {
  return request.post('/api/desensitization/rules', data)
}

export function getDesensitizationKeys() {
  return request.get('/api/desensitization/keys')
}

export function autoDetectRules(datasetId, sampleSize = 50) {
  return request.post('/api/desensitization/auto-detect', null, {
    params: { dataset_id: datasetId, sample_size: sampleSize }
  })
}

export function previewDesensitization(data) {
  return request.post('/api/desensitization/preview', data)
}

export function createDesensitizationTask(data) {
  return request.post('/api/desensitization/tasks', data)
}

export function getDesensitizationTasks(params) {
  return request.get('/api/desensitization/tasks', { params })
}

export function getDesensitizationTask(id) {
  return request.get(`/api/desensitization/tasks/${id}`)
}

export function getDesensitizationResults(id, params) {
  return request.get(`/api/desensitization/tasks/${id}/results`, { params })
}

export function downloadDesensitizedFile(id) {
  return request.get(`/api/desensitization/tasks/${id}/download`, {
    responseType: 'blob'
  })
}

export function generateReport(id) {
  return request.post(`/api/desensitization/tasks/${id}/generate-report`)
}

export function downloadReport(id, format = 'html') {
  return request.get(`/api/desensitization/tasks/${id}/download-report`, {
    params: { format },
    responseType: 'blob'
  })
}
