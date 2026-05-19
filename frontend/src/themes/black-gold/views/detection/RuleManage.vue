<template>
  <div class="rule-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>识别规则管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon> 新建规则
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="filterForm">
        <el-form-item label="语言">
          <el-select v-model="filterForm.language" placeholder="全部" clearable>
            <el-option label="中文" value="zh" />
            <el-option label="英语" value="en" />
            <el-option label="日语" value="ja" />
            <el-option label="韩语" value="ko" />
            <el-option label="法语" value="fr" />
            <el-option label="德语" value="de" />
          </el-select>
        </el-form-item>
        <el-form-item label="规则类型">
          <el-select v-model="filterForm.rule_type" placeholder="全部" clearable>
            <el-option label="正则表达式" value="regex" />
            <el-option label="关键词" value="keyword" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadRules">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="rules" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则名称" />
        <el-table-column prop="language" label="语言">
          <template #default="{ row }">
            <el-tag>{{ languageMap[row.language] || row.language }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rule_type" label="类型">
          <template #default="{ row }">
            <el-tag :type="row.rule_type === 'regex' ? 'primary' : 'success'">
              {{ row.rule_type === 'regex' ? '正则' : '关键词' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="example" label="示例" show-overflow-tooltip />
        <el-table-column prop="is_builtin" label="来源">
          <template #default="{ row }">
            <el-tag :type="row.is_builtin ? 'info' : 'warning'">
              {{ row.is_builtin ? '内置' : '自定义' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button link type="primary" @click="showRuleDetail(row)">
              查看详情
            </el-button>
            <el-button
              v-if="!row.is_builtin"
              link
              type="warning"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-popconfirm
              v-if="!row.is_builtin"
              title="确定删除此规则？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreateDialog" :title="isEditMode ? '编辑识别规则' : '新建识别规则'" width="600px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="规则名称" required>
          <el-input v-model="createForm.name" />
        </el-form-item>
        <el-form-item label="语言" required>
          <el-select v-model="createForm.language">
            <el-option label="中文" value="zh" />
            <el-option label="英语" value="en" />
            <el-option label="日语" value="ja" />
            <el-option label="韩语" value="ko" />
            <el-option label="法语" value="fr" />
            <el-option label="德语" value="de" />
          </el-select>
        </el-form-item>
        <el-form-item label="规则类型" required>
          <el-radio-group v-model="createForm.rule_type">
            <el-radio label="regex">正则表达式</el-radio>
            <el-radio label="keyword">关键词</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="匹配模式" v-if="createForm.rule_type === 'regex'">
          <el-input v-model="createForm.pattern" placeholder="输入正则表达式" />
        </el-form-item>
        <el-form-item label="关键词" v-if="createForm.rule_type === 'keyword'">
          <el-select
            v-model="createForm.keywords"
            multiple
            filterable
            allow-create
            placeholder="输入关键词"
          />
        </el-form-item>
        <el-form-item label="示例">
          <el-input v-model="createForm.example" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="submitCreate">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="识别规则详情" width="700px">
      <div v-if="currentRule">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="规则名称">{{ currentRule.name }}</el-descriptions-item>
          <el-descriptions-item label="适用语言">{{ languageMap[currentRule.language] || currentRule.language }}</el-descriptions-item>
          <el-descriptions-item label="规则类型">
            <el-tag :type="currentRule.rule_type === 'regex' ? 'primary' : 'success'">
              {{ currentRule.rule_type === 'regex' ? '正则表达式' : '关键词匹配' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="规则说明">
            {{ getRuleDescription(currentRule) }}
          </el-descriptions-item>
          <el-descriptions-item label="匹配模式" v-if="currentRule.pattern">
            <code style="background: #f5f7fa; padding: 4px 8px; border-radius: 4px;">{{ currentRule.pattern }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="关键词列表" v-if="currentRule.keywords && currentRule.keywords.length > 0">
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
              <el-tag
                v-for="(kw, index) in currentRule.keywords"
                :key="index"
                size="default"
                type="success"
                effect="plain"
              >
                {{ kw }}
              </el-tag>
            </div>
            <div style="margin-top: 8px; color: #909399; font-size: 12px;">
              共 {{ currentRule.keywords.length }} 个关键词
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h4>识别示例</h4>
        <el-alert type="info" :closable="false">
          <template #title>
            <div>
              <strong>示例数据：</strong>{{ currentRule.example || '暂无示例' }}
            </div>
            <div style="margin-top: 8px; color: #67c23a;">
              <strong>该规则可以识别上述类型的敏感信息</strong>
            </div>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getDetectionRules, createDetectionRule, deleteDetectionRule, updateDetectionRule } from '@/api/detection'

const loading = ref(false)
const rules = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const currentRule = ref(null)
const isEditMode = ref(false)
const editingRuleId = ref(null)

const filterForm = ref({
  language: '',
  rule_type: ''
})

const createForm = ref({
  name: '',
  language: 'zh',
  rule_type: 'regex',
  pattern: '',
  keywords: [],
  example: ''
})

const languageMap = {
  zh: '中文',
  en: '英语',
  ja: '日语',
  ko: '韩语',
  fr: '法语',
  de: '德语'
}

const getRuleDescription = (rule) => {
  const descriptions = {
    '手机号': '识别中国手机号码，通常为11位数字，以13、15、18等开头',
    '身份证': '识别中国居民身份证号码，18位字符，包含地区码、出生日期和校验码',
    '邮箱': '识别电子邮件地址，格式为用户名@域名',
    '银行卡': '识别银行卡号，通常为16-19位数字',
    '姓名': '识别中文姓名，通常为2-4个汉字',
    '地址': '识别中国地址信息，包含省市区和详细地址',
    '车牌号': '识别中国机动车号牌，如京A12345',
    '护照号': '识别护照号码，通常为G/E开头加8位数字'
  }
  for (const [key, desc] of Object.entries(descriptions)) {
    if (rule.name.includes(key)) {
      return desc
    }
  }
  return rule.description || `${rule.rule_type === 'regex' ? '正则表达式' : '关键词'}匹配规则，用于识别${rule.language === 'zh' ? '中文' : rule.language}环境下的敏感信息`
}

const showRuleDetail = (rule) => {
  currentRule.value = rule
  showDetailDialog.value = true
}

const loadRules = async () => {
  loading.value = true
  try {
    const res = await getDetectionRules(filterForm.value)
    rules.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const submitCreate = async () => {
  try {
    if (isEditMode.value) {
      await updateDetectionRule(editingRuleId.value, createForm.value)
      ElMessage.success('更新成功')
    } else {
      await createDetectionRule(createForm.value)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    resetForm()
    loadRules()
  } catch (e) {
    console.error(e)
    ElMessage.error(isEditMode.value ? '更新失败' : '创建失败')
  }
}

const handleEdit = (row) => {
  isEditMode.value = true
  editingRuleId.value = row.id
  createForm.value = {
    name: row.name,
    language: row.language,
    rule_type: row.rule_type,
    pattern: row.pattern || '',
    keywords: row.keywords || [],
    example: row.example || ''
  }
  showCreateDialog.value = true
}

const resetForm = () => {
  isEditMode.value = false
  editingRuleId.value = null
  createForm.value = {
    name: '',
    language: 'zh',
    rule_type: 'regex',
    pattern: '',
    keywords: [],
    example: ''
  }
}

const handleCancel = () => {
  showCreateDialog.value = false
  resetForm()
}

const handleDelete = async (row) => {
  try {
    await deleteDetectionRule(row.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch (e) {
    console.error(e)
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
