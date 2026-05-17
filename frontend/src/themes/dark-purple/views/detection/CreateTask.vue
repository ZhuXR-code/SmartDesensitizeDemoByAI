<template>
  <div class="create-task">
    <el-card>
      <template #header>
        <span>创建识别任务</span>
      </template>
      
      <el-steps :active="activeStep" finish-status="success" simple>
        <el-step title="选择数据集" />
        <el-step title="配置规则" />
        <el-step title="确认启动" />
      </el-steps>
      
      <div v-if="activeStep === 0" style="margin-top: 20px;">
        <el-alert title="请选择一个数据集进行敏感数据识别" type="info" :closable="false" style="margin-bottom: 20px;" />
        <el-table :data="datasets" @row-click="selectDataset" highlight-current-row>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="row_count" label="行数" />
          <el-table-column prop="column_count" label="列数" />
        </el-table>
        <el-pagination
          v-model:current-page="datasetPage"
          v-model:page-size="datasetPageSize"
          :total="datasetTotal"
          layout="prev, pager, next"
          style="margin-top: 10px;"
          @change="loadDatasets"
        />
      </div>
      
      <div v-if="activeStep === 1" style="margin-top: 20px;">
        <el-form :model="taskForm" label-width="120px">
          <el-form-item label="任务名称">
            <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
          </el-form-item>
          <el-form-item label="规则集">
            <el-select v-model="taskForm.rule_set_id" placeholder="默认使用全部规则" clearable>
              <el-option
                v-for="rs in ruleSets"
                :key="rs.id"
                :label="rs.name"
                :value="rs.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="扫描范围">
            <el-radio-group v-model="scanScope">
              <el-radio label="all">全量扫描</el-radio>
              <el-radio label="custom">指定列</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="选择列" v-if="scanScope === 'custom'">
            <el-checkbox-group v-model="taskForm.scan_columns">
              <el-checkbox
                v-for="col in selectedDatasetColumns"
                :key="col"
                :label="col"
              />
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="语言策略">
            <el-tag type="info">自动检测（根据数据内容智能识别语言）</el-tag>
          </el-form-item>
        </el-form>
      </div>
      
      <div v-if="activeStep === 2" style="margin-top: 20px;">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务名称">{{ taskForm.name }}</el-descriptions-item>
          <el-descriptions-item label="数据集">{{ selectedDatasetName }}</el-descriptions-item>
          <el-descriptions-item label="扫描范围">{{ scanScope === 'all' ? '全量扫描' : taskForm.scan_columns.join(', ') }}</el-descriptions-item>
          <el-descriptions-item label="语言策略">自动检测</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <div style="margin-top: 20px; text-align: center;">
        <el-button v-if="activeStep > 0" @click="activeStep--">上一步</el-button>
        <el-button v-if="activeStep < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-if="activeStep === 2" type="success" @click="submitTask" :loading="submitting">启动任务</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDatasetList } from '@/api/dataset'
import { getRuleSets, createDetectionTask } from '@/api/detection'

const route = useRoute()
const router = useRouter()

const activeStep = ref(0)
const loading = ref(false)
const submitting = ref(false)

const datasets = ref([])
const datasetPage = ref(1)
const datasetPageSize = ref(20)
const datasetTotal = ref(0)

const ruleSets = ref([])
const scanScope = ref('all')

const selectedDataset = ref(null)
const selectedDatasetName = ref('')
const selectedDatasetColumns = ref([])

const taskForm = ref({
  name: '',
  dataset_id: null,
  rule_set_id: null,
  scan_columns: [],
  language_strategy: 'auto'
})

const loadDatasets = async () => {
  try {
    const res = await getDatasetList({ page: datasetPage.value, page_size: datasetPageSize.value })
    datasets.value = res.data.items || []
    datasetTotal.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  }
}

const loadRuleSets = async () => {
  try {
    const res = await getRuleSets()
    ruleSets.value = res.data || []
    console.log('加载规则集成功:', ruleSets.value)
  } catch (e) {
    console.error('加载规则集失败:', e)
  }
}

const selectDataset = (row) => {
  selectedDataset.value = row
  selectedDatasetName.value = row.name
  selectedDatasetColumns.value = row.columns || []
  taskForm.value.dataset_id = row.id
  activeStep.value = 1
}

const nextStep = () => {
  if (activeStep.value === 0) {
    // 第一步：验证是否选择了数据集
    if (!taskForm.value.dataset_id) {
      ElMessage.warning('请先选择一个数据集')
      return
    }
  }
  
  if (activeStep.value === 1) {
    // 第二步：验证任务名称
    if (!taskForm.value.name) {
      ElMessage.warning('请输入任务名称')
      return
    }
    if (scanScope.value === 'all') {
      // 全量扫描时，将 scan_columns 设置为空数组或 undefined
      taskForm.value.scan_columns = []
    }
  }
  activeStep.value++
}

const submitTask = async () => {
  // 验证必填字段
  if (!taskForm.value.dataset_id) {
    ElMessage.error('请先选择一个数据集')
    return
  }
  
  if (!taskForm.value.name) {
    ElMessage.error('请输入任务名称')
    return
  }
  
  submitting.value = true
  try {
    // 构建提交数据，确保格式正确
    const submitData = {
      name: taskForm.value.name,
      dataset_id: parseInt(taskForm.value.dataset_id),  // 确保是整数
      language_strategy: taskForm.value.language_strategy
    }
    
    // 只有在选择指定列时才添加 scan_columns
    if (scanScope.value === 'custom' && taskForm.value.scan_columns && taskForm.value.scan_columns.length > 0) {
      submitData.scan_columns = taskForm.value.scan_columns
    }
    // 全量扫描时不传 scan_columns 字段，让后端使用默认值 null
    
    // rule_set_id 只有在有值时才添加
    if (taskForm.value.rule_set_id) {
      submitData.rule_set_id = parseInt(taskForm.value.rule_set_id)
    }
    
    console.log('提交任务数据:', submitData)
    await createDetectionTask(submitData)
    ElMessage.success('任务创建成功')
    router.push('/detection/tasks')
  } catch (e) {
    console.error('创建任务失败:', e)
    const errorMsg = e.response?.data?.detail
    if (Array.isArray(errorMsg)) {
      // Pydantic 验证错误，显示详细信息
      const details = errorMsg.map(err => `${err.loc?.join('.')}: ${err.msg}`).join('; ')
      ElMessage.error('参数验证失败: ' + details)
    } else {
      ElMessage.error('创建任务失败: ' + (errorMsg || e.message))
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadDatasets()
  loadRuleSets()
  
  const datasetId = route.query.dataset_id
  if (datasetId) {
    const dataset = datasets.value.find(d => d.id === parseInt(datasetId))
    if (dataset) {
      selectDataset(dataset)
    }
  }
})
</script>

<style scoped lang="scss">
.create-task {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 步骤条玻璃效果 - design02 色系 */
:deep(.el-steps--simple) {
  background: rgba(57, 79, 73, 0.4) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(244, 253, 175, 0.1) !important;
  border-radius: 12px !important;
}

/* 表格行悬浮效果 - design02 色系 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(244, 253, 175, 0.08) !important;
  }
}

/* 描述列表玻璃效果 - design02 色系 */
:deep(.el-descriptions__body) {
  background: rgba(57, 79, 73, 0.3) !important;
  backdrop-filter: blur(8px) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(244, 253, 175, 0.1) !important;
}
</style>
