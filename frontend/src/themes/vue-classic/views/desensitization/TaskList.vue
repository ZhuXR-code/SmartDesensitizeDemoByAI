<template>
  <div class="task-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>脱敏任务列表</span>
          <el-space>
            <el-tooltip :content="autoRefresh ? '自动刷新已开启' : '自动刷新已关闭'" placement="top">
              <el-switch
                v-model="autoRefresh"
                active-text="自动刷新"
                inline-prompt
                @change="toggleAutoRefresh"
              />
            </el-tooltip>
            <el-button :loading="refreshing" @click="handleManualRefresh">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
            <el-button type="primary" @click="$router.push('/desensitization/tasks/create')">
              <el-icon><Plus /></el-icon> 创建任务
            </el-button>
          </el-space>
        </div>
      </template>
      
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" />
          </template>
        </el-table-column>
        <el-table-column prop="output_mode" label="输出模式">
          <template #default="{ row }">
            <el-tag :type="row.output_mode === 'copy' ? 'success' : 'danger'">
              {{ row.output_mode === 'copy' ? '生成副本' : '覆盖原数据' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="processed_rows" label="已处理/总行数">
          <template #default="{ row }">
            {{ row.processed_rows }} / {{ row.total_rows }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="450">
          <template #default="{ row }">
            <el-space :size="8" wrap>
              <el-tooltip content="查看任务详细信息" placement="top">
                <el-button type="primary" size="small" @click="viewDetail(row)">详情</el-button>
              </el-tooltip>
              <el-tooltip content="下载脱敏后的数据副本" placement="top">
                <el-button 
                  type="success" 
                  size="small" 
                  @click="downloadFile(row)" 
                  v-if="row.status === 'completed' && (row.output_path || row.temp_file_path)"
                >
                  下载副本
                </el-button>
              </el-tooltip>
              <el-dropdown @command="(cmd) => downloadReportWithFormat(row, cmd)" style="margin-right: 4px;">
                <el-button type="warning" size="small">
                  下载报告<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="html">HTML格式</el-dropdown-item>
                    <el-dropdown-item command="markdown">Markdown格式</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-tooltip content="在线预览脱敏报告" placement="top">
                <el-button type="info" size="small" @click="previewReport(row)" style="margin-left: 4px;">
                  <el-icon><View /></el-icon>
                  预览
                </el-button>
              </el-tooltip>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 20px;"
        @change="loadData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElIcon } from 'element-plus'
import { Plus, ArrowDown, View, Refresh } from '@element-plus/icons-vue'
import { getDesensitizationTasks, downloadDesensitizedFile, generateReport, downloadReport } from '@/api/desensitization'

const router = useRouter()
const loading = ref(false)
const tasks = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const refreshing = ref(false)
const autoRefresh = ref(true)
let refreshTimer = null

const getStatusType = (status) => {
  const map = {
    'completed': 'success',
    'running': 'warning',
    'pending': 'info',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const hasRunningTasks = computed(() => {
  return tasks.value.some(t => t.status === 'running' || t.status === 'pending')
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getDesensitizationTasks({ page: page.value, page_size: pageSize.value })
    tasks.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleManualRefresh = async () => {
  refreshing.value = true
  try {
    await loadData()
    ElMessage.success('刷新成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = setInterval(async () => {
    try {
      const res = await getDesensitizationTasks({ page: page.value, page_size: pageSize.value })
      const newTasks = res.data.items || []
      const newTotal = res.data.total || 0
      
      tasks.value = tasks.value.map(oldTask => {
        const newTask = newTasks.find(t => t.id === oldTask.id)
        if (newTask) {
          return { ...oldTask, ...newTask }
        }
        return oldTask
      })
      
      const existingIds = tasks.value.map(t => t.id)
      const newItems = newTasks.filter(t => !existingIds.includes(t.id))
      if (newItems.length > 0) {
        tasks.value = [...newItems, ...tasks.value].slice(0, pageSize.value)
      }
      
      total.value = newTotal
      
      if (!hasRunningTasks.value) {
        stopAutoRefresh()
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

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    if (hasRunningTasks.value) {
      startAutoRefresh()
      ElMessage.success('已开启自动刷新（每3秒）')
    } else {
      ElMessage.info('当前没有进行中的任务，将在有新任务时自动启动')
    }
  } else {
    stopAutoRefresh()
    ElMessage.info('已停止自动刷新')
  }
}

const viewDetail = (row) => {
  router.push(`/desensitization/tasks/${row.id}`)
}

const downloadFile = async (row) => {
  try {
    const res = await downloadDesensitizedFile(row.id)
    const blob = new Blob([res])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `脱敏结果_${row.id}.csv`
    link.click()
    ElMessage.success('下载成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('下载失败')
  }
}

const downloadReportWithFormat = async (row, format) => {
  try {
    const res = await downloadReport(row.id, format)
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
    link.download = `脱敏报告_${row.id}_${Date.now()}.${extMap[format] || 'txt'}`
    link.click()
    ElMessage.success(`${format === 'markdown' ? 'Markdown' : format.toUpperCase()}报告下载成功`)
  } catch (e) {
    console.error(e)
    ElMessage.error('下载报告失败')
  }
}

const previewReport = async (row) => {
  try {
    const res = await downloadReport(row.id, 'html')
    const blob = new Blob([res], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } catch (e) {
    console.error(e)
    ElMessage.error('预览报告失败')
  }
}

onMounted(() => {
  loadData().then(() => {
    if (autoRefresh.value && hasRunningTasks.value) {
      startAutoRefresh()
    }
  })
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 修复下拉菜单按钮的重叠阴影问题 */
:deep(.el-dropdown) {
  position: relative;
  z-index: 1;
}

:deep(.el-space__item) {
  position: relative;
  display: inline-flex;
}

/* 给操作按钮添加独立间距，避免重叠 */
:deep(.el-button + .el-dropdown),
:deep(.el-dropdown + .el-button),
:deep(.el-button + .el-button) {
  margin-left: 8px !important;
}
</style>
