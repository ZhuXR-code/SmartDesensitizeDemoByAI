<template>
  <div class="workflow-express">
    <div class="welcome-section">
      <h1 class="page-title">快速脱敏工作流</h1>
      <p class="page-subtitle">4步完成 数据导入 → 敏感识别 → 脱敏处理 → 报告导出，轻松实现数据安全保护</p>
    </div>

    <div class="steps-indicator">
      <div
        v-for="(step, index) in steps"
        :key="step.key"
        class="indicator-item"
        :class="{
          'is-active': currentStep === step.key,
          'is-completed': completedSteps.includes(step.key),
          'is-disabled': !canAccess(step.key)
        }"
        @click="goToStep(step.key)"
      >
        <div class="indicator-number">
          <el-icon v-if="completedSteps.includes(step.key)" size="18"><Check /></el-icon>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="indicator-label">{{ step.title }}</div>
        <div class="indicator-connector" v-if="index < steps.length - 1">
          <div class="connector-line"></div>
        </div>
      </div>
    </div>

    <div class="step-cards">
      <div
        v-for="(step, index) in steps"
        :key="step.key"
        class="step-card"
        :class="{
          'is-active': currentStep === step.key,
          'is-completed': completedSteps.includes(step.key)
        }"
      >
        <div class="step-card-header" :style="{ background: step.gradient }">
          <div class="step-card-number">{{ index + 1 }}</div>
          <div class="step-card-title">{{ step.title }}</div>
        </div>
        <div class="step-card-body">
          <div class="step-card-desc">{{ step.description }}</div>
          <div class="step-card-details">
            <div v-for="(detail, dIdx) in step.details" :key="dIdx" class="detail-item">
              <el-icon size="14" color="#67C23A"><Select /></el-icon>
              <span>{{ detail }}</span>
            </div>
          </div>
          <div class="step-card-tags">
            <el-tag
              v-for="(tag, tIdx) in step.tags"
              :key="tIdx"
              :type="tag.type"
              size="small"
              effect="light"
            >
              {{ tag.text }}
            </el-tag>
          </div>
          <div class="step-card-actions">
            <el-button
              v-if="!completedSteps.includes(step.key)"
              type="primary"
              size="large"
              @click="executeStep(step)"
            >
              {{ index === 0 ? '开始导入数据' : '去执行' }}
            </el-button>
            <el-button
              v-if="completedSteps.includes(step.key) && !isLastStep(index)"
              type="success"
              size="large"
              @click="executeStep(step)"
            >
              重新执行
            </el-button>
            <div v-if="completedSteps.includes(step.key)" class="completed-badge">
              <el-icon size="16" color="#67C23A"><CircleCheckFilled /></el-icon>
              <span>已完成</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="step-flow-connector">
      <div class="flow-line"></div>
      <div
        v-for="(step, index) in steps"
        :key="step.key"
        class="flow-node"
        :class="{
          'is-active': currentStep === step.key,
          'is-completed': completedSteps.includes(step.key)
        }"
        @click="goToStep(step.key)"
      >
        <div class="flow-dot">
          <el-icon v-if="completedSteps.includes(step.key)" size="12"><Check /></el-icon>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="flow-label">{{ step.title }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Check, CircleCheckFilled, Select, Upload, Search, Lock, Tickets } from '@element-plus/icons-vue'

const router = useRouter()
const WORKFLOW_KEY = 'workflow-express-progress'

const completedSteps = ref([])

const steps = [
  {
    key: 'import',
    title: '导入数据',
    description: '将待处理的敏感数据导入平台，支持多种数据源',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    icon: 'Upload',
    details: [
      '支持 Excel (.xlsx/.xls) 格式上传',
      '支持 CSV / TXT / JSON / Markdown / 日志文件',
      '支持直接连接 MySQL / PostgreSQL / Oracle / SQL Server 数据库导入表数据',
      '支持从 Excel 复制数据后通过剪贴板粘贴导入',
      '文件最大支持 100MB，自动识别编码和格式'
    ],
    tags: [
      { text: 'Excel', type: 'primary' },
      { text: 'CSV', type: 'success' },
      { text: '数据库连接', type: 'warning' }
    ],
    route: '/datasets/upload'
  },
  {
    key: 'detect',
    title: '识别敏感数据',
    description: '智能扫描数据，自动发现并标记所有敏感字段',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    icon: 'Search',
    details: [
      '规则引擎识别：基于正则+关键词快速匹配，支持6种语言（中/英/日/韩/法/德）',
      'AI智能识别：基于大模型的语义级敏感判断，准确率95%+',
      '自动识别：姓名、身份证号、手机号、银行卡号、地址、邮箱等20+类敏感数据',
      '置信度评分 0-1，高置信度自动标记，低置信度需要人工复核',
      '识别结果支持一键跳转创建脱敏任务，自动传递数据和推荐规则'
    ],
    tags: [
      { text: '规则引擎', type: 'primary' },
      { text: 'AI大模型', type: 'danger' },
      { text: '多语言', type: 'success' }
    ],
    route: '/detection/tasks/create'
  },
  {
    key: 'desensitize',
    title: '配置并执行脱敏',
    description: '选择或智能推荐脱敏策略，预览确认后执行全量脱敏',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    icon: 'Lock',
    details: [
      '5种脱敏策略：完全遮盖、部分遮盖、仿真造数、关联仿真、固定遮盖',
      '智能推荐：根据识别结果自动匹配最优脱敏规则，一键应用',
      '预览确认：执行前展示10-20条脱敏前后对比数据，确保效果符合预期',
      '关联仿真：基于密钥的确定性脱敏，保证跨表数据一致性',
      '输出模式可选：生成副本（推荐）或覆盖原数据（需二次确认）'
    ],
    tags: [
      { text: '智能推荐', type: 'success' },
      { text: '预览确认', type: 'primary' },
      { text: '跨表一致', type: 'warning' }
    ],
    route: '/desensitization/tasks/create'
  },
  {
    key: 'report',
    title: '查看报告 & 导出',
    description: '生成完整的脱敏工作报告，支持多格式下载',
    gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    icon: 'Tickets',
    details: [
      '脱敏任务完成后自动关联数据集和脱敏结果信息',
      'HTML 在线预览：支持在浏览器中直接查看脱敏前后对比',
      'HTML 下载：完整的脱敏报告，含统计图表和数据表格',
      'Markdown 下载：适合版本管理和开发人员使用',
      '脱敏数据文件下载：支持 XLSX 和 CSV 两种格式，含纯脱敏数据和对比数据'
    ],
    tags: [
      { text: 'HTML预览', type: 'primary' },
      { text: 'Markdown', type: 'success' },
      { text: 'XLSX下载', type: 'warning' }
    ],
    route: '/desensitization/tasks'
  }
]

