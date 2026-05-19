<template>
  <div class="ai-config-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon size="18" style="vertical-align: middle; margin-right: 6px;"><Setting /></el-icon>
            AI 模型配置
          </span>
          <el-button type="primary" @click="openDialog(null)">
            <el-icon><Plus /></el-icon> 新增配置
          </el-button>
        </div>
      </template>

      <el-table :data="configs" stripe v-loading="loading" empty-text="暂无配置，请点击「新增配置」添加">
        <el-table-column label="配置名称" min-width="140">
          <template #default="{ row }">
            <span>{{ row.alias || '未命名' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="provider" label="提供商" width="110" />
        <el-table-column prop="model_name" label="模型名称" width="170" />
        <el-table-column label="温度" width="70" align="center">
          <template #default="{ row }">{{ row.temperature }}</template>
        </el-table-column>
        <el-table-column label="Token" width="100" align="center">
          <template #default="{ row }">{{ row.max_tokens }}</template>
        </el-table-column>
        <el-table-column label="默认" width="60" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" type="success" size="small" effect="dark">默认</el-tag>
            <span v-else style="color: #c0c4cc;">—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button v-if="!row.is_active" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑AI配置' : '新增AI配置'" width="680px" top="5vh">
      <el-form :model="form" label-width="110px" label-position="left">
        <el-form-item label="配置名称">
          <el-input v-model="form.alias" placeholder="例如：我的DeepSeek配置" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="AI提供商" required>
              <el-select v-model="form.provider" @change="onProviderChange" style="width: 100%">
                <el-option v-for="p in providers" :key="p.provider" :label="p.label" :value="p.provider" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="模型名称" required>
              <el-select v-model="form.model_name" style="width: 100%">
                <el-option v-for="m in currentModels" :key="m.name" :label="m.label" :value="m.name" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="API 密钥" required>
          <div style="display: flex; gap: 8px; width: 100%;">
            <el-input 
              v-model="form.api_key" 
              type="password" 
              show-password
              :placeholder="isEdit && configId ? '请输入 API Key' : '请输入 API Key'" 
              style="flex: 1;"
            />
          </div>
          <div v-if="isEdit && configId" style="margin-top: 4px; font-size: 12px; color: #909399;">
            当前已配置密钥，点击眼睛图标可查看，修改后将覆盖原有密钥
          </div>
        </el-form-item>
        <el-form-item label="API 地址" required>
          <el-input v-model="form.api_base_url" placeholder="请输入 API 地址" />
        </el-form-item>
        <el-divider />
        <el-form-item label="联网搜索">
          <el-switch v-model="form.enable_web_search" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="温度">
              <el-slider v-model="form.temperature" :min="0" :max="1" :step="0.1" show-input style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Max Tokens">
              <el-input-number v-model="form.max_tokens" :min="1024" :max="32768" :step="1024" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-button type="warning" @click="handleTest" :loading="testing" plain>测试连接</el-button>
          <div style="display: flex; gap: 8px;">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAiConfigs, getAiConfigDetail, saveAiConfig, updateConfig, deleteConfig, activateConfig, testAiConnection } from '@/api/ai'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Plus } from '@element-plus/icons-vue'

const configs = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const configId = ref(null)
const saving = ref(false)
const testing = ref(false)

const form = ref({
  alias: '', provider: 'openai', model_name: 'gpt-4o-mini',
  api_key: '', api_base_url: '', enable_web_search: false,
  temperature: 0.3, max_tokens: 4096
})

// 保存原始密钥用于还原
const originalApiKey = ref('')

const providers = [
  { provider: 'openai', label: 'OpenAI', base_url: 'https://api.openai.com' },
  { provider: 'deepseek', label: 'DeepSeek', base_url: 'https://api.deepseek.com' },
  { provider: 'qwen', label: '阿里千问', base_url: 'https://dashscope.aliyuncs.com/compatible-mode' },
  { provider: 'kimi', label: '月之暗面 Kimi', base_url: 'https://api.moonshot.cn' },
  { provider: 'zhipu', label: '智谱 GLM', base_url: 'https://open.bigmodel.cn/api/paas/v4' },
  { provider: 'baidu', label: '百度文心', base_url: 'https://aip.baidubce.com' },
  { provider: 'azure', label: 'Azure OpenAI', base_url: '' },
  { provider: 'custom', label: '自定义（兼容OpenAI协议）', base_url: '' }
]

