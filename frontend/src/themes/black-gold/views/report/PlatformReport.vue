<template>
  <div class="platform-report">
    <!-- 页面标题 -->
    <div class="report-header">
      <div class="header-left">
        <h2 class="report-title">📊 平台运营成效报告</h2>
        <p class="report-subtitle">敏感信息智能识别与脱敏平台 · 领导决策视图</p>
      </div>
      <div class="header-right">
        <el-tag type="success" effect="dark" size="large">实时数据</el-tag>
        <span class="update-time">更新时间: {{ currentTime }}</span>
      </div>
    </div>

    <!-- 核心指标总览 -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="4" v-for="(kpi, index) in kpis" :key="index">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-icon" :style="{ background: kpi.gradient }">
            <el-icon size="24"><component :is="kpi.icon" /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ kpi.value }}</div>
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-trend" v-if="kpi.trend">
              <el-tag :type="kpi.trendType" size="small" effect="plain">{{ kpi.trend }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 业务价值总结 -->
    <el-row class="section-row">
      <el-col :span="24">
        <el-card shadow="hover" class="summary-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">🎯 平台核心价值总结</span>
            </div>
          </template>
          <el-row :gutter="30">
            <el-col :xs="24" :md="8" v-for="(item, idx) in valueSummaries" :key="idx">
              <div class="value-item">
                <div class="value-number">{{ item.number }}</div>
                <div class="value-title">{{ item.title }}</div>
                <div class="value-desc">{{ item.description }}</div>
                <el-divider v-if="idx < 2" direction="vertical" class="value-divider" />
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 合规成果 + 平台优势（左右互换） -->
    <el-row :gutter="20" class="section-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="insight-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">💡 平台优势与结论</span>
            </div>
          </template>
          <div class="insight-list">
            <div v-for="(insight, idx) in insights" :key="idx" class="insight-item">
              <div class="insight-icon" :style="{ background: insight.color }">
                <el-icon size="18"><component :is="insight.icon" /></el-icon>
              </div>
              <div class="insight-content">
                <div class="insight-title">{{ insight.title }}</div>
                <div class="insight-desc">{{ insight.description }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="compliance-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">✅ 数据合规保障成果</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="敏感字段保护率">
              <el-progress :percentage="compliance.column_protection?.protection_rate || 0" :color="progressColors" />
              <span class="desc-detail">{{ compliance.column_protection?.protected_columns || 0 }} / {{ compliance.column_protection?.total_sensitive_columns || 0 }} 个字段</span>
            </el-descriptions-item>
            <el-descriptions-item label="脱敏任务完成率">
              <el-progress :percentage="desensitizationCompletionRate" :color="progressColors" />
              <span class="desc-detail">{{ overview.desensitization_tasks_completed || 0 }} / {{ overview.total_desensitization_tasks || 0 }} 个任务</span>
            </el-descriptions-item>
            <el-descriptions-item label="累计处理行数">
              <el-tag type="warning">{{ overview.total_processed_rows || 0 }} 行</el-tag>
              <span class="desc-detail">平台累计处理的敏感数据记录总量</span>
            </el-descriptions-item>
            <el-descriptions-item label="识别-脱敏闭环率">
              <el-progress :percentage="closedLoopRate" color="#67C23A" />
              <span class="desc-detail">{{ overview.total_desensitized || 0 }} / {{ overview.total_sensitive_found || 0 }} 条</span>
            </el-descriptions-item>
            <el-descriptions-item label="数据源接入规模">
              <el-tag type="primary">{{ overview.total_datasets || 0 }} 个</el-tag>
              <span class="desc-detail">多源异构数据统一纳管，灵活接入</span>
            </el-descriptions-item>
            <el-descriptions-item label="平均识别耗时">
              <el-tag type="success">{{ compliance.processing_efficiency?.avg_detection_time_seconds || 0 }} 秒</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="平均脱敏耗时">
              <el-tag type="success">{{ compliance.processing_efficiency?.avg_desensitization_time_seconds || 0 }} 秒</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="审计报告生成">
              <el-tag type="primary">{{ compliance.audit_trail?.total_reports_generated || 0 }} 份</el-tag>
              <span class="desc-detail">完整的操作日志支持审计追溯</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 技术先进性 -->
    <el-row class="section-row">
      <el-col :span="24">
        <el-card shadow="hover" class="tech-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">🚀 技术创新与先进性</span>
              <el-tag type="primary" effect="dark">行业领先</el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" v-for="(tech, idx) in techHighlights" :key="idx">
              <div class="tech-item">
                <div class="tech-badge">{{ tech.badge }}</div>
                <div class="tech-title">{{ tech.title }}</div>
                <div class="tech-metric">
                  <span class="metric-num">{{ tech.metric }}</span>
                  <span class="metric-unit">{{ tech.unit }}</span>
                </div>
                <div class="tech-desc">{{ tech.description }}</div>
                <div class="tech-tags">
                  <el-tag v-for="(tag, tidx) in tech.tags" :key="tidx" :type="tag.type" size="small" effect="plain">
                    {{ tag.text }}
                  </el-tag>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 安全价值 + 效率提升 -->
    <el-row :gutter="20" class="section-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">🛡️ 敏感数据安全保护成效</span>
            </div>
          </template>
          <div v-if="securityData.sensitive_type_distribution?.length > 0" ref="securityChartRef" style="height: 320px;"></div>
          <el-empty v-else description="暂无数据" :image-size="80" />
          <div class="chart-summary">
            <el-alert
              :title="`累计识别敏感信息 ${overview.total_sensitive_found || 0} 条，已完成脱敏保护 ${overview.total_desensitized || 0} 条`"
              type="success"
              :closable="false"
              show-icon
            />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">⚡ 自动化处理效率趋势（近7天）</span>
            </div>
          </template>
          <div v-if="efficiency.daily_trend?.length > 0" ref="efficiencyChartRef" style="height: 320px;"></div>
          <el-empty v-else description="暂无数据" :image-size="80" />
          <div class="chart-summary">
            <el-alert
              :title="`识别成功率 ${efficiency.detection_success_rate || 0}%，脱敏成功率 ${efficiency.desensitization_success_rate || 0}%，平均处理速度 ${efficiency.avg_desensitization_speed || 0} 行/秒`"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import {
  Document, Search, Lock, Warning, TrendCharts, Cpu,
  Check, Star, Lightning, WarnTriangleFilled, Connection, View, Key, Medal
} from '@element-plus/icons-vue'
import {
  getPlatformOverview,
  getSecurityValue,
  getEfficiencyStats,
  getTechnologyHighlights,
  getComplianceStats
} from '@/api/platformReport'

const currentTime = ref(new Date().toLocaleString())
const overview = ref({})
const securityData = ref({})
const efficiency = ref({})
const technology = ref({})
const compliance = ref({})

const securityChartRef = ref(null)
const efficiencyChartRef = ref(null)

const progressColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]

// KPI数据
const kpis = computed(() => [
  {
    icon: 'Document',
    value: overview.value.total_datasets || 0,
    label: '数据集总数',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    icon: 'Search',
    value: overview.value.total_detection_tasks || 0,
    label: '识别任务',
    trend: `本月+${overview.value.monthly_detection_tasks || 0}`,
    trendType: 'success',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    icon: 'Lock',
    value: overview.value.total_desensitization_tasks || 0,
    label: '脱敏任务',
    trend: `本月+${overview.value.monthly_desensitization_tasks || 0}`,
    trendType: 'success',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    icon: 'Warning',
    value: overview.value.total_sensitive_found || 0,
    label: '敏感信息发现',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  },
  {
    icon: 'Check',
    value: `${overview.value.accuracy_rate || 0}%`,
    label: '识别准确率',
    trend: '高精度保障',
    trendType: 'primary',
    gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
  },
  {
    icon: 'WarnTriangleFilled',
    value: `${overview.value.coverage_rate || 0}%`,
    label: '脱敏覆盖率',
    trend: '全面保护',
    trendType: 'warning',
    gradient: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)'
  }
])

