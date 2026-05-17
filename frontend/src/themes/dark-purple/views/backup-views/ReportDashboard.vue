<template>
  <div class="report-dashboard">
    <el-page-header title="规则校验报告" @back="$router.back()">
      <template #content>
        <span class="page-title">脱敏规则校验报告</span>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>生成报告</span>
            </div>
          </template>

          <el-form :model="form" label-width="120px">
            <el-form-item label="选择数据集" required>
              <el-select v-model="form.dataset_id" placeholder="选择数据集" style="width: 300px;">
                <el-option
                  v-for="ds in datasets"
                  :key="ds.id"
                  :label="ds.name"
                  :value="ds.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="字段规则配置" required>
              <el-table :data="ruleMappings" border size="small" style="width: 100%;">
                <el-table-column label="字段名" width="200">
                  <template #default="scope">
                    <el-input v-model="scope.row.column" placeholder="字段名" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="脱敏规则" min-width="300">
                  <template #default="scope">
                    <el-select v-model="scope.row.rule_id" placeholder="选择规则" size="small" style="width: 100%;">
                      <el-option
                        v-for="rule in allRules"
                        :key="rule.id"
                        :label="rule.name"
                        :value="rule.id"
                      />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100">
                  <template #default="scope">
                    <el-button link type="danger" @click="removeMapping(scope.$index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-button type="primary" link @click="addMapping" style="margin-top: 8px;">
                <el-icon><Plus /></el-icon> 添加字段映射
              </el-button>
            </el-form-item>

            <el-form-item label="报告格式">
              <el-radio-group v-model="form.output_format">
                <el-radio label="json">JSON</el-radio>
                <el-radio label="html">HTML (可视化)</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="generateReport" :loading="generating">
                <el-icon><DocumentChecked /></el-icon>
                生成校验报告
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-if="report" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>报告结果: {{ report.report_name }}</span>
              <el-button type="primary" link @click="downloadReportFile">
                <el-icon><Download /></el-icon> 下载报告
              </el-button>
            </div>
          </template>

          <el-row :gutter="16">
            <el-col :span="6">
              <div class="metric-card accuracy">
                <div class="metric-value">{{ report.summary.overall_accuracy_rate }}%</div>
                <div class="metric-label">脱敏准确率</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card coverage">
                <div class="metric-value">{{ report.summary.overall_coverage_rate }}%</div>
                <div class="metric-label">规则覆盖率</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card speed">
                <div class="metric-value">{{ report.performance.rows_per_second }}</div>
                <div class="metric-label">处理速度 (行/秒)</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card time">
                <div class="metric-value">{{ report.performance.total_time_ms }}ms</div>
                <div class="metric-label">总耗时</div>
              </div>
            </el-col>
          </el-row>

          <el-divider />

          <h4>性能指标</h4>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="总数据行">{{ report.performance.total_rows }} 行</el-descriptions-item>
            <el-descriptions-item label="总字段数">{{ report.performance.total_columns }} 个</el-descriptions-item>
            <el-descriptions-item label="识别耗时">{{ report.performance.detection_time_ms }} ms</el-descriptions-item>
            <el-descriptions-item label="脱敏耗时">{{ report.performance.desensitization_time_ms }} ms</el-descriptions-item>
            <el-descriptions-item label="总耗时">{{ report.performance.total_time_ms }} ms</el-descriptions-item>
            <el-descriptions-item label="峰值内存">{{ report.performance.memory_peak_mb }} MB</el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <h4>规则覆盖率详情</h4>
          <el-table :data="report.rule_coverage" border size="small">
            <el-table-column prop="rule_name" label="规则名称" min-width="180" />
            <el-table-column prop="rule_type" label="类型" width="100" />
            <el-table-column prop="matched_count" label="匹配次数" width="100" />
            <el-table-column prop="matched_rows" label="涉及行数" width="100" />
            <el-table-column label="覆盖率" width="120">
              <template #default="scope">
                <el-progress :percentage="scope.row.coverage_rate" :color="coverageColor" />
              </template>
            </el-table-column>
          </el-table>

          <el-divider />

          <h4>脱敏准确率详情</h4>
          <el-table :data="report.accuracy_details" border size="small">
            <el-table-column prop="column_name" label="字段" width="120" />
            <el-table-column prop="rule_name" label="应用规则" width="150" />
            <el-table-column prop="total_values" label="总数据" width="90" />
            <el-table-column prop="desensitized_count" label="已脱敏" width="90" />
            <el-table-column label="准确率" width="150">
              <template #default="scope">
                <el-progress :percentage="scope.row.accuracy_rate" :color="accuracyColor" />
              </template>
            </el-table-column>
            <el-table-column label="示例" min-width="250">
              <template #default="scope">
                <el-tag size="small" type="info">{{ scope.row.sample_original }}</el-tag>
                <el-icon><ArrowRight /></el-icon>
                <el-tag size="small" type="success">{{ scope.row.sample_desensitized }}</el-tag>
              </template>
            </el-table-column>
          </el-table>

          <el-divider />

          <h4>优化建议</h4>
          <el-alert
            v-for="(rec, idx) in report.recommendations"
            :key="idx"
            :title="rec"
            type="info"
            :closable="false"
            style="margin-bottom: 8px;"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentChecked, Download, Delete, Plus, ArrowRight } from '@element-plus/icons-vue'
