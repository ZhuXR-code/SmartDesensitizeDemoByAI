<template>
  <div class="rule-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>脱敏规则管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon> 新建规则
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="语言">
          <el-select v-model="filterForm.language" placeholder="全部" clearable style="width: 140px;">
            <el-option label="中文" value="zh" />
            <el-option label="英语" value="en" />
            <el-option label="日语" value="ja" />
            <el-option label="韩语" value="ko" />
            <el-option label="法语" value="fr" />
            <el-option label="德语" value="de" />
            <el-option label="通用" value="all" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="全部" clearable style="width: 140px;">
            <el-option label="遮盖模式" value="mask" />
            <el-option label="仿真替换" value="simulation" />
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
        <el-table-column prop="desensitization_method" label="脱敏方式">
          <template #default="{ row }">
            <el-tag :type="getMethodType(row.desensitization_method)">
              {{ getMethodName(row.desensitization_method) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="info" effect="plain">
              {{ row.usage_count || 0 }} 次
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_builtin" label="来源">
          <template #default="{ row }">
            <el-tag :type="row.is_builtin ? 'info' : 'warning'">
              {{ row.is_builtin ? '内置' : '自定义' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button link type="primary" class="glass-btn-solid" @click="showRuleDetail(row)" title="查看详情">
              <el-icon><View /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="showCreateDialog" title="新建脱敏规则" width="600px">
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
            <el-option label="通用" value="all" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" required>
          <el-radio-group v-model="createForm.category">
            <el-radio label="mask">遮盖模式</el-radio>
            <el-radio label="simulation">仿真替换</el-radio>
            <el-radio label="deterministic">关联造数</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="方法" required>
          <el-input v-model="createForm.method" placeholder="如: partial_mask, random_chinese_name" />
        </el-form-item>
        <el-form-item label="配置">
          <el-input v-model="createForm.config" type="textarea" placeholder="JSON格式配置" />
        </el-form-item>
        <el-form-item label="脱敏示例">
          <el-input v-model="createForm.example" type="textarea" placeholder='JSON格式，如: {"before": "张三", "after": "李四"}' :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 规则详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="脱敏规则详情" width="800px">
      <div v-if="currentRule">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="规则名称">{{ currentRule.name }}</el-descriptions-item>
          <el-descriptions-item label="脱敏方式">
            <el-tag :type="getMethodType(currentRule.desensitization_method)">
              {{ getMethodName(currentRule.desensitization_method) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="适用语言">{{ languageMap[currentRule.language] || currentRule.language }}</el-descriptions-item>
          <el-descriptions-item label="规则说明">
            {{ currentRule.description || '暂无说明' }}
          </el-descriptions-item>
          <el-descriptions-item label="配置信息">
            <div style="background: #f5f7fa; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 12px;">
              <div><strong>方法名：</strong>{{ currentRule.method }}</div>
              <div style="margin-top: 8px;"><strong>配置参数：</strong></div>
              <pre style="margin: 4px 0 0 0;">{{ JSON.stringify(currentRule.config, null, 2) }}</pre>
              <div style="margin-top: 8px; color: #909399; font-size: 11px;">
                💡 该规则使用 <code>{{ currentRule.method }}</code> 方法进行数据脱敏处理
              </div>
            </div>
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <h4>脱敏效果示例</h4>
        <el-table :data="[currentRule.example || {}]" size="small" border>
          <el-table-column label="脱敏前" prop="before">
            <template #default="{ row }">
              <span style="color: #f56c6c; font-weight: bold;">{{ row.before || '暂无示例' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="脱敏后" prop="after">
            <template #default="{ row }">
              <span style="color: #668F80; font-weight: bold;">{{ row.after || '暂无示例' }}</span>
            </template>
          </el-table-column>
        </el-table>
        
        <el-alert type="info" :closable="false" style="margin-top: 12px;">
          <template #title>
            <div style="font-size: 13px;">
              💡 <strong>使用说明：</strong>{{ getUsageTip(currentRule) }}
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
import { View } from '@element-plus/icons-vue'
import { getDesensitizationRules, createDesensitizationRule } from '@/api/desensitization'

const loading = ref(false)
const rules = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const currentRule = ref(null)

const filterForm = ref({
  language: '',
  category: ''
})

const createForm = ref({
  name: '',
  language: 'zh',
  category: 'mask',
  method: '',
  config: '{}',
  example: '{"before": "", "after": ""}'
})

const languageMap = {
  zh: '中文',
  en: '英语',
  ja: '日语',
  ko: '韩语',
  fr: '法语',
  de: '德语',
  all: '通用'
}

const getMethodName = (method) => {
  const map = {
    'full_mask': '完全遮盖',
    'partial_mask': '部分遮盖',
    'simulation': '仿真造数',
    'deterministic_simulation': '关联造数'
  }
  return map[method] || method
}

const getMethodType = (method) => {
  const map = {
    'full_mask': 'danger',
    'partial_mask': 'warning',
    'simulation': 'success',
    'deterministic_simulation': 'primary'
  }
  return map[method] || 'info'
}

const showRuleDetail = (rule) => {
  currentRule.value = rule
  showDetailDialog.value = true
}

const getUsageTip = (rule) => {
  const tips = {
    'full_mask': '适用于需要完全隐藏原始数据的场景，如密码、密钥等高度敏感信息',
    'partial_mask': '适用于需要保留部分信息以便识别的场景，如显示手机号后4位便于用户确认',
    'simulation': '适用于需要保持数据格式和真实感的场景，如测试数据生成、数据分析等'
  }
  
  const baseTip = tips[rule.desensitization_method] || '根据实际需求选择合适的脱敏规则'
  
  // 根据语言添加额外提示
  if (rule.language !== 'all' && rule.language) {
    return `${baseTip}。该规则专门针对${languageMap[rule.language]}数据优化。`
  }
  
  return baseTip
}

const loadRules = async () => {
  loading.value = true
  try {
    const res = await getDesensitizationRules(filterForm.value)
    rules.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const submitCreate = async () => {
  try {
    const data = { ...createForm.value }
    if (data.config) {
      data.config = JSON.parse(data.config)
    }
    if (data.example) {
      data.example = JSON.parse(data.example)
    }
    await createDesensitizationRule(data)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    loadRules()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped lang="scss">
.rule-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 玻璃质感表格行悬浮效果 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(184, 212, 227, 0.12) !important;
  }
}

/* 标签玻璃效果 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

/* 筛选表单玻璃效果 */
:deep(.el-form--inline) {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.6);
}
</style>
