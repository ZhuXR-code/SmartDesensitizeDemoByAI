<template>
  <div class="dashboard">
    <!-- 欢迎语单独一行 -->
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎使用敏感信息智能脱敏平台</h1>
      <p class="welcome-subtitle">全方位保护数据安全，智能识别与脱敏敏感信息</p>
    </div>

    <!-- 平台亮点单独一行 -->
    <el-row class="section">
      <el-col :span="24">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span class="section-title">平台核心亮点</span>
              <el-tag type="warning" size="small" effect="light">行业领先</el-tag>
            </div>
          </template>
          <div class="highlights-grid">
            <div
              v-for="(item, index) in highlights"
              :key="index"
              class="highlight-item"
            >
              <div class="highlight-icon" :style="{ background: item.gradient }">
                <el-icon size="20"><component :is="item.icon" /></el-icon>
              </div>
              <div class="highlight-body">
                <div class="highlight-title">{{ item.title }}</div>
                <div class="highlight-desc">{{ item.description }}</div>
                <div class="highlight-tags">
                  <el-tag
                    v-for="(tag, tidx) in item.tags"
                    :key="tidx"
                    :type="tag.type"
                    size="small"
                    effect="plain"
                  >
                    {{ tag.text }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row class="section">
      <el-col :span="24">
        <div class="quick-actions">
          <div
            v-for="(action, index) in quickActions"
            :key="index"
            class="quick-action-item"
            @click="$router.push(action.route)"
          >
            <div class="quick-action-icon" :style="{ background: action.gradient }">
              <el-icon size="20"><component :is="action.icon" /></el-icon>
            </div>
            <span class="quick-action-title">{{ action.title }}</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 平台操作流程单独一行 -->
    <el-row class="section">
      <el-col :span="24">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span class="section-title">平台操作流程</span>
              <el-tag type="success" size="small" effect="light">快速开始</el-tag>
            </div>
          </template>
          <div class="workflow-steps">
            <div
              v-for="(step, index) in workflowSteps"
              :key="index"
              class="workflow-step"
              @click="handleWorkflowClick(step)"
            >
              <div class="step-badge" :style="{ background: step.color }">
                <el-icon size="16"><component :is="step.icon" /></el-icon>
              </div>
              <div class="step-info">
                <div class="step-title">{{ step.title }}</div>
                <div class="step-desc">{{ step.description }}</div>
              </div>
              <el-icon v-if="index < workflowSteps.length - 1" class="step-arrow" size="16"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 核心指标 + 最近任务同一行 -->
    <el-row :gutter="16" class="section">
      <el-col :xs="24" :md="10">
        <el-card shadow="never" class="section-card stats-card">
          <template #header>
            <div class="section-header">
              <span class="section-title">平台数据概览</span>
              <el-tag type="info" size="small" effect="light">实时统计</el-tag>
            </div>
          </template>
          <div class="stats-grid">
            <div class="stat-box" @click="$router.push('/datasets')">
              <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon size="24"><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_datasets || 0 }}</div>
                <div class="stat-label">数据集</div>
              </div>
            </div>
            <div class="stat-box" @click="$router.push('/detection/tasks')">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon size="24"><Search /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_detection_tasks || 0 }}</div>
                <div class="stat-label">识别任务</div>
              </div>
            </div>
            <div class="stat-box" @click="$router.push('/desensitization/tasks')">
              <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <el-icon size="24"><Lock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_desensitization_tasks || 0 }}</div>
                <div class="stat-label">脱敏任务</div>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <el-icon size="24"><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value" style="color: #f5576c;">{{ stats.total_sensitive_found || 0 }}</div>
                <div class="stat-label">敏感发现</div>
              </div>
            </div>
          </div>
          <div class="chart-section">
            <div class="chart-header">
              <span class="chart-name">敏感类型分布</span>
              <span class="chart-total">共 {{ sensitiveDistribution.reduce((sum, item) => sum + item.count, 0) }} 条</span>
            </div>
            <div class="chart-body">
              <div v-if="sensitiveDistribution.length > 0" ref="chartRef" class="chart-container"></div>
              <div v-if="sensitiveDistribution.length > 0" class="chart-legend">
                <div
                  v-for="(item, index) in sensitiveDistribution"
                  :key="index"
                  class="legend-item"
                  @mouseenter="highlightChartSlice(index)"
                  @mouseleave="unhighlightChartSlice()"
                >
                  <span class="legend-dot" :style="{ background: chartColors[index % chartColors.length] }"></span>
                  <span class="legend-name" :title="item.name">{{ item.name }}</span>
                  <span class="legend-value">{{ item.count }}</span>
                  <span class="legend-percent">{{ ((item.count / sensitiveDistribution.reduce((sum, i) => sum + i.count, 0)) * 100).toFixed(1) }}%</span>
                </div>
              </div>
              <el-empty v-if="sensitiveDistribution.length === 0" description="暂无数据" :image-size="60" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="14">
        <el-card shadow="never" class="section-card tasks-card">
          <template #header>
            <div class="section-header">
              <span class="section-title">最近任务</span>
              <el-tag type="success" size="small" effect="light">实时更新</el-tag>
            </div>
          </template>
          <el-tabs v-model="activeTab" class="task-tabs">
            <el-tab-pane label="识别任务" name="detection">
              <div class="task-list">
                <div v-if="recentDetectionTasks.length === 0" class="task-empty">
                  <el-empty description="暂无识别任务" :image-size="60" />
                </div>
                <div
                  v-for="task in recentDetectionTasks"
                  :key="task.id"
                  class="task-item"
                  @click="$router.push('/detection/tasks/' + task.id)"
                >
                  <div class="task-dot" :class="getStatusType(task.status)"></div>
                  <div class="task-main">
                    <div class="task-name" :title="task.name">{{ task.name }}</div>
                    <div class="task-meta">
                      <el-tag :type="getStatusType(task.status)" effect="light" size="small">
                        {{ getStatusText(task.status) }}
                      </el-tag>
                      <span class="task-time">{{ formatTime(task.created_at) }}</span>
                    </div>
                  </div>
                  <div class="task-side">
                    <el-tag v-if="task.found_count > 0" type="warning" effect="plain" size="small">
                      {{ task.found_count }}
                    </el-tag>
                    <span v-else class="task-count-zero">0</span>
                    <el-progress
                      :percentage="task.progress || 0"
                      :stroke-width="4"
                      :show-text="false"
                      class="task-progress"
                    />
                  </div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="脱敏任务" name="desensitization">
              <div class="task-list">
                <div v-if="recentDesensitizationTasks.length === 0" class="task-empty">
                  <el-empty description="暂无脱敏任务" :image-size="60" />
                </div>
                <div
                  v-for="task in recentDesensitizationTasks"
                  :key="task.id"
                  class="task-item"
                  @click="$router.push('/desensitization/tasks/' + task.id)"
                >
                  <div class="task-dot" :class="getStatusType(task.status)"></div>
                  <div class="task-main">
                    <div class="task-name" :title="task.name">{{ task.name }}</div>
                    <div class="task-meta">
                      <el-tag :type="getStatusType(task.status)" effect="light" size="small">
                        {{ getStatusText(task.status) }}
                      </el-tag>
                      <span class="task-time">{{ formatTime(task.created_at) }}</span>
                    </div>
                  </div>
                  <div class="task-side">
                    <span class="task-rows">{{ task.processed_rows || 0 }} 行</span>
                    <el-progress
                      :percentage="task.progress || 0"
                      :stroke-width="4"
                      :show-text="false"
                      class="task-progress"
                    />
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Document, Search, Lock, Warning, Upload, DocumentChecked,
  MapLocation, Connection, View, Cpu, Key, TrendCharts,
  ArrowRight, DataAnalysis, Setting, Tickets, ChatDotRound
} from '@element-plus/icons-vue'
import { getDashboardStats } from '@/api/dashboard'

