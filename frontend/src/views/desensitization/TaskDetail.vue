<template>
  <div class="task-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ isAiTask ? 'AI脱敏任务详情' : '脱敏任务详情' }}: {{ task.name }}</span>
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
              v-if="task.status === 'completed' && (task.output_path || task.temp_file_path || task.output_file_path || task.output_file_pure_path)"
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
        <el-descriptions-item label="模式">
          <el-tag v-if="task.mode" :type="task.mode === 'mask' ? 'primary' : 'warning'" size="small">
            {{ task.mode === 'mask' ? '定长遮盖' : '关联仿真' }}
          </el-tag>
          <el-tag v-else :type="task.output_mode === 'copy' ? 'success' : 'danger'" size="small">
            {{ task.output_mode === 'copy' ? '生成副本' : '覆盖原数据' }}
          </el-tag>
        </el-descriptions-item>
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
        <h4>脱敏结果详情</h4>
        <el-table :data="results" size="small" style="margin-top: 10px;">
          <el-table-column prop="row_index" label="行号" width="80" />
          <el-table-column prop="column_name" label="列名" />
          <el-table-column prop="original_value" label="原始值" show-overflow-tooltip />
          <el-table-column prop="desensitized_value" label="脱敏后" show-overflow-tooltip>
            <template #default="{ row }">
              <span style="color: #e6a23c; font-weight: 500;">{{ row.desensitized_value }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="ai_original_is_sensitive" label="AI识别" width="90">
            <template #default="{ row }">
              <el-tag :type="row.ai_original_is_sensitive ? 'danger' : 'success'" size="small">
                {{ row.ai_original_is_sensitive ? '敏感' : '非敏感' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="review_status" label="复核状态" width="90">
            <template #default="{ row }">
              <el-tag v-if="row.review_status === 'reviewed'" :type="row.review_result ? 'danger' : 'success'" size="small">
                {{ row.review_result ? '已复核(敏感)' : '已复核(非敏)' }}
              </el-tag>
              <el-tag v-else type="info" size="small">未复核</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="method" label="方法" width="90">
            <template #default="{ row }">
              <el-tag :type="row.method === 'mask' ? 'primary' : 'warning'" size="small">
                {{ row.method === 'mask' ? '遮盖' : '仿真' }}
              </el-tag>
            </template>
          </el-table-column>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, ArrowDown, View } from '@element-plus/icons-vue'
import { getDesensitizationTask, getDesensitizationResults, downloadDesensitizedFile, downloadReport } from '@/api/desensitization'
import { getAiDesensitizationTaskDetail, generateDesensitizationHtmlReport, generateDesensitizationMarkdownReport } from '@/api/ai'

const route = useRoute()
const router = useRouter()
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

const isAiTask = computed(() => {
  return route.path.includes('/ai/desensitization/tasks/')
})

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
    let res
    if (isAiTask.value) {
      res = await getAiDesensitizationTaskDetail(taskId)
    } else {
      res = await getDesensitizationTask(taskId)
    }
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
      let res
      if (isAiTask.value) {
        res = await getAiDesensitizationTaskDetail(taskId)
      } else {
        res = await getDesensitizationTask(taskId)
      }
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
    let res
    if (isAiTask.value) {
      res = await getAiDesensitizationTaskDetail(taskId)
      results.value = res.data.results || []
      total.value = res.data.results?.length || 0
    } else {
      res = await getDesensitizationResults(taskId, { page: page.value, page_size: pageSize.value })
      results.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch (e) {
    console.error(e)
  }
}

const downloadFile = async () => {
  try {
    let res
    if (isAiTask.value) {
      // AI脱敏任务的下载逻辑需要根据实际API调整
      res = await downloadDesensitizedFile(taskId)
    } else {
      res = await downloadDesensitizedFile(taskId)
    }
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
    let res
    if (isAiTask.value) {
      if (format === 'html') {
        res = await generateDesensitizationHtmlReport(taskId)
      } else if (format === 'markdown') {
        res = await generateDesensitizationMarkdownReport(taskId)
      }
    } else {
      res = await downloadReport(taskId, format)
    }
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
    let res
    if (isAiTask.value) {
      res = await generateDesensitizationHtmlReport(taskId)
    } else {
      // 先尝试获取HTML格式用于预览
      res = await downloadReport(taskId, 'html')
    }
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

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>
