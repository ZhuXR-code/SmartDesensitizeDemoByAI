<template>
  <div class="dashboard">
    <!-- 欢迎语 - 玻璃卡片 -->
    <div class="welcome-glass">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎使用敏感信息智能脱敏平台</h1>
        <p class="welcome-subtitle">全方位保护数据安全，智能识别与脱敏敏感信息</p>
      </div>
      <div class="welcome-decoration"></div>
    </div>

    <!-- 平台核心亮点 - 玻璃卡片 -->
    <div class="section-glass highlights-section-glass">
      <div class="section-header-glass">
        <div class="section-title-wrapper">
          <div class="section-icon-bg" style="background: linear-gradient(135deg, rgba(244,253,175,0.2) 0%, rgba(239,221,141,0.1) 100%);">
            <el-icon size="16" style="color: #F4FDAF;"><Star /></el-icon>
          </div>
          <span class="section-title">平台核心亮点</span>
        </div>
        <span class="section-badge badge-warning">行业领先</span>
      </div>
      <div class="highlights-grid-glass">
        <div
          v-for="(item, index) in highlights"
          :key="index"
          class="highlight-item-glass"
        >
          <div class="highlight-icon-glass" :style="{ background: item.gradient }">
            <el-icon size="18"><component :is="item.icon" /></el-icon>
          </div>
          <div class="highlight-body">
            <div class="highlight-title">{{ item.title }}</div>
            <div class="highlight-desc">{{ item.description }}</div>
            <div class="highlight-tags">
              <span
                v-for="(tag, tidx) in item.tags"
                :key="tidx"
                class="highlight-tag"
                :class="'tag-' + tag.type"
              >
                {{ tag.text }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 - 玻璃胶囊 -->
    <div class="quick-actions-section">
      <div
        v-for="(action, index) in quickActions"
        :key="index"
        class="quick-action-glass"
        @click="$router.push(action.route)"
      >
        <div class="quick-action-icon" :style="{ background: action.gradient }">
          <el-icon size="18"><component :is="action.icon" /></el-icon>
        </div>
        <span class="quick-action-title">{{ action.title }}</span>
        <div class="quick-action-arrow">
          <el-icon size="12"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 平台操作流程 - 玻璃卡片 -->
    <div class="section-glass">
      <div class="section-header-glass">
        <div class="section-title-wrapper">
          <div class="section-icon-bg" style="background: linear-gradient(135deg, rgba(101,116,58,0.3) 0%, rgba(57,79,73,0.2) 100%);">
            <el-icon size="16" style="color: #F4FDAF;"><Guide /></el-icon>
          </div>
          <span class="section-title">平台操作流程</span>
        </div>
        <span class="section-badge">快速开始</span>
      </div>
      <div class="workflow-steps-glass">
        <div
          v-for="(step, index) in workflowSteps"
          :key="index"
          class="workflow-step-glass"
          @click="handleWorkflowClick(step)"
        >
          <div class="step-badge-glass" :style="{ background: step.gradient }">
            <el-icon size="14"><component :is="step.icon" /></el-icon>
          </div>
          <div class="step-info">
            <div class="step-title">{{ step.title }}</div>
            <div class="step-desc">{{ step.description }}</div>
          </div>
          <el-icon v-if="index < workflowSteps.length - 1" class="step-arrow" size="14"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 核心指标 + 最近任务 -->
    <el-row :gutter="20" class="section-row">
      <el-col :xs="24" :md="10" class="equal-height-col">
        <div class="section-glass stats-glass">
          <div class="section-header-glass">
            <div class="section-title-wrapper">
              <div class="section-icon-bg" style="background: linear-gradient(135deg, rgba(101,116,58,0.25) 0%, rgba(57,79,73,0.15) 100%);">
                <el-icon size="16" style="color: #F4FDAF;"><DataLine /></el-icon>
              </div>
              <span class="section-title">平台数据概览</span>
            </div>
            <span class="section-badge badge-info">实时统计</span>
          </div>

          <div class="stats-grid-glass">
            <div class="stat-box-glass" @click="$router.push('/datasets')">
              <div class="stat-icon-glass" style="background: linear-gradient(135deg, rgba(101,116,58,0.6) 0%, rgba(57,79,73,0.5) 100%);">
                <el-icon size="20"><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_datasets || 0 }}</div>
                <div class="stat-label">数据集</div>
              </div>
            </div>
            <div class="stat-box-glass" @click="$router.push('/detection/tasks')">
              <div class="stat-icon-glass" style="background: linear-gradient(135deg, rgba(244,253,175,0.3) 0%, rgba(239,221,141,0.2) 100%);">
                <el-icon size="20"><Search /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_detection_tasks || 0 }}</div>
                <div class="stat-label">识别任务</div>
              </div>
            </div>
            <div class="stat-box-glass" @click="$router.push('/desensitization/tasks')">
              <div class="stat-icon-glass" style="background: linear-gradient(135deg, rgba(57,79,73,0.6) 0%, rgba(33,1,36,0.5) 100%);">
                <el-icon size="20"><Lock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_desensitization_tasks || 0 }}</div>
                <div class="stat-label">脱敏任务</div>
              </div>
            </div>
            <div class="stat-box-glass">
              <div class="stat-icon-glass" style="background: linear-gradient(135deg, rgba(220,38,38,0.4) 0%, rgba(245,158,11,0.3) 100%);">
                <el-icon size="20"><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value" style="color: #FCA5A5;">{{ stats.total_sensitive_found || 0 }}</div>
                <div class="stat-label">敏感发现</div>
              </div>
            </div>
          </div>

          <div class="chart-section-glass">
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
        </div>
      </el-col>

      <el-col :xs="24" :md="14" class="equal-height-col">
        <div class="section-glass tasks-glass">
          <div class="section-header-glass">
            <div class="section-title-wrapper">
              <div class="section-icon-bg" style="background: linear-gradient(135deg, rgba(101,116,58,0.25) 0%, rgba(57,79,73,0.15) 100%);">
                <el-icon size="16" style="color: #F4FDAF;"><Timer /></el-icon>
              </div>
              <span class="section-title">最近任务</span>
            </div>
            <span class="section-badge badge-success">实时更新</span>
          </div>

          <div class="glass-tabs-custom">
            <button
              :class="['glass-tab-custom', { active: activeTab === 'detection' }]"
              @click="activeTab = 'detection'"
            >
              识别任务
            </button>
            <button
              :class="['glass-tab-custom', { active: activeTab === 'desensitization' }]"
              @click="activeTab = 'desensitization'"
            >
              脱敏任务
            </button>
          </div>

          <div class="task-list-glass">
            <template v-if="activeTab === 'detection'">
              <div v-if="recentDetectionTasks.length === 0" class="task-empty">
                <el-empty description="暂无识别任务" :image-size="60" />
              </div>
              <div
                v-for="task in recentDetectionTasks"
                :key="task.id"
                class="task-item-glass"
                @click="$router.push('/detection/tasks/' + task.id)"
              >
                <div class="task-dot" :class="getStatusType(task.status)"></div>
                <div class="task-main">
                  <div class="task-name" :title="task.name">{{ task.name }}</div>
                  <div class="task-meta">
                    <span class="task-status" :class="getStatusType(task.status)">{{ getStatusText(task.status) }}</span>
                    <span class="task-time">{{ formatTime(task.created_at) }}</span>
                  </div>
                </div>
                <div class="task-side">
                  <span v-if="task.found_count > 0" class="task-count">{{ task.found_count }}</span>
                  <span v-else class="task-count-zero">0</span>
                  <el-progress
                    :percentage="task.progress || 0"
                    :stroke-width="3"
                    :show-text="false"
                    class="task-progress"
                  />
                </div>
              </div>
            </template>

            <template v-if="activeTab === 'desensitization'">
              <div v-if="recentDesensitizationTasks.length === 0" class="task-empty">
                <el-empty description="暂无脱敏任务" :image-size="60" />
              </div>
              <div
                v-for="task in recentDesensitizationTasks"
                :key="task.id"
                class="task-item-glass"
                @click="$router.push('/desensitization/tasks/' + task.id)"
              >
                <div class="task-dot" :class="getStatusType(task.status)"></div>
                <div class="task-main">
                  <div class="task-name" :title="task.name">{{ task.name }}</div>
                  <div class="task-meta">
                    <span class="task-status" :class="getStatusType(task.status)">{{ getStatusText(task.status) }}</span>
                    <span class="task-time">{{ formatTime(task.created_at) }}</span>
                  </div>
                </div>
                <div class="task-side">
                  <span class="task-rows">{{ task.processed_rows || 0 }} 行</span>
                  <el-progress
                    :percentage="task.progress || 0"
                    :stroke-width="3"
                    :show-text="false"
                    class="task-progress"
                  />
                </div>
              </div>
            </template>
          </div>
        </div>
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
  ArrowRight, DataAnalysis, Setting, Tickets, Guide, DataLine, Timer, Star
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

