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
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="row.status === 'failed' ? 'exception' : ''" />
          </template>
        </el-table-column>
        <el-table-column prop="scanned_rows" label="已扫描/总行数">
          <template #default="{ row }">
            {{ row.scanned_rows }} / {{ row.total_rows }}
          </template>
        </el-table-column>
        <el-table-column prop="found_count" label="发现敏感数" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-space :size="4">
              <el-tooltip content="查看任务详细信息" placement="top">
                <el-button type="primary" size="small" @click="viewDetail(row)">
                  <el-icon><View /></el-icon> 详情
                </el-button>
              </el-tooltip>
              <el-tooltip content="跳转到脱敏任务配置" placement="top">
                <el-button type="success" size="small" @click="jumpToDesensitization(row)" v-if="row.status === 'completed'">
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
import { ElMessage } from 'element-plus'
import { View, Connection, Plus } from '@element-plus/icons-vue'
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

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
