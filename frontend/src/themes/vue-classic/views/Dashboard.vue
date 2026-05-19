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
              <div class="highlight-icon" style="background: #f0f0f0;">
                <el-icon size="20" style="color: #666;"><component :is="item.icon" /></el-icon>
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

    <!-- 🤖 AI大模型技术架构 -->
    <el-row class="section">
      <el-col :span="24">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span class="section-title">AI大模型技术架构</span>
              <el-tag type="danger" size="small" effect="light">核心技术</el-tag>
            </div>
          </template>
          <div class="ai-arch-flow">
            <div class="ai-arch-step">
              <div class="ai-arch-icon" style="background: #409EFF;">
                <el-icon size="20"><Document /></el-icon>
              </div>
              <div class="ai-arch-title">数据输入层</div>
              <div class="ai-arch-desc">多源异构数据接入<br>Excel/CSV/数据库</div>
            </div>
            <el-icon class="ai-arch-arrow" size="20"><ArrowRight /></el-icon>
            <div class="ai-arch-step">
              <div class="ai-arch-icon" style="background: #f5576c;">
                <el-icon size="20"><Cpu /></el-icon>
              </div>
              <div class="ai-arch-title">AI大模型识别</div>
              <div class="ai-arch-desc">深度学习语义理解<br>自动识别敏感字段</div>
            </div>
            <el-icon class="ai-arch-arrow" size="20"><ArrowRight /></el-icon>
            <div class="ai-arch-step">
              <div class="ai-arch-icon" style="background: #e6a23c;">
                <el-icon size="20"><MagicStick /></el-icon>
              </div>
              <div class="ai-arch-title">智能规则推荐</div>
              <div class="ai-arch-desc">AI匹配最优规则<br>一键配置脱敏策略</div>
            </div>
            <el-icon class="ai-arch-arrow" size="20"><ArrowRight /></el-icon>
            <div class="ai-arch-step">
              <div class="ai-arch-icon" style="background: #67c23a;">
                <el-icon size="20"><Lock /></el-icon>
              </div>
              <div class="ai-arch-title">智能脱敏执行</div>
              <div class="ai-arch-desc">关联仿真算法<br>跨表一致性保障</div>
            </div>
            <el-icon class="ai-arch-arrow" size="20"><ArrowRight /></el-icon>
            <div class="ai-arch-step">
              <div class="ai-arch-icon" style="background: #909399;">
                <el-icon size="20"><DocumentChecked /></el-icon>
              </div>
              <div class="ai-arch-title">报告生成</div>
              <div class="ai-arch-desc">HTML/Markdown<br>审计合规输出</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 🆚 与传统方案对比 -->
    <el-row class="section">
      <el-col :span="24">
        <el-card shadow="never" class="compare-new-card">
          <template #header>
            <div class="section-header">
              <span class="section-title">与传统方案对比</span>
            </div>
          </template>
          <div class="compare-grid">
            <div v-for="(item, idx) in compareItems" :key="idx" class="compare-item" :style="{ '--accent': item.accent }">
              <div class="compare-item-header">
                <span class="compare-item-icon">{{ item.emoji }}</span>
                <span class="compare-item-name">{{ item.feature }}</span>
              </div>
              <div class="compare-item-row">
                <div class="compare-col old">
                  <span class="compare-col-label">传统方案</span>
                  <p class="compare-col-text">{{ item.traditional }}</p>
                </div>
                <div class="compare-col-divider">
                  <svg width="20" height="20" viewBox="0 0 20 20"><path d="M7 4l6 6-6 6" stroke="#c0c4cc" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </div>
                <div class="compare-col new">
                  <span class="compare-col-label new-label">AI 方案</span>
                  <p class="compare-col-text new-text">{{ item.our }}</p>
                </div>
              </div>
              <div class="compare-item-stat">
                <span class="compare-stat-num">{{ item.advantageNum }}</span>
                <span class="compare-stat-desc">{{ item.advantageDesc }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 💰 成本与效率优势 -->
    <el-row class="section">
      <el-col :span="24">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="section-header">
              <span class="section-title">成本与效率优势</span>
              <el-tag type="success" size="small" effect="light">量化对比</el-tag>
            </div>
          </template>
          <div class="efficiency-grid">
            <div class="efficiency-card">
              <div class="efficiency-icon" style="background: #f5576c;">
                <el-icon size="24"><Timer /></el-icon>
              </div>
              <div class="efficiency-number">2小时 → 5分钟</div>
              <div class="efficiency-title">任务处理时间</div>
              <div class="efficiency-desc">AI自动识别+智能推荐，从2小时手动配置缩短至5分钟</div>
              <div class="efficiency-tag">效率提升 <span class="tag-highlight">24倍</span></div>
            </div>
            <div class="efficiency-card">
              <div class="efficiency-icon" style="background: #409EFF;">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="efficiency-number">异步处理 → 不阻塞前端</div>
              <div class="efficiency-title">数据处理方式</div>
              <div class="efficiency-desc">后台异步处理引擎，支持实时进度查看，大文件也能流畅操作</div>
              <div class="efficiency-tag">用户体验 <span class="tag-highlight">优化</span></div>
            </div>
            <div class="efficiency-card">
              <div class="efficiency-icon" style="background: #e6a23c;">
                <el-icon size="24"><User /></el-icon>
              </div>
              <div class="efficiency-number">专业工程师 → 普通用户</div>
              <div class="efficiency-title">使用门槛</div>
              <div class="efficiency-desc">零代码操作，AI自动完成识别与规则配置，无需专业知识</div>
              <div class="efficiency-tag">门槛降低 <span class="tag-highlight">100%</span></div>
            </div>
            <div class="efficiency-card">
              <div class="efficiency-icon" style="background: #67c23a;">
                <el-icon size="24"><Money /></el-icon>
              </div>
              <div class="efficiency-number">主流大模型 → 灵活选择</div>
              <div class="efficiency-title">模型配置</div>
              <div class="efficiency-desc">支持云端API（OpenAI/DeepSeek/千问等）和本地部署（Ollama/LM Studio），按需选择</div>
              <div class="efficiency-tag">本地化部署 <span class="tag-highlight">可选</span></div>
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
            <div class="quick-action-icon" style="background: #f0f0f0;">
              <el-icon size="20" style="color: #666;"><component :is="action.icon" /></el-icon>
            </div>
            <span class="quick-action-title">{{ action.title }}</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快速脱敏工作流入口 -->
    <el-row class="section">
      <el-col :span="24">
        <el-card shadow="never" class="section-card workflow-entry-card">
          <template #header>
            <div class="section-header">
              <div class="section-header-left">
                <span class="section-title">快速脱敏工作流</span>
                <el-tag type="danger" size="small" effect="light" class="new-tag">新</el-tag>
              </div>
              <el-button type="primary" size="small" @click="$router.push('/workflow/express')">
                进入快速脱敏
              </el-button>
            </div>
          </template>
          <div class="workflow-express-entry">
            <div
              v-for="(wf, index) in quickWorkflowSteps"
              :key="index"
              class="wf-entry-step"
              @click="$router.push(wf.route)"
            >
              <div class="wf-step-number" :style="{ background: wf.color }">{{ index + 1 }}</div>
              <div class="wf-step-icon" :style="{ background: wf.color + '22', color: wf.color }">
                <el-icon size="20"><component :is="wf.icon" /></el-icon>
              </div>
              <div class="wf-step-info">
                <div class="wf-step-title">{{ wf.title }}</div>
                <div class="wf-step-desc">{{ wf.description }}</div>
              </div>
              <el-icon v-if="index < quickWorkflowSteps.length - 1" class="wf-step-arrow" size="16"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
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
              <div class="stat-icon" style="background: #f0f0f0;">
                <el-icon size="24" style="color: #666;"><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_datasets || 0 }}</div>
                <div class="stat-label">数据集</div>
              </div>
            </div>
            <div class="stat-box" @click="$router.push('/detection/tasks')">
              <div class="stat-icon" style="background: #f0f0f0;">
                <el-icon size="24" style="color: #666;"><Search /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_detection_tasks || 0 }}</div>
                <div class="stat-label">识别任务</div>
              </div>
            </div>
            <div class="stat-box" @click="$router.push('/desensitization/tasks')">
              <div class="stat-icon" style="background: #f0f0f0;">
                <el-icon size="24" style="color: #666;"><Lock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_desensitization_tasks || 0 }}</div>
                <div class="stat-label">脱敏任务</div>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-icon" style="background: #f0f0f0;">
                <el-icon size="24" style="color: #666;"><Warning /></el-icon>
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
            <el-tab-pane label="AI识别" name="ai-detection">
              <div class="task-list">
                <div v-if="recentAiDetectionTasks.length === 0" class="task-empty">
                  <el-empty description="暂无AI识别任务" :image-size="60" />
                </div>
                <div
                  v-for="task in recentAiDetectionTasks"
                  :key="task.id"
                  class="task-item"
                  @click="$router.push('/ai/detection?taskId=' + task.id)"
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
                    <el-tag v-if="task.found_count > 0" type="danger" effect="dark" size="small">
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
            <el-tab-pane label="AI脱敏" name="ai-desensitization">
              <div class="task-list">
                <div v-if="recentAiDesensitizationTasks.length === 0" class="task-empty">
                  <el-empty description="暂无AI脱敏任务" :image-size="60" />
                </div>
                <div
                  v-for="task in recentAiDesensitizationTasks"
                  :key="task.id"
                  class="task-item"
                  @click="$router.push('/ai/detection?taskId=' + task.id)"
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
  Connection, View, Cpu, Key, TrendCharts,
  ArrowRight, DataAnalysis, Setting, Tickets, ChatDotRound, MagicStick,
  ScaleToOriginal, Money, User, Timer
} from '@element-plus/icons-vue'
import { getDashboardStats } from '@/api/dashboard'