const chartColors = ['#F4FDAF', '#EFDD8D', '#65743A', '#394F49', '#84fab0', '#fccb90', '#e0c3fc', '#8ec5fc']

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
    gradient: 'linear-gradient(135deg, rgba(101,116,58,0.6) 0%, rgba(57,79,73,0.5) 100%)',
    route: '/datasets/upload'
  },
  {
    title: '创建识别',
    icon: 'Search',
    gradient: 'linear-gradient(135deg, rgba(244,253,175,0.3) 0%, rgba(239,221,141,0.2) 100%)',
    route: '/detection/tasks/create'
  },
  {
    title: '创建脱敏',
    icon: 'Lock',
    gradient: 'linear-gradient(135deg, rgba(57,79,73,0.6) 0%, rgba(33,1,36,0.5) 100%)',
    route: '/desensitization/tasks/create'
  },
  {
    title: '规则管理',
    icon: 'Setting',
    gradient: 'linear-gradient(135deg, rgba(101,116,58,0.5) 0%, rgba(244,253,175,0.2) 100%)',
    route: '/desensitization/rules'
  },
  {
    title: '运营报表',
    icon: 'TrendCharts',
    gradient: 'linear-gradient(135deg, rgba(239,221,141,0.3) 0%, rgba(101,116,58,0.4) 100%)',
    route: '/report/platform'
  },
  {
    title: '用户手册',
    icon: 'DocumentChecked',
    gradient: 'linear-gradient(135deg, rgba(244,253,175,0.25) 0%, rgba(239,221,141,0.15) 100%)',
    route: '/help/manual'
  }
]

