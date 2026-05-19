<template>
  <div class="task-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>脱敏任务详情: {{ task.name }}</span>
          <div class="header-actions">
            <el-button 
              type="primary" 
              :icon="RefreshIcon"
              @click="handleManualRefresh"
              :loading="refreshing"
            >
              刷新
            </el-button>
            <el-button 
              :type="autoRefresh ? 'success' : 'info'"
              @click="toggleAutoRefresh"
            >
              {{ autoRefresh ? '停止自动刷新' : '开启自动刷新' }}
            </el-button>
            <el-button 
              type="success" 
              @click="downloadFile" 
              v-if="(task.output_path || task.temp_file_path) && task.status === 'completed'"
            >
              下载副本
            </el-button>
            <el-dropdown @command="downloadReportWithFormat">
              <el-button type="warning">
                下载报告<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="html">HTML格式</el-dropdown-item>
                  <el-dropdown-item command="markdown">Markdown格式</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button type="info" @click="previewReport">
              <el-icon><View /></el-icon>
              在线预览
            </el-button>
          </div>
        </div>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="ID">{{ task.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(task.status)">{{ task.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="进度">
          <el-progress :percentage="task.progress || 0" />
        </el-descriptions-item>
        <el-descriptions-item label="已处理">
          {{ task.processed_rows }} / {{ task.total_rows }} 行
        </el-descriptions-item>
        <el-descriptions-item label="输出模式">
          <el-tag :type="task.output_mode === 'copy' ? 'success' : 'danger'">
            {{ task.output_mode === 'copy' ? '生成副本' : '覆盖原数据' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ (task.duration_seconds || 0).toFixed(3) }} 秒
        </el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px;">
        <h4>脱敏结果示例</h4>
        <el-table :data="results" size="small" style="margin-top: 10px;">
          <el-table-column prop="row_index" label="行号" width="80" />
          <el-table-column prop="column_name" label="列名" />
          <el-table-column prop="original_value" label="原始值" show-overflow-tooltip />
          <el-table-column prop="desensitized_value" label="脱敏后" show-overflow-tooltip />
          <el-table-column prop="rule_name" label="应用规则" />
        </el-table>
        
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          style="margin-top: 10px;"
          @change="loadResults"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, ArrowDown, View } from '@element-plus/icons-vue'
import { getDesensitizationTask, getDesensitizationResults, downloadDesensitizedFile, downloadReport } from '@/api/desensitization'

const route = useRoute()
const taskId = route.params.id

const loading = ref(false)
const refreshing = ref(false)
const task = ref({})
const results = ref([])
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const autoRefresh = ref(false)
let refreshTimer = null

const RefreshIcon = Refresh

const getStatusType = (status) => {
  const map = {
    'completed': 'success',
    'running': 'warning',
    'pending': 'info',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const loadTask = async () => {
  loading.value = true
  try {
    const res = await getDesensitizationTask(taskId)
    task.value = res.data || {}
    await loadResults()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleManualRefresh = async () => {
  refreshing.value = true
  try {
    await loadTask()
    ElMessage.success('刷新成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
    ElMessage.success('已开启自动刷新（每3秒）')
  } else {
    stopAutoRefresh()
    ElMessage.info('已停止自动刷新')
  }
}

const startAutoRefresh = () => {
  // 清除旧的定时器
  stopAutoRefresh()
  // 设置新的定时器，每3秒刷新一次
  refreshTimer = setInterval(async () => {
    try {
      const res = await getDesensitizationTask(taskId)
      const newTask = res.data || {}
      
      // 检查任务状态或进度是否变化
      const statusChanged = newTask.status !== task.value.status
      const progressChanged = newTask.progress !== task.value.progress
      const processedRowsChanged = newTask.processed_rows !== task.value.processed_rows
      
      // 更新任务基本信息
      task.value = {
        ...task.value,
        status: newTask.status,
        progress: newTask.progress,
        processed_rows: newTask.processed_rows,
        total_rows: newTask.total_rows,
        duration_seconds: newTask.duration_seconds
      }
      
      // 如果任务状态、进度或处理行数发生变化，重新加载结果
      if (statusChanged || progressChanged || processedRowsChanged) {
        await loadResults()
      }
      
      // 如果任务刚完成，显示提示
      if (newTask.status === 'completed' && task.value.status !== 'completed') {
        ElMessage.success('任务已完成！')
      }
    } catch (e) {
      console.error('自动刷新失败:', e)
    }
  }, 3000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const loadResults = async () => {
  try {
    const res = await getDesensitizationResults(taskId, { page: page.value, page_size: pageSize.value })
    results.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  }
}

const downloadFile = async () => {
  try {
    const res = await downloadDesensitizedFile(taskId)
    const blob = new Blob([res])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `脱敏结果_${taskId}.csv`
    link.click()
    ElMessage.success('下载成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('下载失败')
  }
}

const downloadReportWithFormat = async (format) => {
  try {
    const res = await downloadReport(taskId, format)
    const mimeTypes = {
      'pdf': 'application/pdf',
      'html': 'text/html',
      'markdown': 'text/markdown'
    }
    const extMap = {
      'pdf': 'pdf',
      'html': 'html',
      'markdown': 'md'
    }
    const blob = new Blob([res], { type: mimeTypes[format] || 'text/plain' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `脱敏报告_${taskId}_${Date.now()}.${extMap[format] || 'txt'}`
    link.click()
    ElMessage.success(`${format === 'markdown' ? 'Markdown' : format.toUpperCase()}报告下载成功`)
  } catch (e) {
    console.error(e)
    ElMessage.error(`下载报告失败`)
  }
}

const previewReport = async () => {
  try {
    // 先尝试获取HTML格式用于预览
    const res = await downloadReport(taskId, 'html')
    const blob = new Blob([res], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } catch (e) {
    console.error(e)
    ElMessage.error('预览报告失败')
  }
}

onMounted(() => {
  loadTask()
})

onUnmounted(() => {
  // 组件卸载时清除定时器
  stopAutoRefresh()
})
</script>

<style scoped lang="scss">
.task-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 表格行悬浮效果 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(184, 212, 227, 0.12) !important;
  }
}

/* 描述列表玻璃效果 */
:deep(.el-descriptions__body) {
  background: rgba(255, 255, 255, 0.5) !important;
  backdrop-filter: blur(8px) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(255, 255, 255, 0.6) !important;
}

/* 进度条玻璃效果 */
:deep(.el-progress-bar__outer) {
  background: rgba(0, 0, 0, 0.05) !important;
}

/* 标签玻璃效果 - 统一绿色为 #668F80 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

:deep(.el-tag--success) {
  background-color: rgba(102, 143, 128, 0.1) !important;
  border-color: rgba(102, 143, 128, 0.4) !important;
  color: #668F80 !important;
}

/* 全局成功色文字替换 */
.success-text {
  color: #668F80 !important;
}
</style>