const router = useRouter()

const stats = ref({})
const recentDetectionTasks = ref([])
const recentDesensitizationTasks = ref([])
const recentAiDetectionTasks = ref([])
const recentAiDesensitizationTasks = ref([])
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

const compareItems = [
  {
    feature: '敏感识别准确率',
    emoji: '🎯',
    accent: '#f43f5e',
    traditional: '人工配置正则规则，误报率高，新型敏感数据无法识别，严重依赖经验积累',
    our: '深度学习语义理解，自动识别上下文语义，准确率高达 95% 以上',
    advantageNum: '10x',
    advantageDesc: '准确率提升'
  },
  {
    feature: '规则配置时间',
    emoji: '⚡',
    accent: '#f59e0b',
    traditional: '手动编写脱敏规则，专业门槛极高，单个任务配置耗时 2-4 小时',
    our: 'AI 自动匹配最优脱敏策略，一键完成配置，仅需 5 分钟',
    advantageNum: '95%',
    advantageDesc: '时间节省'
  },
  {
    feature: '识别-脱敏流程',
    emoji: '🔗',
    accent: '#8b5cf6',
    traditional: '识别与脱敏流程割裂，需手动导出导入数据，流程断裂效率低下',
    our: '识别→推荐→脱敏→报告，全流程自动化闭环，无缝衔接零断点',
    advantageNum: '100%',
    advantageDesc: '流程贯通'
  },
  {
    feature: '跨表一致性',
    emoji: '🔐',
    accent: '#06b6d4',
    traditional: '随机脱敏致同一数据在不同表结果不一致，破坏关联关系且难以追溯',
    our: '基于密钥的确定性脱敏算法，30组独立密钥隔离，跨表结果完全一致',
    advantageNum: '独创',
    advantageDesc: '行业首创'
  },
  {
    feature: '多语言覆盖',
    emoji: '🌐',
    accent: '#10b981',
    traditional: '仅支持中英文场景，多语言环境需额外定制开发，周期长成本高',
    our: '中·英·日·韩·法·德，六种语言自动检测识别，开箱即用零配置',
    advantageNum: '6x',
    advantageDesc: '语言覆盖'
  },
  {
    feature: '部署与成本',
    emoji: '💎',
    accent: '#6366f1',
    traditional: '依赖第三方云服务 API，按调用量计费，敏感数据有出域安全风险',
    our: '支持本地私有化部署，零 API 调用费用，数据完全不出域，安全合规',
    advantageNum: '0元',
    advantageDesc: '额外成本'
  }
]

