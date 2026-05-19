<template>
  <div class="task-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>任务详情: {{ task.name }}</span>
          <div>
            <el-button type="primary" @click="loadTask" :loading="loading" v-if="task.status === 'running' || task.status === 'pending'">
              <el-icon><Refresh /></el-icon>
              手动刷新
            </el-button>
            <el-button type="success" @click="jumpToDesensitization" v-if="task.status === 'completed'">
              <el-icon><Connection /></el-icon>
              一键跳转脱敏
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 核心指标卡片 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card shadow="hover" class="metric-card">
            <div class="metric-content">
              <div class="metric-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon size="30"><DataLine /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ task.total_rows || 0 }}</div>
                <div class="metric-label">总数据行数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="metric-card">
            <div class="metric-content">
              <div class="metric-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon size="30"><Warning /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value" style="color: #f5576c;">{{ task.found_count || 0 }}</div>
                <div class="metric-label">敏感信息条数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="metric-card">
            <div class="metric-content">
              <div class="metric-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <el-icon size="30"><Odometer /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ task.sensitivity_rate || 0 }}%</div>
                <div class="metric-label">敏感数据比例</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="metric-card">
            <div class="metric-content">
              <div class="metric-icon" :style="{ background: riskLevelColor }">
                <el-icon size="30"><TrendCharts /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value" :style="{ color: riskLevelTextColor }">{{ riskLevelText }}</div>
                <div class="metric-label">风险等级</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 详细信息 -->
      <el-descriptions :column="3" border>
        <el-descriptions-item label="任务ID">{{ task.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(task.status)" effect="dark">{{ getStatusText(task.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="数据集名称">
          <el-link type="primary" @click="viewDataset">{{ task.dataset_name || '-' }}</el-link>
        </el-descriptions-item>
        <el-descriptions-item label="使用规则集">
          <el-link v-if="task.rule_set_info" type="primary" @click="viewRuleSet">
            {{ task.rule_set_info.name }} ({{ task.rule_set_info.rule_count }}个规则)
          </el-link>
          <span v-else>全部内置规则</span>
        </el-descriptions-item>
        <el-descriptions-item label="扫描速度">
          {{ task.scan_speed || 0 }} 行/秒
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ formatDuration(task.duration_seconds) }}
        </el-descriptions-item>
        <el-descriptions-item label="开始时间" :span="3">
          {{ task.started_at ? formatDateTime(task.started_at) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="完成时间" :span="3">
          {{ task.completed_at ? formatDateTime(task.completed_at) : '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <!-- 实时日志显示 -->
      <div v-if="task.status === 'running' || task.status === 'pending'" style="margin-top: 20px;">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <div>
                <span>🔍 识别进行中...</span>
                <span style="margin-left: 20px;">进度: {{ task.progress || 0 }}%</span>
                <span style="margin-left: 20px;">已扫描: {{ task.scanned_rows || 0 }} / {{ task.total_rows || 0 }} 行</span>
              </div>
              <div v-if="task.found_count > 0" style="color: #E6A23C; font-weight: bold;">
                ⚠️ 已发现 {{ task.found_count }} 条敏感信息
              </div>
            </div>
          </template>
        </el-alert>
      </div>
      
      <!-- 语言分布图表 -->
      <div v-if="task.language_distribution && Object.keys(task.language_distribution).length > 0" style="margin-top: 20px;">
        <h4>🌍 语言分布统计</h4>
        <el-row :gutter="20">
          <el-col :span="4" v-for="(count, lang) in task.language_distribution" :key="lang">
            <el-statistic :title="languageMap[lang] || lang" :value="count">
              <template #suffix>
                <span style="font-size: 12px; color: #909399;">条</span>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
      </div>
      
      <!-- 识别结果表格 -->
      <div style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <h4 style="margin: 0;">📋 识别结果明细</h4>
          <el-tag v-if="results.length > 0" type="info">
            共 {{ total }} 条记录
          </el-tag>
        </div>
        <el-table :data="results" size="small" style="margin-top: 10px;" stripe>
          <el-table-column prop="row_index" label="行号" width="80" align="center" />
          <el-table-column prop="column_name" label="列名" min-width="120" />
          <el-table-column prop="detected_language" label="检测语言" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ languageMap[row.detected_language] || row.detected_language }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="rule_name" label="命中规则" min-width="150" />
          <el-table-column prop="matched_content" label="匹配内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="confidence" label="置信度" width="150" align="center">
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
              <el-progress 
                :percentage="Math.round(row.confidence * 100)" 
                :color="getConfidenceColor(row.confidence)"
                :stroke-width="8"
              />
            </template>
          </el-table-column>
          <el-table-column prop="desensitization_suggestion" label="脱敏建议" min-width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="warning" effect="plain">{{ row.desensitization_suggestion }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          :page-sizes="[20, 50, 100, 200]"
          style="margin-top: 10px; justify-content: flex-end;"
          @change="loadResults"
        />
      </div>
    </el-card>
    
    <!-- 规则集详情对话框 -->
    <el-dialog v-model="showRuleSetDialog" title="规则集详情" width="900px">
      <div v-if="currentRuleSet">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="规则集名称">{{ currentRuleSet.name }}</el-descriptions-item>
          <el-descriptions-item label="包含规则数">
            <el-tag type="info">{{ currentRuleSet.rules?.length || 0 }} 个规则</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentRuleSet.description || '无' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <h4>规则列表</h4>
        <el-table :data="currentRuleSet.rules || []" max-height="400" stripe>
          <el-table-column prop="name" label="规则名称" min-width="150" />
          <el-table-column prop="language" label="语言" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ languageMap[row.language] || row.language }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="rule_type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="row.rule_type === 'regex' ? 'primary' : 'success'">
                {{ row.rule_type === 'regex' ? '正则' : '关键词' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="example" label="示例" min-width="200" show-overflow-tooltip />
          <el-table-column prop="is_builtin" label="来源" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="row.is_builtin ? 'info' : 'warning'">
                {{ row.is_builtin ? '内置' : '自定义' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showRuleSetDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, QuestionFilled, Connection, DataLine, Warning, Odometer, TrendCharts } from '@element-plus/icons-vue'
import { getDetectionTask, getDetectionResults, jumpToDesensitization as jumpApi, getRuleSetDetail } from '@/api/detection'

const route = useRoute()
const router = useRouter()
const taskId = route.params.id

const loading = ref(false)
const task = ref({})
const results = ref([])
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)

// 规则集详情对话框
const showRuleSetDialog = ref(false)
const currentRuleSet = ref(null)

// 定时器ID
let pollTimer = null
let logPollTimer = null

const languageMap = {
  zh: '中文',
  en: '英语',
  ja: '日语',
  ko: '韩语',
  fr: '法语',
  de: '德语'
}

// 风险等级文本
const riskLevelText = computed(() => {
  const map = {
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险'
  }
  return map[task.value.risk_level] || '未知'
})

// 风险等级颜色
const riskLevelColor = computed(() => {
  const map = {
    'low': 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)',
    'medium': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'high': 'linear-gradient(135deg, #ff0844 0%, #ffb199 100%)'
  }
  return map[task.value.risk_level] || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
})

// 风险等级文字颜色
const riskLevelTextColor = computed(() => {
  const map = {
    'low': '#52c41a',
    'medium': '#faad14',
    'high': '#f5222d'
  }
  return map[task.value.risk_level] || '#666'
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

const getStatusText = (status) => {
  const map = {
    'completed': '已完成',
    'running': '进行中',
    'pending': '等待中',
    'failed': '失败'
  }
  return map[status] || status
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  if (status === 'running' || status === 'pending') return undefined
  return undefined
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.9) return '#67c23a'
  if (confidence >= 0.7) return '#409eff'
  if (confidence >= 0.5) return '#e6a23c'
  return '#f56c6c'
}

const formatDuration = (seconds) => {
  if (!seconds) return '0.000秒'
  if (seconds < 60) return `${seconds.toFixed(3)}秒`
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}分${secs.toFixed(3)}秒`
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '-'
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const viewDataset = () => {
  if (task.value.dataset_id) {
    router.push(`/datasets/${task.value.dataset_id}`)
  }
}

const viewRuleSet = async () => {
  if (!task.value.rule_set_id) return
  
  try {
    const res = await getRuleSetDetail(task.value.rule_set_id)
    currentRuleSet.value = res.data
    showRuleSetDialog.value = true
  } catch (error) {
    ElMessage.error('加载规则集详情失败')
  }
}

const loadTask = async () => {
  try {
    const res = await getDetectionTask(taskId)
    const oldStatus = task.value.status
    task.value = res.data || {}
    
    // 如果状态发生变化，给出提示
    if (oldStatus && oldStatus !== task.value.status) {
      if (task.value.status === 'completed') {
        ElMessage.success('识别任务已完成！')
        stopPolling()
      } else if (task.value.status === 'failed') {
        ElMessage.error('识别任务失败！')
        stopPolling()
      }
    }
    
    // 只有在任务进行中时才加载结果
    if (task.value.status === 'completed' || task.value.status === 'failed') {
      await loadResults()
    }
  } catch (e) {
    console.error('加载任务信息失败:', e)
  }
}

const loadResults = async () => {
  try {
    const res = await getDetectionResults(taskId, { page: page.value, page_size: pageSize.value })
    results.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('加载识别结果失败:', e)
  }
}

// 开始轮询
const startPolling = () => {
  // 每2秒轮询一次任务状态和进度
  pollTimer = setInterval(() => {
    loadTask()
  }, 2000)
}

// 停止轮询
const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  if (logPollTimer) {
    clearInterval(logPollTimer)
    logPollTimer = null
  }
}

const jumpToDesensitization = async () => {
  try {
    const res = await jumpApi(taskId)
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
  loading.value = true
  loadTask().then(() => {
    loading.value = false
    // 如果任务还在进行中，启动轮询
    if (task.value.status === 'running' || task.value.status === 'pending') {
      startPolling()
    }
  })
})

onUnmounted(() => {
  // 组件卸载时清除定时器
  stopPolling()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.metric-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

h4 {
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
}
</style>