const currentStep = computed(() => {
  if (completedSteps.value.length === 0) return 'import'
  const completedKeys = steps.map(s => s.key).filter(k => completedSteps.value.includes(k))
  if (completedKeys.length === steps.length) return 'report'
  for (const step of steps) {
    if (!completedSteps.value.includes(step.key)) return step.key
  }
  return 'import'
})

function isLastStep(index) {
  return index === steps.length - 1
}

function canAccess(stepKey) {
  const idx = steps.findIndex(s => s.key === stepKey)
  if (idx === 0) return true
  const prevKey = steps[idx - 1].key
  return completedSteps.value.includes(prevKey)
}

function goToStep(stepKey) {
  if (canAccess(stepKey)) {
    const step = steps.find(s => s.key === stepKey)
    if (step) router.push(step.route)
  }
}

function executeStep(step) {
  router.push(step.route)
}

function loadProgress() {
  try {
    const saved = localStorage.getItem(WORKFLOW_KEY)
    if (saved) {
      completedSteps.value = JSON.parse(saved)
    }
  } catch (e) {
    completedSteps.value = []
  }
}

function saveProgress() {
  localStorage.setItem(WORKFLOW_KEY, JSON.stringify(completedSteps.value))
}

function markStepComplete(stepKey) {
  if (!completedSteps.value.includes(stepKey)) {
    completedSteps.value.push(stepKey)
    saveProgress()
  }
}

function handleReturnFromStep() {
  const query = router.currentRoute.value.query
  if (query.completed) {
    markStepComplete(query.completed)
    router.replace({ query: {} })
  }
}

onMounted(() => {
  loadProgress()
  handleReturnFromStep()
})
</script>

<style scoped>
.workflow-express {
  padding: 20px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  margin-bottom: 32px;
  padding: 24px 28px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: 12px;
  border-left: 4px solid #409EFF;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
}

.steps-indicator {
  display: flex;
  align-items: flex-start;
  margin-bottom: 32px;
  padding: 20px 0;
}

.indicator-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  flex: 1;
}

.indicator-item.is-disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.indicator-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  background: #e4e7ed;
  color: #909399;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.indicator-item.is-active .indicator-number {
  background: #409EFF;
  color: #fff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.indicator-item.is-completed .indicator-number {
  background: #67C23A;
  color: #fff;
}

.indicator-label {
  margin-left: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.indicator-item.is-active .indicator-label {
  color: #409EFF;
  font-weight: 600;
}

.indicator-item.is-completed .indicator-label {
  color: #67C23A;
}

.indicator-connector {
  flex: 1;
  padding: 0 16px;
}

.connector-line {
  height: 2px;
  background: #e4e7ed;
  position: relative;
}

.step-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.step-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.step-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.step-card.is-active {
  border-color: #409EFF;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
}

.step-card.is-completed {
  border-color: #67C23A;
  opacity: 0.85;
}

.step-card-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-card-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.step-card-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.step-card-body {
  padding: 20px;
}

.step-card-desc {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 16px;
  font-weight: 500;
}

.step-card-details {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.detail-item .el-icon {
  margin-top: 3px;
  flex-shrink: 0;
}

.step-card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.step-card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.completed-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #67C23A;
  font-size: 14px;
  font-weight: 500;
}

.step-flow-connector {
  display: none;
}

@media (max-width: 900px) {
  .step-cards {
    grid-template-columns: 1fr;
  }

  .steps-indicator {
    display: none;
  }

  .step-flow-connector {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 16px 0;
    position: relative;
  }

  .flow-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    cursor: pointer;
    position: relative;
    z-index: 1;
    flex: 1;
  }

  .flow-dot {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #e4e7ed;
    color: #909399;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
  }

  .flow-node.is-active .flow-dot {
    background: #409EFF;
    color: #fff;
  }

  .flow-node.is-completed .flow-dot {
    background: #67C23A;
    color: #fff;
  }

  .flow-label {
    font-size: 11px;
    color: #909399;
  }

  .flow-node.is-active .flow-label {
    color: #409EFF;
    font-weight: 600;
  }

  .flow-node.is-completed .flow-label {
    color: #67C23A;
  }

  .flow-line {
    position: absolute;
    top: 12px;
    left: 10%;
    right: 10%;
    height: 2px;
    background: #e4e7ed;
    z-index: 0;
  }
}
</style>