const quickActions = [
  {
    title: 'AI智能识别',
    icon: 'Cpu',
    route: '/ai/detection'
  },
  {
    title: 'AI智能脱敏',
    icon: 'MagicStick',
    route: '/ai/detection'
  },
  {
    title: '导入数据',
    icon: 'Upload',
    route: '/datasets/upload'
  },
  {
    title: '识别任务',
    icon: 'Search',
    route: '/detection/tasks'
  },
  {
    title: '脱敏任务',
    icon: 'Lock',
    route: '/desensitization/tasks'
  },
  {
    title: '规则管理',
    icon: 'Setting',
    route: '/desensitization/rules'
  },
  {
    title: '运营报表',
    icon: 'TrendCharts',
    route: '/report/platform'
  },
  {
    title: '用户手册',
    icon: 'DocumentChecked',
    route: '/help/manual'
  }
]

const quickWorkflowSteps = [
  {
    title: '导入数据',
    description: '上传文件或连接数据库导入',
    color: '#667eea',
    icon: 'Upload',
    route: '/datasets/upload'
  },
  {
    title: '识别敏感数据',
    description: '规则引擎或AI大模型自动扫描',
    color: '#f5576c',
    icon: 'Search',
    route: '/detection/tasks/create'
  },
  {
    title: '配置脱敏并执行',
    description: '智能推荐策略，预览确认后执行',
    color: '#4facfe',
    icon: 'Lock',
    route: '/desensitization/tasks/create'
  },
  {
    title: '查看报告与导出',
    description: 'HTML预览/Markdown下载',
    color: '#11998e',
    icon: 'Tickets',
    route: '/desensitization/tasks'
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
    title: 'AI智能识别',
    description: '大模型自动识别敏感字段，准确率95%+',
    color: '#f5576c',
    icon: 'Cpu',
    route: '/ai/detection'
  },
  {
    title: 'AI规则推荐',
    description: '智能匹配最优脱敏规则，一键配置',
    color: '#e6a23c',
    icon: 'MagicStick',
    route: '/desensitization/tasks/create'
  },
  {
    title: '预览确认',
    description: '可视化前后对比，安全确认',
    color: '#4facfe',
    icon: 'View',
    route: '/desensitization/tasks'
  },
  {
    title: '执行脱敏',
    description: '关联仿真算法，跨表一致性保障',
    color: '#67c23a',
    icon: 'Lock',
    route: '/desensitization/tasks'
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
    icon: MagicStick,
    title: 'AI大模型驱动识别',
    description: '基于深度学习大模型，智能理解数据语义，自动识别敏感字段类型，准确率高达95%+，远超传统正则匹配',
    tags: [
      { text: '大模型', type: 'danger' },
      { text: '95%+准确率', type: 'success' },
      { text: '语义理解', type: 'primary' }
    ]
  },
  {
    icon: ChatDotRound,
    title: '多语言智能识别',
    description: '支持中、英、日、韩、法、德6种语言的敏感数据识别，基于字符集特征自动检测语言',
    tags: [
      { text: '6种语言', type: 'primary' },
      { text: '自动检测', type: 'success' }
    ]
  },
  {
    icon: Connection,
    title: '识别-脱敏一体化',
    description: '识别结果一键跳转脱敏，自动传递数据并推荐最优脱敏规则，三步完成全流程',
    tags: [
      { text: '一键跳转', type: 'warning' },
      { text: '智能推荐', type: 'success' }
    ]
  },
  {
    icon: Key,
    title: '关联仿真脱敏',
    description: '基于密钥的确定性脱敏算法，保证跨表数据一致性，30组独立密钥安全隔离',
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
    tags: [
      { text: '实时预览', type: 'success' },
      { text: '安全确认', type: 'danger' }
    ]
  },
  {
    icon: Document,
    title: '多种报告格式',
    description: '支持HTML在线预览和Markdown格式下载，方便存档、分享和版本管理',
    tags: [
      { text: 'HTML预览', type: 'primary' },
      { text: 'MD下载', type: 'success' }
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
    recentAiDetectionTasks.value = res.data.recent_tasks?.ai_detection || []
    recentAiDesensitizationTasks.value = res.data.recent_tasks?.ai_desensitization || []
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

/* 快速脱敏工作流入口 */
.workflow-entry-card {
  border: 1px solid #e8e8e8;
}

.workflow-entry-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f4f8 100%);
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-tag {
  animation: pulse-tag 2s infinite;
}

@keyframes pulse-tag {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.workflow-express-entry {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 8px 0;
}

.wf-entry-step {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  cursor: pointer;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
  position: relative;
}

.wf-entry-step:hover {
  background: #f5f7fa;
  transform: translateY(-1px);
}

.wf-step-number {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.wf-step-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.wf-step-info {
  flex: 1;
  min-width: 0;
}

.wf-step-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.wf-step-desc {
  font-size: 11px;
  color: #909399;
  line-height: 1.3;
}

.wf-step-arrow {
  color: #dcdfe6;
  flex-shrink: 0;
  margin: 0 4px;
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
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.workflow-step {
  flex: 0 0 auto;
  min-width: 180px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 14px;
  border-radius: 8px;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  height: 90px;
}

.workflow-step:hover {
  background: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.workflow-step:not(:last-child) {
  /* margin-right removed, using gap instead */
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

  .ai-arch-flow {
    flex-wrap: wrap;
    gap: 16px;
  }

  .ai-arch-arrow {
    transform: rotate(90deg);
  }

  .efficiency-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .compare-modern-wrapper {
    grid-template-columns: 1fr;
  }

  .compare-card-body {
    flex-direction: column;
    gap: 12px;
  }

  .compare-vs-zone {
    flex-direction: row;
    width: 100%;
    height: 28px;
  }

  .vs-line {
    width: 100%;
    height: 1px;
    flex: 1;
    margin-top: 0;
    margin-left: 6px;
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

  .efficiency-grid {
    grid-template-columns: 1fr;
  }
}

/* AI大模型技术架构 */
.ai-arch-flow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px;
  flex-wrap: nowrap;
}

.ai-arch-step {
  flex: 1;
  text-align: center;
  min-width: 0;
}

.ai-arch-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.ai-arch-title {
  font-size: 13px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.ai-arch-desc {
  font-size: 11px;
  color: #606266;
  line-height: 1.5;
}

.ai-arch-arrow {
  color: #c0c4cc;
  flex-shrink: 0;
}

/* ===================== 与传统方案对比 - Apple/GitHub 极简风格 ===================== */
.compare-new-card {
  border: 1px solid #d0d7de;
  border-radius: 12px;
  background: #fff;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  border-top: 1px solid #d0d7de;
}

.compare-item {
  padding: 24px 20px 20px;
  border-right: 1px solid #d0d7de;
  border-bottom: 1px solid #d0d7de;
  transition: background 0.2s;
}

.compare-item:nth-child(3n) {
  border-right: none;
}

.compare-item:nth-child(n+4) {
  border-bottom: none;
}

.compare-item:hover {
  background: #f6f8fa;
}

.compare-item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.compare-item-icon {
  font-size: 24px;
  line-height: 1;
}

.compare-item-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2328;
}

.compare-item-row {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.compare-col {
  flex: 1;
  min-width: 0;
}

.compare-col-label {
  font-size: 11px;
  font-weight: 500;
  color: #8b949e;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  display: block;
}

.compare-col-label.new-label {
  color: #0969da;
}

.compare-col-text {
  font-size: 13px;
  line-height: 1.65;
  color: #656d76;
  margin: 0;
}

.compare-col-text.new-text {
  color: #1f2328;
}

.compare-col-divider {
  display: flex;
  align-items: flex-start;
  padding-top: 22px;
  flex-shrink: 0;
}

.compare-item-stat {
  display: flex;
  align-items: baseline;
  gap: 6px;
  padding-top: 10px;
  border-top: 1px solid #d0d7de;
}

.compare-stat-num {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent, #d1242f);
  letter-spacing: -0.3px;
}

.compare-stat-desc {
  font-size: 12px;
  color: #656d76;
  font-weight: 500;
}

/* ===================== 效率优势卡片 - 现代化设计 ===================== */
.efficiency-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.efficiency-card {
  text-align: center;
  padding: 28px 18px 24px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid #e8eaed;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  position: relative;
  overflow: hidden;
}

.efficiency-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.efficiency-card:hover {
  border-color: #c4cdd5;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.efficiency-card:hover::before {
  opacity: 1;
}

.efficiency-card:nth-child(1)::before {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
}

.efficiency-card:nth-child(2)::before {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.efficiency-card:nth-child(3)::before {
  background: linear-gradient(135deg, #ffecd2, #fcb69f);
}

.efficiency-card:nth-child(4)::before {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}

.efficiency-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin: 0 auto 16px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.efficiency-card:hover .efficiency-icon {
  transform: scale(1.08);
}

.efficiency-number {
  font-size: 20px;
  font-weight: 900;
  color: #1a1a2e;
  margin-bottom: 8px;
  line-height: 1.2;
  letter-spacing: -0.3px;
}

.efficiency-title {
  font-size: 14px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 10px;
  letter-spacing: 0.3px;
}

.efficiency-desc {
  font-size: 12px;
  color: #8e8e93;
  line-height: 1.7;
  margin-bottom: 14px;
}

.efficiency-tag {
  font-size: 12px;
  color: #8e8e93;
  font-weight: 600;
}

.tag-highlight {
  color: #f5576c;
  font-size: 17px;
  font-weight: 900;
  letter-spacing: -0.3px;
}

.efficiency-title {
  font-size: 14px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.efficiency-desc {
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
}

.efficiency-tag {
  font-size: 12px;
  color: #606266;
  font-weight: 600;
}

.tag-highlight {
  color: #f5576c;
  font-size: 16px;
  font-weight: 800;
}
</style>
