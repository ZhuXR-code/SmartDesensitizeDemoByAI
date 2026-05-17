<template>
  <div class="task-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>脱敏任务列表</span>
          <el-button type="primary" @click="$router.push('/desensitization/tasks/create')">
            <el-icon><Plus /></el-icon> 创建任务
          </el-button>
        </div>
      </template>
      
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" min-width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" />
          </template>
        </el-table-column>
        <el-table-column prop="output_mode" label="输出模式" width="120">
          <template #default="{ row }">
            <el-tag :type="row.output_mode === 'copy' ? 'success' : 'danger'">
              {{ row.output_mode === 'copy' ? '生成副本' : '覆盖原数据' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="processed_rows" label="已处理/总行数" width="140">
          <template #default="{ row }">
            {{ row.processed_rows }} / {{ row.total_rows }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" min-width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-space :size="4" wrap>
              <el-tooltip content="查看任务详细信息" placement="top">
                <el-button link type="primary" size="small" class="glass-btn-solid" @click="viewDetail(row)">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="下载脱敏后文件" placement="top">
                <el-button
                  link
                  type="success"
                  size="small"
                  class="glass-btn-solid"
                  @click="downloadFile(row)"
                  v-if="row.status === 'completed' && (row.output_path || row.temp_file_path)"
                >
                  <el-icon><Download /></el-icon>
                </el-button>
              </el-tooltip>
              <el-dropdown @command="(cmd) => handleReportCommand(row, cmd)">
                <el-button link type="warning" size="small" class="glass-btn-solid">
                  <el-icon><Document /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="preview">
                      <el-icon><View /></el-icon>预览报告
                    </el-dropdown-item>
                    <el-dropdown-item divided command="html">
                      <el-icon><Document /></el-icon>下载HTML格式
                    </el-dropdown-item>
                    <el-dropdown-item command="markdown">
                      <el-icon><DocumentCopy /></el-icon>下载Markdown格式
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElIcon } from 'element-plus'
import { Plus, ArrowDown, View, Document, DocumentCopy, Download } from '@element-plus/icons-vue'
import { getDesensitizationTasks, downloadDesensitizedFile, generateReport, downloadReport } from '@/api/desensitization'

const router = useRouter()
const loading = ref(false)
const tasks = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const getStatusType = (status) => {
  const map = {
    'completed': 'success',
    'running': 'warning',
    'pending': 'info',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

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

const handleReportCommand = async (row, cmd) => {
  if (cmd === 'preview') {
    try {
      const res = await downloadReport(row.id, 'html')
      const blob = new Blob([res], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank')
    } catch (e) {
      console.error(e)
      ElMessage.error('预览报告失败')
    }
  } else {
    await downloadReportWithFormat(row, cmd)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.task-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 玻璃质感表格行悬浮效果 - design02 色系 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(244, 253, 175, 0.08) !important;
  }
}

/* 进度条玻璃效果 - design02 色系 */
:deep(.el-progress-bar__outer) {
  background: rgba(0, 0, 0, 0.15) !important;
}

/* 标签玻璃效果 - design02 色系 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(244, 253, 175, 0.2) !important;
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

/* 表格内操作按钮去除悬浮位移和阴影 */
:deep(.el-table .el-button) {
  box-shadow: none !important;

  &:hover {
    transform: none !important;
    box-shadow: none !important;
  }
}

/* 下拉菜单内的按钮也去除阴影 */
:deep(.el-dropdown .el-button) {
  box-shadow: none !important;

  &:hover {
    transform: none !important;
    box-shadow: none !important;
  }
}

/* 玻璃按钮效果 - design02 色系 */
.glass-btn-solid {
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.2);
  transition: all 0.2s ease;

  &:hover {
    background: rgba(244, 253, 175, 0.15);
    border-color: rgba(244, 253, 175, 0.4);
  }
}
</style>