const modelMap = {
  openai: [
    { name: 'gpt-4o', label: 'GPT-4o' }, { name: 'gpt-4o-mini', label: 'GPT-4o Mini（推荐）' },
    { name: 'gpt-4-turbo', label: 'GPT-4 Turbo' }, { name: 'o1-mini', label: 'O1 Mini' }, { name: 'o1-preview', label: 'O1 Preview' }
  ],
  deepseek: [
    { name: 'deepseek-chat', label: 'DeepSeek V3（通用对话）' }, { name: 'deepseek-reasoner', label: 'DeepSeek R1（深度推理）' },
    { name: 'deepseek-v4-pro', label: 'DeepSeek V4 Pro（最新旗舰）' }, { name: 'deepseek-v4-flash', label: 'DeepSeek V4 Flash（快速版）' }
  ],
  qwen: [
    { name: 'qwen-plus', label: 'Qwen-Plus（推荐）' }, { name: 'qwen-max', label: 'Qwen-Max（最强）' }, { name: 'qwen-turbo', label: 'Qwen-Turbo（快速经济）' }
  ],
  kimi: [
    { name: 'moonshot-v1-8k', label: 'Kimi v1-8K' }, { name: 'moonshot-v1-32k', label: 'Kimi v1-32K' }, { name: 'moonshot-v1-128k', label: 'Kimi v1-128K（超长上下文）' }
  ],
  zhipu: [
    { name: 'glm-4-plus', label: 'GLM-4-Plus（推荐）' }, { name: 'glm-4-air', label: 'GLM-4-Air（快速）' }, { name: 'glm-4-flash', label: 'GLM-4-Flash（免费）' }
  ],
  baidu: [
    { name: 'ernie-4.0-8k', label: 'ERNIE 4.0（最强）' }, { name: 'ernie-3.5-8k', label: 'ERNIE 3.5' }, { name: 'ernie-speed-128k', label: 'ERNIE Speed（快速128K）' }
  ],
  azure: [
    { name: 'gpt-4o', label: 'GPT-4o' }, { name: 'gpt-4o-mini', label: 'GPT-4o Mini' }, { name: 'gpt-4', label: 'GPT-4' }
  ],
  custom: [{ name: 'custom', label: '自定义模型' }]
}

const currentModels = computed(() => modelMap[form.value.provider] || modelMap.openai)

const loadConfigs = async () => {
  loading.value = true
  try { const res = await getAiConfigs(); configs.value = res.data || []
  } catch { configs.value = [] } finally { loading.value = false }
}

const openDialog = async (row) => {
  if (row) {
    isEdit.value = true; configId.value = row.id
    // 获取完整配置信息以显示真实密钥
    try {
      const res = await getAiConfigDetail(row.id)
      const config = res.data
      originalApiKey.value = config.api_key || '' // 保存原始密钥
      form.value = {
        alias: config.alias || '', provider: config.provider || 'openai', model_name: config.model_name || 'gpt-4o-mini',
        api_key: config.api_key || '', // 填充真实密钥
        api_base_url: config.api_base_url || '',
        enable_web_search: config.enable_web_search || false, temperature: config.temperature ?? 0.3, max_tokens: config.max_tokens || 4096
      }
    } catch (e) {
      ElMessage.error('获取配置详情失败: ' + (e.message || ''))
      return
    }
  } else {
    isEdit.value = false; configId.value = null
    originalApiKey.value = ''
    form.value = { alias: '', provider: 'openai', model_name: 'gpt-4o-mini', api_key: '', api_base_url: '', enable_web_search: false, temperature: 0.3, max_tokens: 4096 }
  }
  dialogVisible.value = true
}

const onProviderChange = (val) => {
  const p = providers.find(x => x.provider === val)
  const models = modelMap[val] || modelMap.openai
  form.value.model_name = models[0]?.name || 'custom'
  if (p?.base_url && !form.value.api_base_url && !isEdit.value) {
    form.value.api_base_url = p.base_url
  }
}

const handleSave = async () => {
  if (!form.value.api_key && !configId.value) { ElMessage.warning('请输入 API 密钥'); return }
  if (!form.value.api_base_url) { ElMessage.warning('请输入 API 地址'); return }
  saving.value = true
  try {
    if (isEdit.value && configId.value) {
      const payload = { ...form.value }; if (!payload.api_key) delete payload.api_key
      await updateConfig(configId.value, payload)
    } else {
      await saveAiConfig(form.value)
    }
    ElMessage.success(isEdit.value ? '配置已更新' : '配置已创建')
    dialogVisible.value = false
    await loadConfigs()
  } catch (e) { ElMessage.error('操作失败: ' + (e.message || ''))
  } finally { saving.value = false }
}

const handleTest = async () => {
  if (!form.value.api_key) { ElMessage.warning('请先输入 API 密钥'); return }
  testing.value = true
  try {
    const res = await testAiConnection({ provider: form.value.provider, model_name: form.value.model_name, api_key: form.value.api_key, api_base_url: form.value.api_base_url })
    if (res.data?.success) { ElMessage.success(res.data.message) }
    else { ElMessage.error(res.data?.message || '连接失败') }
  } catch (e) { ElMessage.error('测试异常: ' + (e.message || ''))
  } finally { testing.value = false }
}

const handleDelete = async (row) => {
  if (row.is_active) {
    ElMessage.warning('当前配置为默认配置，请先设置其他配置为默认后再删除')
    return
  }
  try {
    await ElMessageBox.confirm('确定删除此配置？删除后不可恢复。', '删除确认', { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' })
    await deleteConfig(row.id)
    ElMessage.success('配置已删除')
    await loadConfigs()
  } catch { /* cancelled */ }
}

onMounted(loadConfigs)
</script>

<style scoped>
.ai-config-page { max-width: 1200px; margin: 0 auto; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
</style>