const workflowSteps = [
  {
    title: '导入数据',
    description: '上传Excel/CSV或连接数据库',
    gradient: 'linear-gradient(135deg, rgba(101,116,58,0.6) 0%, rgba(57,79,73,0.5) 100%)',
    icon: 'Upload',
    route: '/datasets/upload'
  },
  {
    title: '识别敏感数据',
    description: '智能扫描发现敏感信息',
    gradient: 'linear-gradient(135deg, rgba(244,253,175,0.3) 0%, rgba(239,221,141,0.2) 100%)',
    icon: 'Search',
    route: '/detection/tasks/create'
  },
  {
    title: '配置脱敏规则',
    description: '选择或自定义脱敏方式',
    gradient: 'linear-gradient(135deg, rgba(57,79,73,0.6) 0%, rgba(33,1,36,0.5) 100%)',
    icon: 'Setting',
    route: '/desensitization/rules'
  },
  {
    title: '执行脱敏处理',
    description: '预览确认后批量处理',
    gradient: 'linear-gradient(135deg, rgba(239,221,141,0.3) 0%, rgba(101,116,58,0.4) 100%)',
    icon: 'DataAnalysis',
    route: '/desensitization/tasks/create'
  },
  {
    title: '查看报告',
    description: '生成多格式导出报告',
    gradient: 'linear-gradient(135deg, rgba(101,116,58,0.5) 0%, rgba(244,253,175,0.2) 100%)',
    icon: 'Tickets',
    route: '/report/platform'
  }
]

