import request from './request'

export function generateReport(data) {
  return request({
    url: '/api/reports/generate',
    method: 'post',
    data
  })
}

export function generateTaskReport(taskId, data) {
  return request({
    url: `/api/reports/task/${taskId}`,
    method: 'post',
    data
  })
}

export function downloadReport(filename) {
  return request({
    url: `/api/reports/download/${filename}`,
    method: 'get',
    responseType: 'blob'
  })
}
