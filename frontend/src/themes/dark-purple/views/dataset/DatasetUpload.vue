<template>
  <div class="dataset-upload">
    <el-card>
      <template #header>
        <span>导入数据</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="文件上传" name="file">
          <el-upload
            class="upload-area"
            drag
            action=""
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".csv,.xlsx,.xls,.txt,.md,.log,.json"
          >
            <el-icon class="el-icon--upload" size="50"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 Excel、CSV、TXT、JSON、Markdown、Log 等格式
              </div>
            </template>
          </el-upload>

          <el-form v-if="selectedFile" :model="form" label-width="100px" style="margin-top: 20px;">
            <el-form-item label="数据集名称">
              <el-input v-model="form.name" placeholder="请输入数据集名称" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="form.description" type="textarea" placeholder="可选" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitUpload" :loading="uploading">确认上传</el-button>
              <el-button @click="$router.back()">取消</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="从数据库导入" name="database">
          <div style="text-align: center; padding: 60px 20px;">
            <el-icon size="80" color="#409EFF"><DataLine /></el-icon>
            <h3 style="margin: 20px 0 10px; color: #303133;">从数据库导入数据</h3>
            <p style="color: #606266; margin-bottom: 30px; line-height: 1.6;">
              请先在“数据源配置”页面配置数据库连接信息<br/>
              配置完成后，即可从数据库中选择表导入为数据集
            </p>
            <el-button type="primary" size="large" @click="goToDataSource">
              <el-icon><Link /></el-icon>
              前往数据源配置
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="剪贴板粘贴" name="clipboard">
          <el-form :model="clipboardForm" label-width="100px">
            <el-form-item label="数据集名称">
              <el-input v-model="clipboardForm.name" placeholder="请输入数据集名称" />
            </el-form-item>
            <el-form-item label="数据内容">
              <el-input
                v-model="clipboardForm.text"
                type="textarea"
                :rows="10"
                placeholder="请将 CSV 或 JSON 格式数据粘贴到此处"
              />
            </el-form-item>
            <el-form-item label="格式">
              <el-radio-group v-model="clipboardForm.format_type">
                <el-radio label="csv">CSV</el-radio>
                <el-radio label="json">JSON</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitClipboard" :loading="uploading">提交</el-button>
              <el-button @click="$router.back()">取消</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled, Link, DataLine } from '@element-plus/icons-vue'
import { uploadFile as uploadFileApi, createFromText } from '@/api/dataset'

const router = useRouter()
const activeTab = ref('file')
const selectedFile = ref(null)
const uploading = ref(false)

const form = ref({
  name: '',
  description: ''
})

const clipboardForm = ref({
  name: '',
  text: '',
  format_type: 'csv'
})

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  if (!form.value.name) {
    form.value.name = file.name
  }
}

const submitUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const data = new FormData()
    data.append('file', selectedFile.value)
    data.append('name', form.value.name)
    data.append('description', form.value.description)

    await uploadFileApi(data)
    ElMessage.success('上传成功')
    router.push('/datasets')
  } catch (e) {
    console.error(e)
  } finally {
    uploading.value = false
  }
}

const submitClipboard = async () => {
  if (!clipboardForm.value.text) {
    ElMessage.warning('请输入数据内容')
    return
  }

  uploading.value = true
  try {
    await createFromText(clipboardForm.value)
    ElMessage.success('提交成功')
    router.push('/datasets')
  } catch (e) {
    console.error(e)
  } finally {
    uploading.value = false
  }
}

// 跳转到数据源配置页面
const goToDataSource = () => {
  router.push('/datasets/sources')
}

onMounted(() => {
  // 不再需要加载数据源列表
})
</script>

<style scoped lang="scss">
.dataset-upload {
  padding: 20px;
}

.upload-area {
  text-align: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 上传区域玻璃效果 - design02 色系 */
:deep(.el-upload-dragger) {
  background: rgba(57, 79, 73, 0.25) !important;
  backdrop-filter: blur(8px) !important;
  border: 2px dashed rgba(244, 253, 175, 0.2) !important;
  border-radius: 16px !important;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);

  &:hover {
    background: rgba(57, 79, 73, 0.4) !important;
    border-color: rgba(244, 253, 175, 0.4) !important;
    box-shadow: 0 4px 16px rgba(244, 253, 175, 0.1);
  }
}

/* 标签页玻璃效果 - design02 色系 */
:deep(.el-tabs__nav-wrap) {
  background: rgba(57, 79, 73, 0.3);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 4px;
}
</style>
