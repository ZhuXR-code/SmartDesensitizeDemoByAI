import request from './request'

export function uploadFile(data) {
  return request.post('/api/datasets/upload', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function createFromText(data) {
  return request.post('/api/datasets/from-text', data)
}

export function getDatasetList(params) {
  return request.get('/api/datasets/list', { params })
}

export function getDatasetDetail(id) {
  return request.get(`/api/datasets/${id}`)
}

export function getDatasetPreview(id, params) {
  return request.get(`/api/datasets/${id}/preview`, { params })
}

export function deleteDataset(id) {
  return request.delete(`/api/datasets/${id}`)
}
