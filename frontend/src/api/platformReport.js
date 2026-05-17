import request from './request'

export function getPlatformOverview() {
  return request.get('/api/platform-report/overview')
}

export function getSecurityValue() {
  return request.get('/api/platform-report/security-value')
}

export function getEfficiencyStats() {
  return request.get('/api/platform-report/efficiency')
}

export function getTechnologyHighlights() {
  return request.get('/api/platform-report/technology')
}

export function getComplianceStats() {
  return request.get('/api/platform-report/compliance')
}
