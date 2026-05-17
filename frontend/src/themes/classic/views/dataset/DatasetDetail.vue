<template>
  <div class="dataset-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ dataset.name }}</span>
          <div>
            <el-button type="primary" @click="goToDetection">识别敏感数据</el-button>
            <el-button type="warning" @click="goToDesensitization">数据脱敏</el-button>
          </div>
        </div>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="ID">{{ dataset.id }}</el-descriptions-item>
        <el-descriptions-item label="来源类型">{{ dataset.source_type }}</el-descriptions-item>
        <el-descriptions-item label="编码">{{ dataset.encoding }}</el-descriptions-item>
        <el-descriptions-item label="行数">{{ dataset.row_count }} 行</el-descriptions-item>
        <el-descriptions-item label="列数">{{ dataset.column_count }} 列</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ dataset.created_at }}</el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px;">
        <h4>数据预览</h4>
        <el-table :data="previewData" size="small" style="margin-top: 10px;">
          <el-table-column
            v-for="col in columns"
            :key="col"
            :prop="col"
            :label="col"
          />
        </el-table>
        
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="dataset.row_count || 0"
          layout="prev, pager, next"
          style="margin-top: 10px;"
          @change="loadPreview"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDatasetDetail, getDatasetPreview } from '@/api/dataset'

const route = useRoute()
const router = useRouter()
const datasetId = route.params.id

const loading = ref(false)
const dataset = ref({})
const columns = ref([])
const previewData = ref([])
const page = ref(1)
const pageSize = ref(20)

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await getDatasetDetail(datasetId)
    dataset.value = res.data || {}
    columns.value = res.data.columns || []
    await loadPreview()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadPreview = async () => {
  try {
    const res = await getDatasetPreview(datasetId, {
      page: page.value,
      page_size: pageSize.value
    })
    previewData.value = res.data.data || []
  } catch (e) {
    console.error(e)
  }
}

const goToDetection = () => {
  router.push(`/detection/tasks/create?dataset_id=${datasetId}`)
}

const goToDesensitization = () => {
  router.push(`/desensitization/tasks/create?dataset_id=${datasetId}`)
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