// 合规新增指标
const desensitizationCompletionRate = computed(() => {
  if (!overview.value.total_desensitization_tasks) return 0
  return Math.min(100, Math.round((overview.value.desensitization_tasks_completed || 0) / overview.value.total_desensitization_tasks * 100))
})

const closedLoopRate = computed(() => {
  if (!overview.value.total_sensitive_found) return 0
  return Math.min(100, Math.round((overview.value.total_desensitized || 0) / overview.value.total_sensitive_found * 100))
})

// 价值总结
const valueSummaries = computed(() => [
  {
    number: `${efficiency.value.auto_detect_rate || 0}%`,
    title: '智能自动化率',
    description: '平台支持自动识别敏感字段并推荐最优脱敏规则，大幅降低人工配置成本，实现一键式智能处理。'
  },
  {
    number: `${efficiency.value.jump_usage_rate || 0}%`,
    title: '识别-脱敏一体化',
    description: '识别结果一键跳转脱敏任务，自动传递数据与规则配置，三步完成从识别到脱敏的全流程闭环。'
  },
  {
    number: `${technology.value.deterministic_desensitization?.usage_count || 0}`,
    title: '关联造数应用',
    description: '独创的基于密钥的确定性脱敏算法，保证跨表数据一致性，30组独立密钥实现安全隔离，既保管理又保安全。'
  }
])

