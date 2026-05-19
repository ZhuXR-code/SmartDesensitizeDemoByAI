<template>
  <div class="dataset-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据集管理</span>
          <el-button type="primary" @click="$router.push('/datasets/upload')">
            <el-icon><Plus /></el-icon> 导入数据
          </el-button>
        </div>
      </template>
      
      <el-table :data="datasets" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="source_type" label="来源类型">
          <template #default="{ row }">
            <el-tag>{{ row.source_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="row_count" label="行数">
          <template #default="{ row }">
            {{ row.row_count }} 行
          </template>
        </el-table-column>
        <el-table-column prop="column_count" label="列数">
          <template #default="{ row }">
            {{ row.column_count }} 列
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-space :size="4">
              <el-tooltip content="查看数据集详情" placement="top">
                <el-button type="primary" size="small" @click="viewDetail(row)">查看</el-button>
              </el-tooltip>
              <el-tooltip content="删除该数据集" placement="top">
                <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
              </el-tooltip>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 20px;"
        @change="loadData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDatasetList, deleteDataset } from '@/api/dataset'

const router = useRouter()
const loading = ref(false)
const datasets = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getDatasetList({ page: page.value, page_size: pageSize.value })
    datasets.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const viewDetail = (row) => {
  router.push(`/datasets/${row.id}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该数据集？', '提示', { type: 'warning' })
    await deleteDataset(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
