import request from './request'

export const testConnection = (data) => {
  return request({
    url: '/api/data-sources/test-connection',
    method: 'post',
    data
  })
}

export const getTables = (data) => {
  return request({
    url: '/api/data-sources/tables',
    method: 'post',
    data
  })
}

export const previewTable = (data) => {
  return request({
    url: '/api/data-sources/table-preview',
    method: 'post',
    data
  })
}

export const saveAndImport = (data) => {
  return request({
    url: '/api/data-sources/save-and-import',
    method: 'post',
    data
  })
}

export const getDataSourceList = (params) => {
  return request({
    url: '/api/data-sources/list',
    method: 'get',
    params
  })
}

export const getSourceDatasets = (sourceId) => {
  return request({
    url: `/api/data-sources/${sourceId}/datasets`,
    method: 'get'
  })
}

export const deleteDataSource = (sourceId) => {
  return request({
    url: `/api/data-sources/${sourceId}`,
    method: 'delete'
  })
}

export const saveDataSource = (data) => {
  return request({
    url: '/api/data-sources/save',
    method: 'post',
    data
  })
}

export const getDataSourceDetail = (sourceId) => {
  return request({
    url: `/api/data-sources/${sourceId}`,
    method: 'get'
  })
}

export const updateDataSource = (sourceId, data) => {
  return request({
    url: `/api/data-sources/${sourceId}`,
    method: 'put',
    data
  })
}

export const testSavedConnection = (sourceId) => {
  return request({
    url: `/api/data-sources/${sourceId}/test-connection`,
    method: 'post'
  })
}

export const getSavedSourceTables = (sourceId) => {
  return request({
    url: `/api/data-sources/${sourceId}/tables`,
    method: 'post'
  })
}

export const previewSavedTable = (sourceId, data) => {
  return request({
    url: `/api/data-sources/${sourceId}/table-preview`,
    method: 'post',
    data
  })
}

export const importTablesFromSource = (sourceId, data) => {
  return request({
    url: `/api/data-sources/${sourceId}/import-tables`,
    method: 'post',
    data
  })
}