// 技术亮点
const techHighlights = computed(() => [
  {
    badge: '独创',
    title: '关联仿真脱敏',
    metric: technology.value.deterministic_desensitization?.usage_count || 0,
    unit: '次应用',
    description: '基于密钥的确定性脱敏算法，同一原始值始终脱敏为同一结果，保证跨表数据一致性',
    tags: [
      { text: '跨表一致', type: 'primary' },
      { text: '30组密钥', type: 'success' },
      { text: '安全隔离', type: 'warning' }
    ]
  },
  {
    badge: '领先',
    title: '多语言智能识别',
    metric: technology.value.multilingual_support?.language_count || 0,
    unit: '种语言',
    description: '支持中、英、日、韩、法、德6种语言自动检测，基于字符集特征精准识别多语言敏感数据',
    tags: [
      { text: '自动检测', type: 'primary' },
      { text: '6种语言', type: 'success' },
      { text: '字符集分析', type: 'info' }
    ]
  },
  {
    badge: '高效',
    title: '高性能异步处理',
    metric: efficiency.value.avg_desensitization_speed || 0,
    unit: '行/秒',
    description: '大文件后台异步处理，支持实时进度查看，处理速度可达数万行/秒，不阻塞前端操作',
    tags: [
      { text: '异步处理', type: 'primary' },
      { text: '实时进度', type: 'success' },
      { text: '高吞吐', type: 'warning' }
    ]
  }
])

// 优势结论
const insights = [
  {
    icon: 'Star',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    title: '全流程自动化',
    description: '从数据上传、敏感识别、规则推荐到脱敏执行，全流程自动化处理，无需人工干预。'
  },
  {
    icon: 'Connection',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    title: '识别-脱敏一体化',
    description: '识别结果直接驱动脱敏任务，自动传递数据集与规则配置，消除数据流转断点。'
  },
  {
    icon: 'Key',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    title: '独创关联造数',
    description: '基于密钥的确定性脱敏算法为平台独创技术，保证跨表关联数据的一致性，30组密钥实现业务隔离。'
  },
  {
    icon: 'View',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    title: '可视化安全确认',
    description: '脱敏前展示10-20条数据前后对比，用户确认后才执行全量处理，避免误操作导致数据损坏。'
  },
  {
    icon: 'Medal',
    color: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    title: '多格式报告输出',
    description: '支持HTML在线预览和Markdown格式下载，方便存档、分享和版本管理，满足审计合规要求。'
  }
]

const initSecurityChart = () => {
  if (!securityChartRef.value || !securityData.value.sensitive_type_distribution?.length) return
  const chart = echarts.init(securityChartRef.value)
  const data = securityData.value.sensitive_type_distribution

  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { fontSize: 11 } },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 13, fontWeight: 'bold' }
      },
      data: data.map((item, index) => ({
        name: item.name,
        value: item.count,
        itemStyle: { color: ['#667eea', '#f5576c', '#4facfe', '#fa709a', '#84fab0', '#fccb90', '#e0c3fc', '#8ec5fc'][index % 8] }
      }))
    }]
  })
  window.addEventListener('resize', () => chart.resize())
}

const initEfficiencyChart = () => {
  if (!efficiencyChartRef.value || !efficiency.value.daily_trend?.length) return
  const chart = echarts.init(efficiencyChartRef.value)
  const data = efficiency.value.daily_trend

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['识别任务', '脱敏任务'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.date), axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '识别任务',
        type: 'bar',
        data: data.map(d => d.detection),
        itemStyle: { color: '#667eea', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '脱敏任务',
        type: 'bar',
        data: data.map(d => d.desensitization),
        itemStyle: { color: '#4facfe', borderRadius: [4, 4, 0, 0] }
      }
    ]
  })
  window.addEventListener('resize', () => chart.resize())
}

