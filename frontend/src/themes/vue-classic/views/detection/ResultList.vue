<template>
  <div class="result-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>识别结果历史</span>
          <el-button v-if="taskId" type="primary" link @click="showAllResults">
            查看全部结果
          </el-button>
        </div>
      </template>

      <el-empty description="请选择识别任务查看结果" v-if="!taskId">
        <el-button type="primary" @click="$router.push('/detection/tasks')">前往任务列表</el-button>
      </el-empty>

      <div v-else>
        <el-alert
          v-if="taskInfo.name"
          :title="`当前查看任务: ${taskInfo.name}`"
          type="info"
          :closable="false"
          style="margin-bottom: 15px;"
        />
        <el-table :data="results" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="task_id" label="任务ID" />
          <el-table-column prop="column_name" label="列名" />
          <el-table-column prop="rule_name" label="命中规则" />
          <el-table-column prop="matched_content" label="匹配内容" show-overflow-tooltip />
          <el-table-column prop="confidence" label="置信度">
            <template #header>
              <span>置信度</span>
              <el-tooltip
                placement="top"
                effect="light"
                popper-class="confidence-tooltip"
              >
                <template #content>
                  <div style="max-width: 300px; line-height: 1.6;">
                    <strong>置信度说明：</strong><br/>
                    表示系统对识别结果的确信程度，取值范围 0~1。<br/><br/>
                    <strong>计算公式：</strong><br/>
                    置信度 = (正则匹配精度 × 0.4) + (关键词匹配度 × 0.3) + (文本特征得分 × 0.3)<br/><br/>
                    <strong>评分维度：</strong><br/>
                    • 正则匹配精度：模式匹配的完整性和准确性<br/>
                    • 关键词匹配度：与敏感词库的匹配程度<br/>
                    • 文本特征得分：长度、格式、上下文等特征<br/><br/>
                    越接近 1 表示系统越确信该内容属于对应敏感类型。
                  </div>
                </template>
                <el-icon style="margin-left: 4px; cursor: help; color: #909399;"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <template #default="{ row }">
              <el-progress :percentage="Math.round(row.confidence * 100)" />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="识别时间" />
        </el-table>

        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          style="margin-top: 20px;"
          @change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { QuestionFilled } from '@element-plus/icons-vue'
import { getDetectionResults, getDetectionTask } from '@/api/detection'

const route = useRoute()
const router = useRouter()
const taskId = ref(route.query.task_id || null)

const loading = ref(false)
const results = ref([])
const taskInfo = ref({})
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)

const loadTaskInfo = async () => {
  if (!taskId.value) return
  try {
    const res = await getDetectionTask(taskId.value)
    taskInfo.value = res.data || {}
  } catch (e) {
    console.error(e)
  }
}

const loadData = async () => {
  if (!taskId.value) return
  loading.value = true
  try {
    const res = await getDetectionResults(taskId.value, { page: page.value, page_size: pageSize.value })
    results.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const showAllResults = () => {
  taskId.value = null
  taskInfo.value = {}
  results.value = []
  total.value = 0
}

onMounted(() => {
  if (taskId.value) {
    loadTaskInfo()
    loadData()
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
