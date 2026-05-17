<template>
  <div class="create-task">
    <el-card>
      <template #header>
        <span>创建脱敏任务</span>
      </template>
      
      <el-steps :active="activeStep" finish-status="success" simple>
        <el-step title="选择数据" />
        <el-step title="配置规则" />
        <el-step title="预览确认" />
        <el-step title="执行脱敏" />
      </el-steps>
      
      <div v-if="activeStep === 0" style="margin-top: 20px;">
        <el-alert title="选择要脱敏的数据来源" type="info" :closable="false" style="margin-bottom: 20px;" />
        <el-radio-group v-model="sourceType">
          <el-radio-button label="dataset">数据集</el-radio-button>
          <el-radio-button label="detection">识别结果</el-radio-button>
        </el-radio-group>
        
        <div v-if="sourceType === 'dataset'" style="margin-top: 20px;">
          <el-table :data="datasets" @row-click="selectDataset" highlight-current-row>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="row_count" label="行数" />
          </el-table>
        </div>
        
        <div v-if="sourceType === 'detection'" style="margin-top: 20px;">
          <el-alert title="从识别结果自动加载需脱敏的列" type="success" :closable="false" />
        </div>
      </div>
      
      <div v-if="activeStep === 1" style="margin-top: 20px;">
        <el-form :model="taskForm" label-width="120px">
          <el-form-item label="任务名称">
            <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
          </el-form-item>
          
          <el-form-item label="脱敏模式">
            <el-radio-group v-model="desensitizationMode" @change="onModeChange">
              <el-radio label="manual">手动配置规则</el-radio>
              <el-radio label="auto">自动识别并脱敏</el-radio>
            </el-radio-group>
            <el-tooltip content="自动模式下，系统会在处理过程中为每个字段智能匹配最合适的脱敏规则" placement="top">
              <el-icon style="margin-left: 8px; cursor: help; color: #909399;"><QuestionFilled /></el-icon>
            </el-tooltip>
          </el-form-item>
          
          <!-- 手动配置模式 -->
          <template v-if="desensitizationMode === 'manual'">
            <el-form-item label="字段规则配置">
              <div style="margin-bottom: 10px;">
                <el-button type="success" size="small" @click="autoDetectRules" :loading="detecting">
                  <el-icon><MagicStick /></el-icon>
                  自动检测
                </el-button>
                <el-tooltip content="系统会自动分析数据样本，为每个字段推荐最合适的脱敏规则" placement="top">
                  <el-icon style="margin-left: 8px; cursor: help; color: #909399;"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-table :data="fieldConfigList" size="small">
                <el-table-column prop="column" label="字段名" width="150" />
                <el-table-column prop="language" label="检测语言" width="120">
                  <template #default="{ row }">
                    <el-select 
                      v-model="row.language" 
                      size="small"
                      placeholder="选择语言"
                    >
                      <el-option label="中文" value="zh" />
                      <el-option label="英语" value="en" />
                      <el-option label="日语" value="ja" />
                      <el-option label="韩语" value="ko" />
                      <el-option label="法语" value="fr" />
                      <el-option label="德语" value="de" />
                      <el-option label="通用" value="all" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="脱敏方式" width="150">
                  <template #default="{ row }">
                    <el-select 
                      v-model="row.desensitization_method" 
                      placeholder="选择方式" 
                      size="small"
                      @change="onMethodChange(row)"
                    >
                      <el-option label="完全遮盖" value="full_mask">
                        <span style="float: left">🔴 完全遮盖</span>
                      </el-option>
                      <el-option label="仿真造数" value="simulation">
                        <span style="float: left">🟢 仿真造数</span>
                      </el-option>
                      <el-option label="关联造数" value="deterministic_simulation">
                        <span style="float: left">🔵 关联造数</span>
                      </el-option>
                      <el-option label="部分遮盖" value="partial_mask">
                        <span style="float: left">🟡 部分遮盖</span>
                      </el-option>
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="脱敏规则">
                  <template #default="{ row }">
                    <el-select 
                      v-model="row.rule_id" 
                      placeholder="先选脱敏方式" 
                      size="small"
                      :disabled="!row.desensitization_method"
                      clearable
                    >
                      <el-option
                        v-for="rule in getRulesByMethodAndLanguage(row.desensitization_method, row.language)"
                        :key="rule.id"
                        :label="rule.name"
                        :value="rule.id"
                      >
                        <span>{{ rule.name }}</span>
                        <span style="float: right; color: #8492a6; font-size: 12px">
                          {{ rule.example?.before }} → {{ rule.example?.after }}
                        </span>
                      </el-option>
                    </el-select>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>
            
            <el-form-item label="关联密钥">
              <el-select v-model="taskForm.key_id" placeholder="选择密钥（用于关联仿真）" clearable>
                <el-option
                  v-for="key in keys"
                  :key="key.id"
                  :label="key.alias"
                  :value="key.id"
                />
              </el-select>
            </el-form-item>
          </template>
          
          <!-- 自动识别模式提示 -->
          <template v-else>
            <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
              <template #title>
                <div>
                  <strong>🤖 自动识别模式说明：</strong>
                  <ul style="margin: 8px 0 0 20px; padding: 0;">
                    <li>系统将自动分析每个字段的数据特征</li>
                    <li>智能匹配最适合的语言和脱敏规则</li>
                    <li>每行数据的每个字段可能使用不同的规则</li>
                    <li>脱敏结果会展示具体使用的语言和规则</li>
                  </ul>
                </div>
              </template>
            </el-alert>
          </template>
          
          <el-form-item label="输出方式">
            <el-radio-group v-model="taskForm.output_mode">
              <el-radio label="copy">生成副本（推荐）</el-radio>
              <el-radio label="overwrite">覆盖原数据</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
      
      <div v-if="activeStep === 2" style="margin-top: 20px;">
        <h4>脱敏效果预览（前10条）</h4>
        
        <!-- 自动模式提示 -->
        <el-alert v-if="desensitizationMode === 'auto'" type="success" :closable="false" style="margin-bottom: 15px;">
          <template #title>
            <strong>✅ 自动识别完成</strong> - 系统已为每个字段智能匹配了最合适的脱敏规则
          </template>
        </el-alert>
        
        <el-table :data="previewData" size="small" style="margin-top: 10px;" border>
          <el-table-column type="index" label="行号" width="80" />
          <el-table-column
            v-for="col in previewColumns"
            :key="col"
            :label="col"
            min-width="200"
          >
            <template #default="{ row }">
              <div v-if="row.columns[col]" class="cell-content">
                <div class="original">原: {{ row.columns[col].original }}</div>
                <div class="desensitized">脱: {{ row.columns[col].desensitized }}</div>
                
                <!-- 自动模式下显示详细规则信息 -->
                <div v-if="desensitizationMode === 'auto' && row.columns[col].rule_info" class="rule-info">
                  <el-tag size="small" type="info" style="margin-right: 4px;">
                    {{ languageMap[row.columns[col].rule_info.language] || row.columns[col].rule_info.language }}
                  </el-tag>
                  <el-tag size="small" type="primary">
                    {{ row.columns[col].rule_info.rule_name }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 自动模式统计信息 -->
        <div v-if="desensitizationMode === 'auto' && autoDetectStats" style="margin-top: 15px; padding: 15px; background: #f5f7fa; border-radius: 4px;">
          <h5 style="margin: 0 0 10px 0;">📊 自动识别统计</h5>
          <el-descriptions :column="3" size="small" border>
            <el-descriptions-item label="检测字段数">{{ autoDetectStats.total_fields }}</el-descriptions-item>
            <el-descriptions-item label="识别语言分布">
              <span v-for="(count, lang) in autoDetectStats.language_dist" :key="lang">
                <el-tag size="small" style="margin-right: 4px;">{{ languageMap[lang] }}: {{ count }}</el-tag>
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="使用规则数">{{ autoDetectStats.unique_rules }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      
      <div v-if="activeStep === 3" style="margin-top: 20px;">
        <el-result icon="success" title="配置完成" sub-title="点击开始执行脱敏任务">
          <template #extra>
            <el-button type="primary" @click="submitTask" :loading="submitting">开始脱敏</el-button>
          </template>
        </el-result>
      </div>
      
      <div style="margin-top: 20px; text-align: center;" v-if="activeStep < 3">
        <el-button v-if="activeStep > 0" @click="activeStep--">上一步</el-button>
        <el-button type="primary" @click="nextStep">下一步</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, QuestionFilled } from '@element-plus/icons-vue'
import { getDatasetList } from '@/api/dataset'
import { getDesensitizationRules, getDesensitizationKeys, previewDesensitization, createDesensitizationTask, autoDetectRules as autoDetectApi } from '@/api/desensitization'
import { getDetectionTask, getDetectionResults } from '@/api/detection'

const route = useRoute()
const router = useRouter()

const activeStep = ref(0)
const sourceType = ref('dataset')
const loading = ref(false)
const submitting = ref(false)
const detecting = ref(false)  // 自动检测加载状态
const desensitizationMode = ref('manual')  // 'manual' 或 'auto'
const autoDetectStats = ref(null)  // 自动识别统计信息

const datasets = ref([])
const rules = ref([])
const keys = ref([])
const previewData = ref([])
const previewColumns = ref([])

const taskForm = ref({
  name: '',
  dataset_id: null,
  source_type: 'dataset',
  detection_task_id: null,
  field_rules: {},
  output_mode: 'copy',
  key_id: null
})

const fieldConfigList = ref([])

const languageMap = {
  zh: '中文',
  en: '英语',
  ja: '日语',
  ko: '韩语',
  fr: '法语',
  de: '德语'
}

const desensitizationMethodMap = {
  'full_mask': '完全遮盖',
  'simulation': '仿真造数',
  'deterministic_simulation': '关联造数',
  'partial_mask': '部分遮盖'
}

const loadDatasets = async () => {
  try {
    const res = await getDatasetList({ page: 1, page_size: 100 })
    datasets.value = res.data.items || []
  } catch (e) {
    console.error(e)
  }
}

const loadRules = async () => {
  try {
    const res = await getDesensitizationRules({})
    rules.value = res.data || []
    console.log('[DEBUG] 加载规则成功:', rules.value.length, '条')
    if (rules.value.length > 0) {
      console.log('[DEBUG] 第一条规则:', rules.value[0])
      console.log('[DEBUG] 规则字段检查:', {
        has_desensitization_method: 'desensitization_method' in rules.value[0],
        desensitization_method_value: rules.value[0].desensitization_method
      })
    }
  } catch (e) {
    console.error('[ERROR] 加载规则失败:', e)
  }
}

const loadKeys = async () => {
  try {
    const res = await getDesensitizationKeys()
    keys.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const getRulesByLanguage = (lang) => {
  return rules.value.filter(r => r.language === lang || r.language === 'all')
}

const getRulesByMethodAndLanguage = (method, lang) => {
  if (!method) return []
  
  console.log('[DEBUG] 筛选规则:', { method, lang, totalRules: rules.value.length })
  
  const filtered = rules.value.filter(r => {
    // 匹配脱敏方式（优先使用 desensitization_method，如果为空则通过 category 推断）
    let methodMatch = false
    if (r.desensitization_method) {
      methodMatch = r.desensitization_method === method
    } else if (r.category) {
      // 如果没有 desensitization_method，根据 category 推断
      // mask 类别包含 full_mask 和 partial_mask
      // simulation 类别对应 simulation
      if (method === 'simulation') {
        methodMatch = r.category === 'simulation'
      } else if (method === 'full_mask' || method === 'partial_mask') {
        methodMatch = r.category === 'mask'
      }
    }
    
    // 匹配语言（精确匹配或通用）
    const langMatch = r.language === lang || r.language === 'all'
    
    if (methodMatch && langMatch) {
      console.log('[DEBUG] 匹配规则:', r.name, 'desensitization_method:', r.desensitization_method, 'category:', r.category, 'language:', r.language)
    }
    
    return methodMatch && langMatch
  })
  
  console.log('[DEBUG] 筛选结果:', filtered.length, '条规则')
  if (filtered.length > 0) {
    console.log('[DEBUG] 匹配的规则列表:', filtered.map(r => ({ name: r.name, method: r.desensitization_method, category: r.category })))
  }
  return filtered
}

const onMethodChange = (row) => {
  // 切换脱敏方式时，清空已选择的规则
  row.rule_id = null
}

const onModeChange = () => {
  // 切换模式时，重置统计信息
  autoDetectStats.value = null
  if (desensitizationMode.value === 'auto') {
    ElMessage.info('已切换到自动识别模式，系统将智能匹配脱敏规则')
  }
}

const selectDataset = (row) => {
  taskForm.value.dataset_id = row.id
  taskForm.value.name = `${row.name}_脱敏任务`
  
  fieldConfigList.value = (row.columns || []).map(col => ({
    column: col,
    language: 'zh',
    desensitization_method: null,  // 新增：脱敏方式
    rule_id: null
  }))
  
  activeStep.value = 1
}

// 自动检测规则
const autoDetectRules = async () => {
  if (!taskForm.value.dataset_id) {
    ElMessage.warning('请先选择数据集')
    return
  }
  
  detecting.value = true
  try {
    const res = await autoDetectApi(taskForm.value.dataset_id, 50)
    const suggestions = res.data
    
    console.log('[DEBUG] 自动检测结果:', suggestions)
    
    // 更新字段配置
    let updatedCount = 0
    fieldConfigList.value.forEach(field => {
      if (suggestions[field.column]) {
        const suggestion = suggestions[field.column]
        field.language = suggestion.language
        field.desensitization_method = suggestion.desensitization_method
        field.rule_id = suggestion.rule_id
        updatedCount++
        
        console.log(`[DEBUG] 字段 ${field.column}:`, {
          language: suggestion.language,
          method: suggestion.desensitization_method,
          rule: suggestion.rule_name,
          confidence: suggestion.confidence
        })
      }
    })
    
    ElMessage.success(`自动检测完成，已为 ${updatedCount} 个字段推荐脱敏规则`)
  } catch (e) {
    console.error('[ERROR] 自动检测失败:', e)
    ElMessage.error('自动检测失败：' + (e.response?.data?.detail || e.message))
  } finally {
    detecting.value = false
  }
}

const nextStep = async () => {
  if (activeStep.value === 1) {
    // 手动模式：需要配置规则
    if (desensitizationMode.value === 'manual') {
      const fieldRules = {}
      fieldConfigList.value.forEach(item => {
        if (item.rule_id) {
          fieldRules[item.column] = item.rule_id
        }
      })
      taskForm.value.field_rules = fieldRules
      
      console.log('[DEBUG] 字段规则配置:', fieldRules)
      console.log('[DEBUG] 字段配置列表:', fieldConfigList.value.map(item => ({
        column: item.column,
        language: item.language,
        desensitization_method: item.desensitization_method,
        rule_id: item.rule_id
      })))
      
      if (Object.keys(fieldRules).length === 0) {
        ElMessage.warning('请至少配置一个字段的脱敏规则')
        return
      }
      
      try {
        const res = await previewDesensitization({
          dataset_id: taskForm.value.dataset_id,
          field_rules: fieldRules,
          key_id: taskForm.value.key_id,
          limit: 10
        })
        previewData.value = res.data || []
        if (previewData.value.length > 0) {
          previewColumns.value = Object.keys(previewData.value[0].columns || {})
        }
      } catch (e) {
        console.error(e)
        return
      }
    } 
    // 自动模式：使用auto_detect参数
    else {
      try {
        const res = await previewDesensitization({
          dataset_id: taskForm.value.dataset_id,
          auto_detect: true,  // 启用自动识别
          key_id: taskForm.value.key_id,
          limit: 10
        })
        previewData.value = res.data || []
        if (previewData.value.length > 0) {
          previewColumns.value = Object.keys(previewData.value[0].columns || {})
          
          // 统计自动识别结果
          calculateAutoDetectStats()
        }
      } catch (e) {
        console.error('[ERROR] 自动识别预览失败:', e)
        ElMessage.error('自动识别失败：' + (e.response?.data?.detail || e.message))
        return
      }
    }
  }
  
  activeStep.value++
}

const submitTask = async () => {
  submitting.value = true
  try {
    // 自动模式下，设置auto_detect参数
    if (desensitizationMode.value === 'auto') {
      taskForm.value.auto_detect = true
      taskForm.value.field_rules = {}  // 清空手动配置的规则
    }
    
    await createDesensitizationTask(taskForm.value)
    ElMessage.success('脱敏任务已创建')
    router.push('/desensitization/tasks')
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

// 计算自动识别统计信息
const calculateAutoDetectStats = () => {
  if (!previewData.value || previewData.value.length === 0) {
    autoDetectStats.value = null
    return
  }
  
  const languageDist = {}
  const ruleSet = new Set()
  let totalFields = 0
  
  previewData.value.forEach(row => {
    if (row.columns) {
      Object.values(row.columns).forEach(col => {
        if (col.rule_info) {
          totalFields++
          const lang = col.rule_info.language
          languageDist[lang] = (languageDist[lang] || 0) + 1
          ruleSet.add(col.rule_info.rule_id)
        }
      })
    }
  })
  
  autoDetectStats.value = {
    total_fields: totalFields,
    language_dist: languageDist,
    unique_rules: ruleSet.size
  }
}

const loadDetectionResult = async (taskId) => {
  try {
    const taskRes = await getDetectionTask(taskId)
    const task = taskRes.data
    taskForm.value.name = `${task.name}_脱敏任务`

    const resultsRes = await getDetectionResults(taskId, { page: 1, page_size: 1000 })
    const results = resultsRes.data.items || []

    const columnMap = {}
    results.forEach(r => {
      if (!columnMap[r.column_name]) {
        columnMap[r.column_name] = {
          column: r.column_name,
          language: r.detected_language || 'zh',
          desensitization_method: null,
          rule_id: null,
          suggestion: r.desensitization_suggestion
        }
      }
    })

    fieldConfigList.value = Object.values(columnMap)
    if (fieldConfigList.value.length > 0) {
      activeStep.value = 1
    }
  } catch (e) {
    console.error('[ERROR] 加载识别结果失败:', e)
    ElMessage.error('加载识别结果失败')
  }
}

onMounted(() => {
  loadDatasets()
  loadRules()
  loadKeys()

  const datasetId = route.query.dataset_id
  const detectionTaskId = route.query.detection_task_id

  if (datasetId) {
    taskForm.value.dataset_id = parseInt(datasetId)
    if (detectionTaskId) {
      taskForm.value.source_type = 'detection'
      taskForm.value.detection_task_id = parseInt(detectionTaskId)
      sourceType.value = 'detection'
      loadDetectionResult(parseInt(detectionTaskId))
    }
  }
})
</script>

<style scoped lang="scss">
.create-task {
  padding: 20px;
}

.original {
  color: #909399;
  text-decoration: line-through;
}
.desensitized {
  color: #668F80;
  font-weight: bold;
}
.cell-content {
  padding: 4px 0;
}
.rule-info {
  margin-top: 6px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* 步骤条玻璃效果 */
:deep(.el-steps--simple) {
  background: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.6) !important;
  border-radius: 12px !important;
}

/* 表格行悬浮效果 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(184, 212, 227, 0.12) !important;
  }
}

/* 单选按钮组玻璃效果 */
:deep(.el-radio-group) {
  .el-radio-button__inner {
    backdrop-filter: blur(8px);
    transition: all 0.15s cubic-bezier(0.22, 1, 0.36, 1);
  }
}

/* 标签玻璃效果 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

/* 警告提示玻璃效果 */
:deep(.el-alert) {
  border-radius: 12px !important;
  backdrop-filter: blur(8px);
}
</style>