const handleWorkflowClick = (step) => {
  if (step.route) router.push(step.route)
}

const highlights = [
  {
    icon: 'MapLocation',
    title: '多语言智能识别',
    description: '支持中、英、日、韩、法、德6种语言的敏感数据识别，基于字符集特征自动检测语言',
    gradient: 'linear-gradient(135deg, rgba(101,116,58,0.6) 0%, rgba(57,79,73,0.5) 100%)',
    tags: [
      { text: '6种语言', type: 'primary' },
      { text: '自动检测', type: 'success' }
    ]
  },
  {
    icon: 'Connection',
    title: '识别-脱敏一体化',
    description: '识别结果一键跳转脱敏，自动传递数据并推荐最优脱敏规则，三步完成全流程',
    gradient: 'linear-gradient(135deg, rgba(244,253,175,0.3) 0%, rgba(239,221,141,0.2) 100%)',
    tags: [
      { text: '一键跳转', type: 'warning' },
      { text: '智能推荐', type: 'success' }
    ]
  },
  {
    icon: 'Key',
    title: '关联仿真脱敏',
    description: '基于密钥的确定性脱敏算法，保证跨表数据一致性，30组独立密钥安全隔离',
    gradient: 'linear-gradient(135deg, rgba(57,79,73,0.6) 0%, rgba(33,1,36,0.5) 100%)',
    tags: [
      { text: '跨表关联', type: 'primary' },
      { text: '安全隔离', type: 'success' },
      { text: '行业首创', type: 'warning' }
    ]
  },
  {
    icon: 'View',
    title: '可视化前后对比',
    description: '脱敏前展示数据对比预览，用户确认后才执行全量处理，避免误操作风险',
    gradient: 'linear-gradient(135deg, rgba(239,221,141,0.3) 0%, rgba(101,116,58,0.4) 100%)',
    tags: [
      { text: '实时预览', type: 'success' },
      { text: '安全确认', type: 'danger' }
    ]
  },
  {
    icon: 'Document',
    title: '多种报告格式',
    description: '支持HTML在线预览和Markdown格式下载，方便存档、分享和版本管理',
    gradient: 'linear-gradient(135deg, rgba(101,116,58,0.5) 0%, rgba(244,253,175,0.2) 100%)',
    tags: [
      { text: 'HTML预览', type: 'primary' },
      { text: 'MD下载', type: 'success' }
    ]
  },
  {
    icon: 'Cpu',
    title: '高性能异步处理',
    description: '大文件后台异步处理，支持实时进度查看，处理速度可达数万行每秒',
    gradient: 'linear-gradient(135deg, rgba(244,253,175,0.25) 0%, rgba(239,221,141,0.15) 100%)',
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
        return `<div style="padding: 8px 12px; backdrop-filter: blur(12px); background: rgba(33,1,36,0.95); border-radius: 8px; border: 1px solid rgba(244,253,175,0.2); box-shadow: 0 4px 16px rgba(0,0,0,0.4);">
          <div style="font-weight: 600; margin-bottom: 4px; font-size: 13px; color: #F4FDAF;">${params.name}</div>
          <div style="font-size: 12px; color: #EFDD8D;">数量：${params.value}  占比：${params.percent}%</div>
        </div>`
      },
      backgroundColor: 'transparent',
      borderColor: 'transparent',
      borderWidth: 0,
      textStyle: { color: '#F4FDAF', fontSize: 12 },
      extraCssText: 'box-shadow: none;'
    },
    legend: { show: false },
    series: [{
      type: 'pie',
      radius: ['38%', '68%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 8, borderColor: 'rgba(33,1,36,0.8)', borderWidth: 3 },
      label: { show: false },
      labelLine: { show: false },
      emphasis: {
        scaleSize: 8,
        label: { show: true, fontSize: 12, fontWeight: 'bold', formatter: '{b}\n{d}%', color: '#F4FDAF' },
        itemStyle: { shadowBlur: 12, shadowOffsetX: 0, shadowColor: 'rgba(244, 253, 175, 0.2)' }
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

<style scoped lang="scss">
.dashboard {
  padding: 4px;
  max-width: 1320px;
  margin: 0 auto;
}

// 欢迎语 - 玻璃卡片
.welcome-glass {
  position: relative;
  margin-bottom: 20px;
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(57, 79, 73, 0.5) 0%, rgba(33, 1, 36, 0.4) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(244, 253, 175, 0.1);
  border-radius: 20px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(244, 253, 175, 0.08);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);

  &:hover {
    box-shadow:
      0 12px 40px rgba(0, 0, 0, 0.4),
      inset 0 1px 0 rgba(244, 253, 175, 0.12);
    transform: translateY(-1px);
  }
}

.welcome-content {
  position: relative;
  z-index: 2;
}

.welcome-decoration {
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(244, 253, 175, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.welcome-title {
  font-size: 22px;
  font-weight: 700;
  color: #F4FDAF;
  margin: 0 0 8px 0;
  line-height: 1.3;
  letter-spacing: -0.3px;
}

.welcome-subtitle {
  font-size: 14px;
  color: rgba(239, 221, 141, 0.7);
  margin: 0;
  line-height: 1.5;
}

// 快捷操作 - 玻璃胶囊
.quick-actions-section {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.quick-action-glass {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  background: rgba(57, 79, 73, 0.35);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(244, 253, 175, 0.08);
  border-radius: 9999px;
  box-shadow:
    0 4px 16px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(244, 253, 175, 0.05);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  flex: 1;
  min-width: 140px;

  &:hover {
    background: rgba(57, 79, 73, 0.5);
    transform: translateY(-2px);
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.3),
      inset 0 1px 0 rgba(244, 253, 175, 0.1);
  }

  &:active {
    transform: translateY(0);
  }
}

.quick-action-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #F4FDAF;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.quick-action-title {
  font-size: 13px;
  font-weight: 600;
  color: #EFDD8D;
  flex: 1;
}

.quick-action-arrow {
  color: rgba(239, 221, 141, 0.4);
  transition: all 0.2s ease;
}

.quick-action-glass:hover .quick-action-arrow {
  color: #F4FDAF;
  transform: translateX(2px);
}

// 通用玻璃区块
.section-glass {
  background: rgba(57, 79, 73, 0.3);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(244, 253, 175, 0.08);
  border-radius: 20px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(244, 253, 175, 0.05);
  padding: 20px;
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);

  &:hover {
    background: rgba(57, 79, 73, 0.4);
    box-shadow:
      0 12px 40px rgba(0, 0, 0, 0.35),
      inset 0 1px 0 rgba(244, 253, 175, 0.08);
  }
}

.section-header-glass {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon-bg {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  color: #F4FDAF;
  letter-spacing: -0.2px;
}

.section-badge {
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, rgba(57, 79, 73, 0.4) 0%, rgba(33, 1, 36, 0.3) 100%);
  color: rgba(239, 221, 141, 0.8);
}

.badge-success {
  background: linear-gradient(135deg, rgba(101, 116, 58, 0.3) 0%, rgba(57, 79, 73, 0.2) 100%);
  color: #F4FDAF;
}

.badge-info {
  background: linear-gradient(135deg, rgba(57, 79, 73, 0.4) 0%, rgba(33, 1, 36, 0.3) 100%);
  color: rgba(239, 221, 141, 0.8);
}

.badge-warning {
  background: linear-gradient(135deg, rgba(244, 253, 175, 0.15) 0%, rgba(239, 221, 141, 0.1) 100%);
  color: #EFDD8D;
}

// 工作流程
.workflow-steps-glass {
  display: flex;
  align-items: stretch;
  gap: 0;
}

.workflow-step-glass {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 12px;
  border-radius: 14px;
  background: rgba(33, 1, 36, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.06);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  position: relative;

  &:hover {
    background: rgba(33, 1, 36, 0.5);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
    border-color: rgba(244, 253, 175, 0.12);
  }

  &:not(:last-child) {
    margin-right: 10px;
  }
}

.step-badge-glass {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #F4FDAF;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 13px;
  font-weight: 600;
  color: #F4FDAF;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-desc {
  font-size: 11px;
  color: rgba(239, 221, 141, 0.5);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-arrow {
  color: rgba(244, 253, 175, 0.3);
  flex-shrink: 0;
}

// 核心指标
.stats-grid-glass {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-box-glass {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 14px;
  background: rgba(33, 1, 36, 0.25);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.06);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);

  &:hover {
    background: rgba(33, 1, 36, 0.45);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
    border-color: rgba(244, 253, 175, 0.1);
  }
}

.stat-icon-glass {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #F4FDAF;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #F4FDAF;
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.stat-label {
  font-size: 12px;
  color: rgba(239, 221, 141, 0.5);
  margin-top: 2px;
  font-weight: 500;
}

// 图表区域
.chart-section-glass {
  padding-top: 14px;
  border-top: 1px solid rgba(244, 253, 175, 0.06);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-name {
  font-size: 13px;
  font-weight: 600;
  color: #F4FDAF;
}

.chart-total {
  font-size: 11px;
  color: rgba(239, 221, 141, 0.5);
  font-weight: 500;
}

.chart-body {
  display: flex;
  align-items: center;
  gap: 14px;
}

.chart-container {
  flex: 1;
  height: 200px;
  min-width: 0;
}

.chart-legend {
  width: 140px;
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
  padding: 5px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(33, 1, 36, 0.2);

  &:hover {
    background: rgba(33, 1, 36, 0.4);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
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
  color: rgba(239, 221, 141, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.legend-value {
  font-size: 11px;
  font-weight: 600;
  color: #F4FDAF;
  flex-shrink: 0;
}

.legend-percent {
  font-size: 10px;
  color: rgba(239, 221, 141, 0.4);
  flex-shrink: 0;
}

// 玻璃标签页
.glass-tabs-custom {
  display: flex;
  background: rgba(33, 1, 36, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.06);
  border-radius: 12px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 14px;
}

.glass-tab-custom {
  flex: 1;
  padding: 8px 16px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  color: rgba(239, 221, 141, 0.5);
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);

  &:hover {
    color: #EFDD8D;
    background: rgba(244, 253, 175, 0.05);
  }

  &.active {
    color: #F4FDAF;
    background: rgba(244, 253, 175, 0.1);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  }
}

// 任务列表
.task-list-glass {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item-glass {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(33, 1, 36, 0.25);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.04);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);

  &:hover {
    background: rgba(33, 1, 36, 0.45);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateX(2px);
    border-color: rgba(244, 253, 175, 0.08);
  }
}

.task-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-dot.success { background: #65743A; box-shadow: 0 0 0 3px rgba(101, 116, 58, 0.2); }
.task-dot.warning { background: #EFDD8D; box-shadow: 0 0 0 3px rgba(239, 221, 141, 0.15); }
.task-dot.info { background: rgba(239, 221, 141, 0.4); box-shadow: 0 0 0 3px rgba(239, 221, 141, 0.08); }
.task-dot.danger { background: #EF4444; box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15); }

.task-main {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 13px;
  font-weight: 600;
  color: #F4FDAF;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-status {
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
}

.task-status.success { background: rgba(101, 116, 58, 0.2); color: #F4FDAF; }
.task-status.warning { background: rgba(239, 221, 141, 0.1); color: #EFDD8D; }
.task-status.info { background: rgba(57, 79, 73, 0.3); color: rgba(239, 221, 141, 0.6); }
.task-status.danger { background: rgba(220, 38, 38, 0.1); color: #FCA5A5; }

.task-time {
  font-size: 11px;
  color: rgba(239, 221, 141, 0.4);
}

.task-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.task-count {
  font-size: 12px;
  font-weight: 700;
  color: #EFDD8D;
  background: rgba(239, 221, 141, 0.08);
  padding: 2px 8px;
  border-radius: 9999px;
}

.task-count-zero {
  font-size: 12px;
  color: rgba(239, 221, 141, 0.3);
  font-weight: 600;
}

.task-rows {
  font-size: 11px;
  color: rgba(244, 253, 175, 0.6);
  font-weight: 600;
}

.task-progress {
  width: 70px;
}

.task-empty {
  padding: 20px 0;
}

// 平台亮点
.highlights-grid-glass {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.highlight-item-glass {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 18px;
  border-radius: 16px;
  background: rgba(33, 1, 36, 0.25);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.04);
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);

  &:hover {
    background: rgba(33, 1, 36, 0.45);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-3px);
    border-color: rgba(244, 253, 175, 0.08);
  }
}

.highlight-icon-glass {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #F4FDAF;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
}

.highlight-body {
  flex: 1;
  min-width: 0;
}

.highlight-title {
  font-size: 14px;
  font-weight: 700;
  color: #F4FDAF;
  margin-bottom: 5px;
  letter-spacing: -0.2px;
}

.highlight-desc {
  font-size: 12px;
  color: rgba(239, 221, 141, 0.6);
  line-height: 1.6;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.highlight-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.highlight-tag {
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.tag-primary { background: rgba(244, 253, 175, 0.1); color: #F4FDAF; }
.tag-success { background: rgba(101, 116, 58, 0.2); color: #F4FDAF; }
.tag-warning { background: rgba(239, 221, 141, 0.08); color: #EFDD8D; }
.tag-info { background: rgba(57, 79, 73, 0.3); color: rgba(239, 221, 141, 0.7); }
.tag-danger { background: rgba(220, 38, 38, 0.08); color: #FCA5A5; }

// 等高度列
.equal-height-col {
  display: flex;

  > .section-glass {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
}

.stats-glass {
  display: flex;
  flex-direction: column;

  .stats-grid-glass {
    flex-shrink: 0;
  }

  .chart-section-glass {
    flex: 1;
    display: flex;
    flex-direction: column;

    .chart-body {
      flex: 1;
    }
  }
}

.tasks-glass {
  display: flex;
  flex-direction: column;

  .glass-tabs-custom {
    flex-shrink: 0;
  }

  .task-list-glass {
    flex: 1;
    overflow-y: auto;
  }
}

// 间距
.section-row {
  margin-bottom: 0;
}

// 响应式
@media (max-width: 1200px) {
  .workflow-steps-glass {
    flex-wrap: wrap;
    gap: 10px;
  }

  .workflow-step-glass {
    flex: 0 0 calc(33.333% - 7px);
    margin-right: 0 !important;
  }

  .step-arrow {
    display: none;
  }

  .highlights-grid-glass {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 8px;
  }

  .welcome-glass {
    padding: 18px 20px;
  }

  .welcome-title {
    font-size: 18px;
  }

  .workflow-step-glass {
    flex: 0 0 calc(50% - 5px);
  }

  .stats-grid-glass {
    grid-template-columns: repeat(2, 1fr);
  }

  .quick-action-glass {
    min-width: calc(50% - 6px);
    padding: 10px 14px;
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

  .highlights-grid-glass {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .workflow-step-glass {
    flex: 0 0 100%;
  }

  .quick-action-glass {
    min-width: 100%;
  }

  .stats-grid-glass {
    grid-template-columns: 1fr;
  }
}
</style>