const router = useRouter()

const stats = ref({})
const recentDetectionTasks = ref([])
const recentDesensitizationTasks = ref([])
const sensitiveDistribution = ref([])
const chartRef = ref(null)
const chartInstance = ref(null)
const activeTab = ref('detection')

const chartColors = ['#667eea', '#f5576c', '#4facfe', '#fa709a', '#84fab0', '#fccb90', '#e0c3fc', '#8ec5fc']

const highlightChartSlice = (index) => {
  if (chartInstance.value) {
    chartInstance.value.dispatchAction({ type: 'highlight', seriesIndex: 0, dataIndex: index })
    chartInstance.value.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: index })
  }
}

const unhighlightChartSlice = () => {
  if (chartInstance.value) {
    chartInstance.value.dispatchAction({ type: 'downplay', seriesIndex: 0 })
    chartInstance.value.dispatchAction({ type: 'hideTip' })
  }
}

const quickActions = [
  {
    title: '导入数据',
    icon: 'Upload',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    route: '/datasets/upload'
  },
  {
    title: '创建识别',
    icon: 'Search',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    route: '/detection/tasks/create'
  },
  {
    title: '创建脱敏',
    icon: 'Lock',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    route: '/desensitization/tasks/create'
  },
  {
    title: '规则管理',
    icon: 'Setting',
    gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    route: '/desensitization/rules'
  },
  {
    title: '运营报表',
    icon: 'TrendCharts',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    route: '/report/platform'
  },
  {
    title: '用户手册',
    icon: 'DocumentChecked',
    gradient: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
    route: '/help/manual'
  }
]

