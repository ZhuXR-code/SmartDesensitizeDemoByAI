<template>
  <div class="data-source-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>已配置的数据源</span>
          <div>
            <el-button type="primary" @click="goToManage">
              <el-icon><Plus /></el-icon>
              新建数据源
            </el-button>
            <el-button @click="loadSourceList" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新列表
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="sourceList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        
        <el-table-column prop="name" label="数据源名称" min-width="180">
          <template #default="scope">
            <el-link type="primary" @click="goToManage(scope.row.id)">
              {{ scope.row.name }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column prop="source_type" label="类型" width="90">
          <template #default="scope">
            <el-tag v-if="scope.row.source_type === 'database'" type="primary" size="small">数据库</el-tag>
            <el-tag v-else type="info" size="small">{{ scope.row.source_type }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="连接信息" min-width="300">
          <template #default="scope">
            <div v-if="scope.row.config" class="connection-info">
              <el-tag size="small" type="info">{{ (scope.row.config.db_type || 'mysql').toUpperCase() }}</el-tag>
              <span class="separator">://</span>
              <strong>{{ scope.row.config.username || '***' }}</strong>
              <span class="separator">@</span>
              <span>{{ scope.row.config.host }}:{{ scope.row.config.port }}</span>
              <span class="separator">/</span>
              <span>{{ scope.row.config.database }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-button 
              link 
              type="success" 
              size="small" 
              @click="quickTestConnection(scope.row)"
              :loading="scope.row._testing"
            >
              {{ scope.row._connected ? '已连接' : '测试连接' }}
            </el-button>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="170" />

        <el-table-column label="操作" min-width="220" fixed="right" align="right">
          <template #default="scope">
            <el-space wrap :size="4">
              <el-button link type="primary" size="small" class="glass-btn-solid" @click="goToManage(scope.row.id)">
                <el-icon><View /></el-icon>
              </el-button>

              <el-button link type="warning" size="small" class="glass-btn-solid" @click="editDataSource(scope.row)">
                <el-icon><Edit /></el-icon>
              </el-button>

              <el-button link type="primary" size="small" class="glass-btn-solid" @click="viewDatasets(scope.row)">
                <el-icon><Collection /></el-icon>
              </el-button>

              <el-popconfirm
                title="确定删除此数据源？将同时删除关联的所有数据集！"
                @confirm="deleteSource(scope.row)"
                confirm-button-text="确定删除"
                cancel-button-text="取消"
                confirm-button-type="danger"
              >
                <template #reference>
                  <el-button link type="danger" size="small" class="glass-btn-solid">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-popconfirm>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && sourceList.length === 0" class="empty-state">
        <el-empty description="暂无已配置的数据源">
          <el-button type="primary" @click="goToManage">
            立即添加第一个数据源
          </el-button>
        </el-empty>
      </div>
    </el-card>

    <el-dialog v-model="datasetsDialogVisible" title="关联的数据集" width="700px">
      <el-table :data="datasets" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="数据集名称" min-width="150" />
        <el-table-column prop="row_count" label="行数" width="100" />
        <el-table-column prop="column_count" label="列数" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button link type="primary" class="glass-btn-solid" @click="goToDataset(scope.row.id)">
              <el-icon><View /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Delete, View, Edit, Collection } from '@element-plus/icons-vue'
import {
  getDataSourceList,
  testSavedConnection,
  getSourceDatasets,
  deleteDataSource,
  getDataSourceDetail
} from '@/api/datasource'

const router = useRouter()

const loading = ref(false)
const sourceList = ref([])
const datasetsDialogVisible = ref(false)
const datasets = ref([])

const loadSourceList = async () => {
  loading.value = true
  
  try {
    const res = await getDataSourceList({ page: 1, page_size: 100 })
    
    if (res.data && res.data.items) {
      sourceList.value = res.data.items.map(item => ({
        ...item,
        _testing: false,
        _connected: false,
        _datasetCount: null
      }))
      
      for (let source of sourceList.value) {
        // 确保 source.id 存在且有效
        if (source.id && !isNaN(source.id)) {
          try {
            const dsRes = await getSourceDatasets(source.id)
            source._datasetCount = dsRes.data ? dsRes.data.length : 0
          } catch {
            source._datasetCount = 0
          }
        } else {
          console.warn('[WARN] 数据源ID无效:', source)
          source._datasetCount = 0
        }
      }
    }
  } catch (error) {
    console.error('加载数据源列表失败:', error)
    ElMessage.error('加载数据源列表失败')
  } finally {
    loading.value = false
  }
}

const goToManage = (sourceId) => {
  // 如果 sourceId 是事件对象（PointerEvent），则视为没有ID
  if (sourceId && typeof sourceId === 'object' && sourceId.type) {
    // 这是点击事件，不是ID，跳转到新建页面
    router.push('/datasets/sources/manage')
  } else if (sourceId) {
    // 有ID，跳转到使用该数据源的页面
    router.push(`/datasets/sources/manage?id=${sourceId}`)
  } else {
    // 没有ID，跳转到新建页面
    router.push('/datasets/sources/manage')
  }
}

const editDataSource = (row) => {
  router.push(`/datasets/sources/manage?mode=edit&id=${row.id}`)
}

const quickTestConnection = async (row) => {
  row._testing = true
  
  try {
    const res = await testSavedConnection(row.id)
    
    if (res.data && res.data.connected) {
      row._connected = true
      ElMessage.success(`数据源「${row.name}」连接成功！`)
      
      setTimeout(() => {
        row._connected = false
      }, 3000)
    } else {
      row._connected = false
      ElMessage.error(`数据源「${row.name}」连接失败`)
    }
  } catch (error) {
    row._connected = false
    ElMessage.error('连接失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    setTimeout(() => {
      row._testing = false
    }, 500)
  }
}

const viewDatasets = async (row) => {
  // 验证 row.id
  if (!row.id || isNaN(row.id)) {
    ElMessage.error('数据源ID无效')
    console.error('[ERROR] 数据源ID无效:', row)
    return
  }
  
  try {
    const res = await getSourceDatasets(row.id)
    
    if (res.data) {
      datasets.value = res.data
      datasetsDialogVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载关联数据集失败')
  }
}

const goToDataset = (id) => {
  router.push(`/datasets/${id}`)
}

const deleteSource = async (row) => {
  try {
    await deleteDataSource(row.id)
    ElMessage.success(`数据源「${row.name}」已删除`)
    loadSourceList()
  } catch (error) {
    ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(() => {
  loadSourceList()
})
</script>

<style scoped lang="scss">
.data-source-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.connection-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.separator {
  color: #909399;
  margin: 0 2px;
}

.empty-state {
  padding: 40px 0;
}

/* 玻璃质感表格行悬浮效果 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(184, 212, 227, 0.12) !important;
  }
}

/* 标签玻璃效果 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

/* 链接玻璃效果 */
:deep(.el-link) {
  transition: all 0.2s ease;
}

/* 表格内操作按钮样式优化 - 深色字体 */
:deep(.el-table .el-button.glass-btn-solid) {
  color: #394F49 !important;
  font-weight: 600 !important;
}

/* 使用/数据集按钮 - 使用 #D5CFE1 */
:deep(.el-table .el-button--primary.glass-btn-solid) {
  background: #D5CFE1 !important;
  border-color: #D5CFE1 !important;
  box-shadow: 0 2px 8px rgba(213, 207, 225, 0.3) !important;

  &:hover {
    background: #C5BFD1 !important;
    box-shadow: 0 4px 12px rgba(213, 207, 225, 0.4) !important;
  }
}

/* 编辑按钮 - 使用 #B6A6CA */
:deep(.el-table .el-button--warning.glass-btn-solid) {
  background: #B6A6CA !important;
  border-color: #B6A6CA !important;
  box-shadow: 0 2px 8px rgba(182, 166, 202, 0.3) !important;

  &:hover {
    background: #A594BA !important;
    box-shadow: 0 4px 12px rgba(182, 166, 202, 0.4) !important;
  }
}

/* 删除按钮 - 保持红色但优化配色 */
:deep(.el-table .el-button--danger.glass-btn-solid) {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
  color: #ffffff !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3) !important;

  &:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%) !important;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4) !important;
  }
}
</style>