const loadData = async () => {
  try {
    const [ovRes, secRes, effRes, techRes, compRes] = await Promise.all([
      getPlatformOverview(),
      getSecurityValue(),
      getEfficiencyStats(),
      getTechnologyHighlights(),
      getComplianceStats()
    ])

    overview.value = ovRes.data || {}
    securityData.value = secRes.data || {}
    efficiency.value = effRes.data || {}
    technology.value = techRes.data || {}
    compliance.value = compRes.data || {}

    nextTick(() => {
      initSecurityChart()
      initEfficiencyChart()
    })
  } catch (e) {
    console.error('加载平台报表数据失败:', e)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.platform-report {
  padding: 20px;
  background: transparent;
  min-height: 100vh;
}

/* 页面标题 - 暖灰米色（大地起始） */
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: #E5E2DC;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 16px;
  border: 1px solid rgba(219, 214, 210, 0.5);
  box-shadow:
    0 8px 32px 0 rgba(31, 38, 135, 0.1),
    inset 0 1px 0 rgba(219, 214, 210, 0.6);
}

.report-title {
  font-size: 24px;
  font-weight: 600;
  color: #1F2937;
  margin: 0 0 6px 0;
}

.report-subtitle {
  font-size: 13px;
  color: #6B7280;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.update-time {
  font-size: 12px;
  color: #6B7280;
}

/* KPI卡片 */
.kpi-row {
  margin-bottom: 20px;
}

.kpi-card {
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  height: 100%;
  background: #E5E2DC;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(219, 214, 210, 0.5);
  box-shadow:
    0 8px 32px 0 rgba(31, 38, 135, 0.1),
    inset 0 1px 0 rgba(219, 214, 210, 0.6);

  &:hover {
    transform: translateY(-3px);
    box-shadow:
      0 12px 40px 0 rgba(31, 38, 135, 0.14),
      inset 0 1px 0 rgba(219, 214, 210, 0.8);
  }
}

.kpi-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  min-height: 90px;
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.kpi-content {
  flex: 1;
  min-width: 0;
}

.kpi-value {
  font-size: 22px;
  font-weight: bold;
  color: #1F2937;
  line-height: 1.2;
}

.kpi-label {
  font-size: 12px;
  color: #6B7280;
  margin-top: 4px;
}

.kpi-trend {
  margin-top: 4px;
}

/* 区块通用 */
.section-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1F2937;
}

/* 价值总结 */
.summary-card :deep(.el-card__body) {
  padding: 30px;
}

.value-item {
  text-align: center;
  padding: 10px;
  position: relative;
}

.value-number {
  font-size: 36px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
}

.value-title {
  font-size: 15px;
  font-weight: 600;
  color: #1F2937;
  margin: 10px 0 8px;
}

.value-desc {
  font-size: 12px;
  color: #4B5563;
  line-height: 1.6;
}

.value-divider {
  position: absolute;
  right: 0;
  top: 20%;
  height: 60%;
}

/* 图表 */
.chart-card :deep(.el-card__body) {
  padding: 20px;
}

.chart-summary {
  margin-top: 15px;
}

/* 技术亮点 */
.tech-card :deep(.el-card__body) {
  padding: 24px;
  background: #B7C6E1;
  border-radius: 16px;
}

.tech-item {
  background: rgba(229, 226, 220, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  margin-bottom: 10px;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  border: 1px solid rgba(219, 214, 210, 0.5);

  &:hover {
    background: rgba(229, 226, 220, 0.85);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(31, 38, 135, 0.1);
  }
}

.tech-badge {
  display: inline-block;
  background: linear-gradient(135deg, #f5576c 0%, #fa709a 100%);
  color: white;
  font-size: 11px;
  font-weight: bold;
  padding: 2px 10px;
  border-radius: 10px;
  margin-bottom: 10px;
}

.tech-title {
  font-size: 15px;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 8px;
}

.tech-metric {
  margin: 10px 0;
}

.metric-num {
  font-size: 28px;
  font-weight: bold;
  color: #4A90A4;
}

.metric-unit {
  font-size: 12px;
  color: #6B7280;
  margin-left: 4px;
}

.tech-desc {
  font-size: 12px;
  color: #4B5563;
  line-height: 1.6;
  margin-bottom: 10px;
}

.tech-tags {
  display: flex;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}

/* 合规 - 石板灰蓝（理性权威） */
.compliance-card {
  height: 100%;
  background: #8D99A5;
  border: 1px solid rgba(141, 153, 165, 0.5);
}

.compliance-card :deep(.el-card__body) {
  padding: 20px;
}

.desc-detail {
  font-size: 12px;
  color: #6B7280;
  margin-left: 8px;
}

/* 优势结论 - 雾霭青（通透智慧） */
.insight-card {
  height: 100%;
  background: #81A9B1;
  border: 1px solid rgba(129, 169, 177, 0.5);
}

.insight-card :deep(.el-card__body) {
  padding: 20px;
}

.insight-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.insight-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.insight-title {
  font-size: 14px;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 4px;
}

.insight-desc {
  font-size: 12px;
  color: #4B5563;
  line-height: 1.5;
}

/* 标签玻璃效果 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}
</style>
