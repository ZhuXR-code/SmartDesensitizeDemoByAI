<template>
  <div class="rule-set-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>规则集管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon> 新建规则集
          </el-button>
        </div>
      </template>
      
      <el-table :data="ruleSets" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则集名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="rule_count" label="包含规则数" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.rule_count }} 个规则</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-space>
              <el-tooltip content="查看规则集详情" placement="top">
                <el-button link type="primary" size="small" class="glass-btn-solid" @click="viewRuleSet(row)">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑规则集" placement="top">
                <el-button link type="warning" size="small" class="glass-btn-solid" @click="editRuleSet(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-popconfirm
                title="确定删除此规则集？"
                @confirm="deleteRuleSet(row)"
              >
                <template #reference>
                  <el-tooltip content="删除规则集" placement="top">
                    <el-button link type="danger" size="small" class="glass-btn-solid">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </template>
              </el-popconfirm>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!loading && ruleSets.length === 0" class="empty-state">
        <el-empty description="暂无规则集，请点击右上角新建">
          <el-button type="primary" @click="showCreateDialog = true">
            立即创建第一个规则集
          </el-button>
        </el-empty>
      </div>
    </el-card>
    
    <!-- 创建/编辑规则集对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingId ? '编辑规则集' : '新建规则集'" 
      width="900px"
    >
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="规则集名称" required>
          <el-input v-model="createForm.name" placeholder="例如：个人隐私保护规则集" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="2"
            placeholder="描述该规则集的用途" 
          />
        </el-form-item>
        
        <el-divider>选择规则</el-divider>
        
        <el-form-item label="语言筛选">
          <el-select v-model="filterLanguage" placeholder="全部语言" clearable style="width: 200px">
            <el-option label="中文" value="zh" />
            <el-option label="英语" value="en" />
            <el-option label="日语" value="ja" />
            <el-option label="韩语" value="ko" />
            <el-option label="法语" value="fr" />
            <el-option label="德语" value="de" />
          </el-select>
          <el-tag type="info" style="margin-left: 10px">
            已选择 {{ selectedRules.length }} 个规则
          </el-tag>
        </el-form-item>
        
        <el-table 
          :data="filteredRules" 
          height="400"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="name" label="规则名称" min-width="150" />
          <el-table-column prop="language" label="语言" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ languageMap[row.language] || row.language }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="rule_type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="row.rule_type === 'regex' ? 'primary' : 'success'">
                {{ row.rule_type === 'regex' ? '正则' : '关键词' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="example" label="示例" min-width="200" show-overflow-tooltip />
          <el-table-column prop="is_builtin" label="来源" width="80">
            <template #default="{ row }">
              <el-tag size="small" :type="row.is_builtin ? 'info' : 'warning'">
                {{ row.is_builtin ? '内置' : '自定义' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitting">
          {{ editingId ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 查看规则集详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="规则集详情" width="800px">
      <div v-if="currentRuleSet">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="规则集名称">{{ currentRuleSet.name }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ currentRuleSet.description || '无' }}</el-descriptions-item>
          <el-descriptions-item label="包含规则数">
            <el-tag type="info">{{ currentRuleSet.rules?.length || 0 }} 个规则</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentRuleSet.created_at }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <h4>规则列表</h4>
        <el-table :data="currentRuleSet.rules || []" max-height="400">
          <el-table-column prop="name" label="规则名称" min-width="150" />
          <el-table-column prop="language" label="语言" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ languageMap[row.language] || row.language }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="rule_type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="row.rule_type === 'regex' ? 'primary' : 'success'">
                {{ row.rule_type === 'regex' ? '正则' : '关键词' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="example" label="示例" min-width="200" show-overflow-tooltip />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, View, Edit, Delete } from '@element-plus/icons-vue'
import { 
  getDetectionRules,
  getRuleSets,
  createRuleSet,
  updateRuleSet,
  deleteRuleSet as deleteRuleSetApi,
  getRuleSetDetail
} from '@/api/detection'

const loading = ref(false)
const submitting = ref(false)
const ruleSets = ref([])
const allRules = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const currentRuleSet = ref(null)
const editingId = ref(null)
const filterLanguage = ref('')
const selectedRules = ref([])

const createForm = ref({
  name: '',
  description: '',
  rule_ids: []
})

const languageMap = {
  zh: '中文',
  en: '英语',
  ja: '日语',
  ko: '韩语',
  fr: '法语',
  de: '德语'
}

// 根据语言筛选规则
const filteredRules = computed(() => {
  if (!filterLanguage.value) return allRules.value
  return allRules.value.filter(r => r.language === filterLanguage.value)
})

// 加载所有规则
const loadAllRules = async () => {
  try {
    const res = await getDetectionRules({})
    allRules.value = res.data || []
  } catch (error) {
    console.error('加载规则失败:', error)
  }
}

// 加载规则集列表
const loadRuleSets = async () => {
  loading.value = true
  try {
    const res = await getRuleSets({})
    ruleSets.value = res.data || []
  } catch (error) {
    ElMessage.error('加载规则集失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 处理规则选择
const handleSelectionChange = (selection) => {
  selectedRules.value = selection.map(r => r.id)
}

// 提交创建/编辑
const submitCreate = async () => {
  if (!createForm.value.name) {
    ElMessage.warning('请输入规则集名称')
    return
  }
  
  if (selectedRules.value.length === 0) {
    ElMessage.warning('请至少选择一个规则')
    return
  }
  
  submitting.value = true
  try {
    const data = {
      name: createForm.value.name,
      description: createForm.value.description,
      rules: selectedRules.value  // 修改：使用 rules 而不是 rule_ids
    }
    
    if (editingId.value) {
      await updateRuleSet(editingId.value, data)
      ElMessage.success('规则集更新成功')
    } else {
      await createRuleSet(data)
      ElMessage.success('规则集创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    loadRuleSets()
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

// 查看规则集详情
const viewRuleSet = async (row) => {
  try {
    const res = await getRuleSetDetail(row.id)
    currentRuleSet.value = res.data
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('加载规则集详情失败')
  }
}

// 编辑规则集
const editRuleSet = async (row) => {
  try {
    const res = await getRuleSetDetail(row.id)
    const ruleSet = res.data
    
    editingId.value = row.id
    createForm.value.name = ruleSet.name
    createForm.value.description = ruleSet.description || ''
    selectedRules.value = ruleSet.rules?.map(r => r.id) || []
    
    showCreateDialog.value = true
  } catch (error) {
    ElMessage.error('加载规则集失败')
  }
}

// 删除规则集
const deleteRuleSet = async (row) => {
  try {
    await deleteRuleSetApi(row.id)
    ElMessage.success('规则集已删除')
    loadRuleSets()
  } catch (error) {
    ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 重置表单
const resetForm = () => {
  editingId.value = null
  createForm.value = {
    name: '',
    description: '',
    rule_ids: []
  }
  selectedRules.value = []
  filterLanguage.value = ''
}

onMounted(() => {
  loadRuleSets()
  loadAllRules()
})
</script>

<style scoped lang="scss">
.rule-set-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 玻璃质感表格行悬浮效果 - design02 色系 */
:deep(.el-table__row) {
  transition: all 0.2s ease;

  &:hover {
    background: rgba(244, 253, 175, 0.08) !important;
  }
}

/* 标签玻璃效果 - design02 色系 */
:deep(.el-tag) {
  backdrop-filter: blur(4px);
  border: 1px solid rgba(244, 253, 175, 0.2) !important;
}

/* 玻璃按钮效果 - design02 色系 */
.glass-btn-solid {
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.2);
  transition: all 0.2s ease;

  &:hover {
    background: rgba(244, 253, 175, 0.15);
    border-color: rgba(244, 253, 175, 0.4);
  }
}

/* 空状态 */
.empty-state {
  padding: 40px 0;
}
</style>