const workflowSteps = [
  {
    title: '导入数据',
    description: '上传Excel/CSV或连接数据库',
    color: '#667eea',
    icon: 'Upload',
    route: '/datasets/upload'
  },
  {
    title: '识别敏感数据',
    description: '智能扫描发现敏感信息',
    color: '#f5576c',
    icon: 'Search',
    route: '/detection/tasks/create'
  },
  {
    title: '配置脱敏规则',
    description: '选择或自定义脱敏方式',
    color: '#4facfe',
    icon: 'Setting',
    route: '/desensitization/rules'
  },
  {
    title: '执行脱敏处理',
    description: '预览确认后批量处理',
    color: '#fa709a',
    icon: 'DataAnalysis',
    route: '/desensitization/tasks/create'
  },
  {
    title: '查看报告',
    description: '生成多格式导出报告',
    color: '#11998e',
    icon: 'Tickets',
    route: '/report/platform'
  }
]

const handleWorkflowClick = (step) => {
  if (step.route) router.push(step.route)
}

const highlights = [
  {
    icon: ChatDotRound,
    title: '多语言智能识别',
    description: '支持中、英、日、韩、法、德6种语言的敏感数据识别，基于字符集特征自动检测语言',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    tags: [
      { text: '6种语言', type: 'primary' },
      { text: '自动检测', type: 'success' }
    ]
  },
  {
    icon: Connection,
    title: '识别-脱敏一体化',
    description: '识别结果一键跳转脱敏，自动传递数据并推荐最优脱敏规则，三步完成全流程',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    tags: [
      { text: '一键跳转', type: 'warning' },
      { text: '智能推荐', type: 'success' }
    ]
  },
  {
    icon: Key,
    title: '关联仿真脱敏',
    description: '基于密钥的确定性脱敏算法，保证跨表数据一致性，30组独立密钥安全隔离',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    tags: [
      { text: '首创算法', type: 'danger' },
      { text: '跨表一致', type: 'primary' },
      { text: '安全隔离', type: 'success' }
    ]
  },
  {
    icon: View,
    title: '可视化前后对比',
    description: '脱敏前展示数据对比预览，用户确认后才执行全量处理，避免误操作风险',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    tags: [
      { text: '实时预览', type: 'success' },
      { text: '安全确认', type: 'danger' }
    ]
  },
  {
    icon: Document,
    title: '多种报告格式',
    description: '支持HTML在线预览和Markdown格式下载，方便存档、分享和版本管理',
    gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    tags: [
      { text: 'HTML预览', type: 'primary' },
      { text: 'MD下载', type: 'success' }
    ]
  },
  {
    icon: Cpu,
    title: '高性能异步处理',
    description: '大文件后台异步处理，支持实时进度查看，处理速度可达数万行每秒',
    gradient: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
    tags: [
      { text: '异步处理', type: 'warning' },
      { text: '实时进度', type: 'primary' }
    ]
  }
]

const getStatusType = (status) => {
  const map = {
    completed: 'success',
    running: 'warning',
    pending: 'info',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    completed: '已完成',
    running: '进行中',
    pending: '等待中',
    failed: '失败'
  }
  return map[status] || status
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (date.toDateString() === now.toDateString()) {
    return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  return `${date.getMonth() + 1}-${date.getDate()}`
}

const initChart = () => {
  if (!chartRef.value || sensitiveDistribution.value.length === 0) return
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  chartInstance.value = echarts.init(chartRef.value)
  chartInstance.value.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        return `<div style="padding: 6px 10px;">
          <div style="font-weight: 600; margin-bottom: 4px; font-size: 12px;">${params.name}</div>
          <div style="font-size: 12px;">数量：${params.value}  占比：${params.percent}%</div>
        </div>`
      },
      backgroundColor: 'rgba(255, 255, 255, 0.98)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133', fontSize: 12 },
      extraCssText: 'box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12); border-radius: 4px;'
    },
    legend: { show: false },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      labelLine: { show: false },
      emphasis: {
        scaleSize: 6,
        label: { show: true, fontSize: 11, fontWeight: 'bold', formatter: '{b}\n{d}%' },
        itemStyle: { shadowBlur: 8, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.2)' }
      },
      data: sensitiveDistribution.value.map((item, index) => ({
        name: item.name,
        value: item.count,
        itemStyle: { color: chartColors[index % chartColors.length] }
      }))
    }]
  })
  window.addEventListener('resize', () => chartInstance.value && chartInstance.value.resize())
}

