<template>
  <div class="task-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>识别任务列表</span>
          <el-button type="primary" @click="$router.push('/detection/tasks/create')">
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
        <el-table-column prop="dataset_name" label="数据集" min-width="150" />
        <el-table-column prop="ruleset_name" label="规则集" min-width="150" />
        <el-table-column prop="processed_rows" label="已处理/总行数" width="140">
          <template #default="{ row }">
            {{ row.processed_rows }} / {{ row.total_rows }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" min-width="240" fixed="right" align="right">
          <template #default="{ row }">
            <el-space :size="4" wrap>
              <el-tooltip content="查看任务详细信息" placement="top">
                <el-button type="primary" size="small" class="glass-btn-solid" @click="viewDetail(row)">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="跳转到脱敏任务配置" placement="top">
                <el-button
                  type="success"
                  size="small"
                  class="glass-btn-solid"
                  @click="handleJump(row)"
                  v-if="row.status === 'completed'"
                >
                  <el-icon><Connection /></el-icon> 去脱敏
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElIcon } from 'element-plus'
import { Plus, View, Connection } from '@element-plus/icons-vue'
import { getDetectionTasks, jumpToDesensitization } from '@/api/detection'

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
    const res = await getDetectionTasks({ page: page.value, page_size: pageSize.value })
    tasks.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const viewDetail = (row) => {
  router.push(`/detection/tasks/${row.id}`)
}

const handleJump = async (row) => {
  try {
    const res = await jumpToDesensitization(row.id)
    const data = res.data
    router.push({
      path: '/desensitization/tasks/create',
      query: {
        dataset_id: data.dataset_id,
        detection_task_id: data.detection_task_id
      }
    })
  } catch (e) {
    console.error(e)
    ElMessage.error('跳转失败')
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

/* 玻璃质感表格行悬浮效果 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(184, 212, 227, 0.12) !important;
  }
}

/* 进度条玻璃效果 */
:deep(.el-progress-bar__outer) {
  background: rgba(0, 0, 0, 0.05) !important;
}

/* 标签玻璃效果 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
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

/* 表格内操作按钮样式优化 - 深色字体 */
:deep(.el-table .el-button.glass-btn-solid) {
  color: #394F49 !important;
  font-weight: 600 !important;
}

/* 去脱敏按钮 - 使用 #B6A6CA */
:deep(.el-table .el-button--success.glass-btn-solid) {
  background: #B6A6CA !important;
  border-color: #B6A6CA !important;
  color: #394F49 !important;
  box-shadow: 0 2px 8px rgba(182, 166, 202, 0.3) !important;

  &:hover {
    background: #A594BA !important;
    box-shadow: 0 4px 12px rgba(182, 166, 202, 0.4) !important;
  }
}

/* 报告按钮 - 使用 #D4BEBE */
:deep(.el-table .el-button--warning.glass-btn-solid) {
  background: #D4BEBE !important;
  border-color: #D4BEBE !important;
  box-shadow: 0 2px 8px rgba(212, 190, 190, 0.3) !important;

  &:hover {
    background: #C4AEAE !important;
    box-shadow: 0 4px 12px rgba(212, 190, 190, 0.4) !important;
  }
}

/* 详情按钮 - 使用 #D5CFE1 */
:deep(.el-table .el-button--primary.glass-btn-solid) {
  background: #D5CFE1 !important;
  border-color: #D5CFE1 !important;
  color: #394F49 !important;
  box-shadow: 0 2px 8px rgba(213, 207, 225, 0.3) !important;

  &:hover {
    background: #C5BFD1 !important;
    box-shadow: 0 4px 12px rgba(213, 207, 225, 0.4) !important;
  }
}
</style>
