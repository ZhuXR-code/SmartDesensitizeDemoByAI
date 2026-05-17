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
            <el-progress :percentage="row.progress" :status="row.status === 'failed' ? 'exception' : ''" />
          </template>
        </el-table-column>
        <el-table-column prop="scanned_rows" label="已扫描/总行数" width="140">
          <template #default="{ row }">
            {{ row.scanned_rows }} / {{ row.total_rows }}
          </template>
        </el-table-column>
        <el-table-column prop="found_count" label="发现敏感数" width="110" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" min-width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-space :size="4">
              <el-tooltip content="查看任务详细信息" placement="top">
                <el-button link type="primary" size="small" class="glass-btn-solid" @click="viewDetail(row)">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="跳转到脱敏任务" placement="top">
                <el-button link type="success" size="small" class="glass-btn-solid" @click="jumpToDesensitization(row)" v-if="row.status === 'completed'">
                  <el-icon><Right /></el-icon>
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
import { ElMessage } from 'element-plus'
import { View, Right } from '@element-plus/icons-vue'
import { getDetectionTasks, jumpToDesensitization as jumpApi } from '@/api/detection'

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

const jumpToDesensitization = async (row) => {
  try {
    const res = await jumpApi(row.id)
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