const loadStats = async () => {
  try {
    const res = await getDashboardStats()
    stats.value = res.data.overview || {}
    recentDetectionTasks.value = res.data.recent_tasks?.detection || []
    recentDesensitizationTasks.value = res.data.recent_tasks?.desensitization || []
    sensitiveDistribution.value = res.data.sensitive_type_distribution || []
    nextTick(() => initChart())
  } catch (e) {
    console.error('加载统计数据失败:', e)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1280px;
  margin: 0 auto;
}

/* 欢迎语单独一行 */
.welcome-section {
  margin-bottom: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: 10px;
  border-left: 4px solid #409EFF;
}

.welcome-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
  line-height: 1.3;
}

.welcome-subtitle {
  font-size: 13px;
  color: #606266;
  margin: 0;
  line-height: 1.4;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.quick-action-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
  min-width: 120px;
}

.quick-action-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-action-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.quick-action-title {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

/* 区块通用 */
.section {
  margin-bottom: 16px;
}

.section-card {
  border-radius: 10px;
}

/* 平台数据概览卡片 */
.stats-card {
  height: 100%;
}

/* 最近任务卡片 */
.tasks-card {
  height: 100%;
}

.section-card :deep(.el-card__header) {
  padding: 12px 18px;
  border-bottom: 1px solid #ebeef5;
}

.section-card :deep(.el-card__body) {
  padding: 16px 18px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 平台操作流程 - 横向排列 */
.workflow-steps {
  display: flex;
  align-items: stretch;
  gap: 0;
}

.workflow-step {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 12px;
  border-radius: 8px;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.workflow-step:hover {
  background: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.workflow-step:not(:last-child) {
  margin-right: 10px;
}

.step-badge {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-desc {
  font-size: 11px;
  color: #909399;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-arrow {
  color: #c0c4cc;
  flex-shrink: 0;
}

/* 核心指标 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  border-radius: 8px;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stat-box:hover {
  background: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* 图表区域 */
.chart-section {
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chart-name {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.chart-total {
  font-size: 11px;
  color: #909399;
}

.chart-body {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-container {
  flex: 1;
  height: 200px;
  min-width: 0;
}

.chart-legend {
  width: 130px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.legend-item:hover {
  background: #f5f7fa;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  flex: 1;
  font-size: 11px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.legend-value {
  font-size: 11px;
  font-weight: 600;
  color: #303133;
  flex-shrink: 0;
}

.legend-percent {
  font-size: 10px;
  color: #909399;
  flex-shrink: 0;
}

/* 任务列表 */
.task-tabs :deep(.el-tabs__header) {
  margin-bottom: 10px;
}

.task-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  font-weight: 500;
  padding: 0 14px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-item:hover {
  background: #ecf5ff;
}

.task-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-dot.success { background: #67c23a; }
.task-dot.warning { background: #e6a23c; }
.task-dot.info { background: #909399; }
.task-dot.danger { background: #f56c6c; }

.task-main {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-time {
  font-size: 11px;
  color: #909399;
}

.task-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.task-count-zero {
  font-size: 12px;
  color: #c0c4cc;
  font-weight: 500;
}

.task-rows {
  font-size: 11px;
  color: #409EFF;
  font-weight: 500;
}

.task-progress {
  width: 70px;
}

.task-empty {
  padding: 16px 0;
}

/* 平台亮点 */
.highlights-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.highlight-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px;
  border-radius: 8px;
  background: #f5f7fa;
  transition: all 0.2s ease;
}

.highlight-item:hover {
  background: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.highlight-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.highlight-body {
  flex: 1;
  min-width: 0;
}

.highlight-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.highlight-desc {
  font-size: 11px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.highlight-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* 响应式 */
@media (max-width: 1200px) {
  .workflow-steps {
    flex-wrap: wrap;
    gap: 10px;
  }

  .workflow-step {
    flex: 0 0 calc(33.333% - 7px);
    margin-right: 0 !important;
  }

  .step-arrow {
    display: none;
  }

  .highlights-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 12px;
  }

  .welcome-section {
    padding: 16px 20px;
  }

  .welcome-title {
    font-size: 18px;
  }

  .workflow-step {
    flex: 0 0 calc(50% - 5px);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .quick-action-item {
    min-width: calc(50% - 5px);
    padding: 8px 12px;
  }

  .chart-body {
    flex-direction: column;
  }

  .chart-container {
    height: 180px;
    width: 100%;
  }

  .chart-legend {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    max-height: none;
  }

  .legend-item {
    flex: 0 0 calc(50% - 3px);
  }

  .highlights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .workflow-step {
    flex: 0 0 100%;
  }

  .quick-action-item {
    min-width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
