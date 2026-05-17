import request from './request'

export function getDetectionRules(params) {
  return request.get('/api/detection/rules', { params })
}

export function createDetectionRule(data) {
  return request.post('/api/detection/rules', data)
}

export function deleteDetectionRule(id) {
  return request.delete(`/api/detection/rules/${id}`)
}

export function updateDetectionRule(id, data) {
  return request.put(`/api/detection/rules/${id}`, data)
}

export function getRuleSets(params) {
  return request.get('/api/detection/rule-sets', { params })
}

export function createRuleSet(data) {
  return request.post('/api/detection/rule-sets', data)
}

export function updateRuleSet(id, data) {
  return request.put(`/api/detection/rule-sets/${id}`, data)
}

export function deleteRuleSet(id) {
  return request.delete(`/api/detection/rule-sets/${id}`)
}

export function getRuleSetDetail(id) {
  return request.get(`/api/detection/rule-sets/${id}`)
}

export function createDetectionTask(data) {
  console.log('[API] 创建检测任务 - 请求数据:', JSON.stringify(data, null, 2))
  return request.post('/api/detection/tasks', data).catch(error => {
    console.error('[API] 创建检测任务失败:', error)
    if (error.response) {
      console.error('[API] 响应状态:', error.response.status)
      console.error('[API] 响应数据:', error.response.data)
    }
    throw error
  })
}

export function getDetectionTasks(params) {
  return request.get('/api/detection/tasks', { params })
}

export function getDetectionTask(id) {
  return request.get(`/api/detection/tasks/${id}`)
}

export function getDetectionResults(id, params) {
  return request.get(`/api/detection/tasks/${id}/results`, { params })
}

export function jumpToDesensitization(id) {
  return request.post(`/api/detection/tasks/${id}/jump-to-desensitization`)
}