import { generateReport as generateReportApi } from '@/api/report'
import { getDatasetList } from '@/api/dataset'
import { getDesensitizationRules } from '@/api/desensitization'

const datasets = ref([])
const allRules = ref([])
const generating = ref(false)
const report = ref(null)

const form = ref({
  dataset_id: null,
  output_format: 'json',
  report_name: '脱敏规则校验报告'
})

const ruleMappings = ref([
  { column: '姓名', rule_id: 3 },
  { column: '手机号', rule_id: 1 },
  { column: '身份证号', rule_id: 2 },
  { column: '银行卡号', rule_id: 4 },
  { column: '地址', rule_id: 5 },
  { column: '邮箱', rule_id: 8 }
])

const coverageColor = (percentage) => {
  if (percentage < 50) return '#f56c6c'
  if (percentage < 80) return '#e6a23c'
  return '#67c23a'
}

const accuracyColor = (percentage) => {
  if (percentage < 50) return '#f56c6c'
  if (percentage < 90) return '#e6a23c'
  return '#67c23a'
}

const addMapping = () => {
  ruleMappings.value.push({ column: '', rule_id: null })
}

const removeMapping = (index) => {
  ruleMappings.value.splice(index, 1)
}

const generateReport = async () => {
  if (!form.value.dataset_id) {
    ElMessage.warning('请选择数据集')
    return
  }

  const fieldRules = {}
  for (const m of ruleMappings.value) {
    if (m.column && m.rule_id) {
      fieldRules[m.column] = m.rule_id
    }
  }

  if (Object.keys(fieldRules).length === 0) {
    ElMessage.warning('请配置至少一个字段规则映射')
    return
  }

  generating.value = true
  try {
    const res = await generateReportApi({
      dataset_id: form.value.dataset_id,
      field_rules: fieldRules,
      report_name: form.value.report_name,
      output_format: form.value.output_format
    })
    report.value = res.data
    ElMessage.success('报告生成成功')
  } catch (e) {
    ElMessage.error('报告生成失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    generating.value = false
  }
}

const downloadReportFile = () => {
  if (report.value?.download_url) {
    window.open(report.value.download_url, '_blank')
  }
}

onMounted(async () => {
  try {
    const dsRes = await getDatasetList({ page: 1, page_size: 100 })
    datasets.value = dsRes.data?.items || []

    const ruleRes = await getDesensitizationRules()
    allRules.value = ruleRes.data || []
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped lang="scss">
.report-dashboard {
  padding: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-card {
  text-align: center;
  padding: 20px;
  border-radius: 16px;
  color: white;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
}

.metric-card.accuracy {
  background: linear-gradient(135deg, rgba(17, 153, 142, 0.9) 0%, rgba(56, 239, 125, 0.9) 100%);
}

.metric-card.coverage {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
}

.metric-card.speed {
  background: linear-gradient(135deg, rgba(252, 74, 26, 0.9) 0%, rgba(247, 183, 51, 0.9) 100%);
}

.metric-card.time {
  background: linear-gradient(135deg, rgba(33, 147, 176, 0.9) 0%, rgba(109, 213, 237, 0.9) 100%);
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
}

.metric-label {
  font-size: 13px;
  margin-top: 4px;
  opacity: 0.9;
}

h4 {
  margin: 16px 0 12px;
  color: #1F2937;
  font-weight: 600;
}

/* 表格行悬浮效果 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(184, 212, 227, 0.12) !important;
  }
}

/* 进度条玻璃效果 */
:deep(.el-progress-bar__outer) {
  background: rgba(0, 0, 0, 0.05) !important;
}

/* 标签玻璃效果 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}
</style>
