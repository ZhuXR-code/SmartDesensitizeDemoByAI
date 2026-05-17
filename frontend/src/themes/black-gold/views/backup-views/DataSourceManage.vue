<template>
  <div class="data-source-manage">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="connection-card">
          <template #header>
            <div class="card-header">
              <span>{{ isEditing ? '编辑数据源' : (currentSourceId ? '使用数据源' : '新建数据源') }}</span>
              <div v-if="currentSourceId || isEditing">
                <el-button size="small" @click="cancelEdit">取消</el-button>
              </div>
            </div>
          </template>

          <el-form :model="connectionForm" label-position="top" ref="connectionFormRef">
            <el-form-item label="数据源名称" required>
              <el-input v-model="connectionForm.source_name" placeholder="给这个数据源起个名字" />
            </el-form-item>

            <el-form-item label="数据库类型" required>
              <el-select v-model="connectionForm.db_type" placeholder="选择数据库类型" style="width: 100%">
                <el-option label="MySQL" value="mysql" />
                <el-option label="PostgreSQL" value="postgresql" />
                <el-option label="Oracle" value="oracle" />
                <el-option label="SQL Server" value="sqlserver" />
              </el-select>
            </el-form-item>

            <el-form-item label="主机地址" required>
              <el-input v-model="connectionForm.host" placeholder="例如: localhost 或 192.168.1.100" />
            </el-form-item>

            <el-form-item label="端口" required>
              <el-input-number v-model="connectionForm.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>

            <el-form-item label="数据库名" required>
              <el-input v-model="connectionForm.database" placeholder="数据库名称" />
            </el-form-item>

            <el-form-item label="用户名" required>
              <el-input v-model="connectionForm.username" placeholder="数据库用户名" />
            </el-form-item>

            <el-form-item label="密码" required>
              <el-input v-model="connectionForm.password" type="password" placeholder="数据库密码" show-password />
            </el-form-item>

            <el-divider />

            <el-form-item>
              <el-space wrap>
                <el-button type="primary" @click="testConnection" :loading="testing">
                  <el-icon><Link /></el-icon>
                  测试连接
                </el-button>
                
                <el-button type="success" @click="loadTables" :loading="loadingTables" :disabled="!connected">
                  <el-icon><Refresh /></el-icon>
                  加载表列表
                </el-button>

                <el-button 
                  v-if="!isEditing && !currentSourceId"
                  type="warning" 
                  @click="saveOnlyConfig"
                  :loading="saving"
                >
                  <el-icon><FolderAdd /></el-icon>
                  仅保存配置
                </el-button>

                <el-button 
                  v-if="isEditing"
                  type="success" 
                  @click="updateSourceConfig"
                  :loading="saving"
                >
                  <el-icon><Check /></el-icon>
                  更新配置
                </el-button>
              </el-space>
            </el-form-item>

            <el-alert 
              v-if="currentSourceId && !isEditing" 
              type="info" 
              :closable="false"
              show-icon
              style="margin-top: 10px"
            >
              当前使用已保存的数据源：<strong>{{ currentSourceName }}</strong> (ID: {{ currentSourceId }})
            </el-alert>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card v-if="tableList.length > 0" class="table-card">
          <template #header>
            <div class="card-header">
              <span>表列表 ({{ tableList.length }}个表)</span>
              <div>
                <el-input
                  v-model="tableSearch"
                  placeholder="搜索表名"
                  style="width: 200px; margin-right: 10px"
                  clearable
                />
                <el-button type="primary" @click="importSelectedTables" :loading="importing">
                  <el-icon><Download /></el-icon>
                  导入选中表到数据集 ({{ selectedTables.length }})
                </el-button>
              </div>
            </div>
          </template>

          <el-table
            :data="filteredTables"
            style="width: 100%"
            @selection-change="handleSelectionChange"
            height="400"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="name" label="表名" min-width="200" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button link type="primary" @click="previewTableData(scope.row.name)">
                  预览
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="import-options" v-if="selectedTables.length > 0">
            <el-divider />
            <el-form :inline="true">
              <el-form-item label="数据集名称前缀">
                <el-input v-model="namePrefix" placeholder="可选，例如: 生产环境_" style="width: 250px" />
              </el-form-item>
              <el-form-item>
                <el-tag type="info">已选择 {{ selectedTables.length }} 个表</el-tag>
              </el-form-item>
            </el-form>
          </div>
        </el-card>

        <el-card v-else-if="!loadingTables && connected" class="empty-card">
          <el-empty description="点击「加载表列表」获取数据库中的表" />
        </el-card>

        <el-card v-else class="empty-card">
          <el-empty description="请先配置数据库连接并测试成功，或从下方选择已保存的数据源" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>已保存的数据源配置</span>
              <el-tag type="info">{{ sourceList.length }} 个数据源</el-tag>
            </div>
          </template>

          <el-table :data="sourceList" style="width: 100%">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="name" label="数据源名称" min-width="150">
              <template #default="scope">
                <el-link type="primary" @click="useDataSource(scope.row)">
                  {{ scope.row.name }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="source_type" label="类型" width="90">
              <template #default="scope">
                <el-tag v-if="scope.row.source_type === 'database'" type="primary" size="small">数据库</el-tag>
                <el-tag v-else type="info" size="small">其他</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="连接信息" min-width="250">
              <template #default="scope">
                <span v-if="scope.row.config">
                  <el-tag size="small" type="info">{{ scope.row.config.db_type?.toUpperCase() }}</el-tag>
                  <span style="margin: 0 5px; color: #909399;">://</span>
                  <strong>{{ scope.row.config.username }}</strong>
                  <span style="margin: 0 3px; color: #909399;">@</span>
                  <span>{{ scope.row.config.host }}:{{ scope.row.config.port }}</span>
                  <span style="margin: 0 3px; color: #909399;">/</span>
                  <span>{{ scope.row.config.database }}</span>
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" />
            <el-table-column label="操作" width="380" fixed="right">
              <template #default="scope">
                <el-space>
                  <el-button link type="primary" size="small" @click="useDataSource(scope.row)">
                    使用
                  </el-button>
                  <el-button link type="success" size="small" @click="quickTestConnection(scope.row)" :loading="scope.row._testing">
                    测试连接
                  </el-button>
                  <el-button link type="warning" size="small" @click="editDataSource(scope.row)">
                    编辑
                  </el-button>
                  <el-button link type="primary" size="small" @click="viewSourceDatasets(scope.row)">
                    数据集
                  </el-button>
                  <el-button link type="danger" size="small" @click="deleteSource(scope.row)">
                    删除
                  </el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="previewVisible" title="表数据预览" width="800px">
      <div v-if="previewLoading" class="preview-loading">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else>
        <p><strong>表名:</strong> {{ previewData.table_name }}</p>
        <p><strong>总行数:</strong> {{ previewData.total_rows }}</p>
        <el-table :data="previewData.data" style="width: 100%; margin-top: 10px" max-height="400">
          <el-table-column
            v-for="col in previewData.columns"
            :key="col"
            :prop="col"
            :label="col"
            min-width="120"
          />
        </el-table>
      </div>
    </el-dialog>

    <el-dialog v-model="sourceDatasetsVisible" title="数据源关联的数据集" width="700px">
      <el-table :data="sourceDatasets" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="数据集名称" min-width="150" />
        <el-table-column prop="row_count" label="行数" width="100" />
        <el-table-column prop="column_count" label="列数" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button link type="primary" @click="goToDataset(scope.row.id)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Link, Refresh, Download, FolderAdd, Check } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import {
  testConnection as testConnectionApi,
  getTables,
  previewTable,
  saveAndImport,
  getDataSourceList,
  getSourceDatasets,
  deleteDataSource,
  saveDataSource,
  updateDataSource as updateDataSourceApi,
  testSavedConnection,
  getSavedSourceTables,
  previewSavedTable,
  importTablesFromSource,
  getDataSourceDetail
} from '@/api/datasource'

const router = useRouter()
const route = useRoute()

const connectionForm = ref({
  source_name: '',
  db_type: 'mysql',
  host: 'localhost',
  port: 3308,
  database: '',
  username: '',
  password: ''
})

const testing = ref(false)
const connected = ref(false)
const loadingTables = ref(false)
const importing = ref(false)
const saving = ref(false)
const tableList = ref([])
const tableSearch = ref('')
const selectedTables = ref([])
const namePrefix = ref('')

const previewVisible = ref(false)
const previewLoading = ref(false)
const previewData = ref({
  table_name: '',
  total_rows: 0,
  columns: [],
  data: []
})

const sourceList = ref([])
const sourceDatasetsVisible = ref(false)
const sourceDatasets = ref([])

const currentSourceId = ref(null)
const currentSourceName = ref('')
const isEditing = ref(false)
const editingSourceId = ref(null)

const filteredTables = computed(() => {
  if (!tableSearch.value) return tableList.value.map(name => ({ name }))
  return tableList.value
    .filter(name => name.toLowerCase().includes(tableSearch.value.toLowerCase()))
    .map(name => ({ name }))
})

const resetForm = () => {
  connectionForm.value = {
    source_name: '',
    db_type: 'mysql',
    host: 'localhost',
    port: 3308,
    database: '',
    username: '',
    password: ''
  }
  currentSourceId.value = null
  currentSourceName.value = ''
  isEditing.value = false
  editingSourceId.value = null
  connected.value = false
  tableList.value = []
  selectedTables.value = []
}

const cancelEdit = () => {
  resetForm()
}

const useDataSource = async (row) => {
  // 验证 row.id
  if (!row.id || isNaN(row.id)) {
    ElMessage.error('数据源ID无效')
    console.error('[ERROR] 数据源ID无效:', row)
    return
  }
  
  try {
    const res = await getDataSourceDetail(row.id)
    if (res.data) {
      const config = res.data.config
      
      connectionForm.value = {
        source_name: res.data.name,
        db_type: config.db_type || 'mysql',
        host: config.host || '',
        port: config.port || 3306,
        database: config.database || '',
        username: config.username || '',
        password: config.password || ''
      }
      
      currentSourceId.value = row.id
      currentSourceName.value = row.name
      isEditing.value = false
      editingSourceId.value = null
      connected.value = false
      tableList.value = []
      selectedTables.value = []
      
      ElMessage.success(`已加载数据源「${row.name}」的配置，可以测试连接或直接操作`)
    }
  } catch (error) {
    ElMessage.error('加载数据源失败: ' + (error.response?.data?.detail || error.message))
  }
}

const editDataSource = async (row) => {
  // 验证 row.id
  if (!row.id || isNaN(row.id)) {
    ElMessage.error('数据源ID无效')
    console.error('[ERROR] 数据源ID无效:', row)
    return
  }
  
  try {
    const res = await getDataSourceDetail(row.id)
    if (res.data) {
      const config = res.data.config
      
      connectionForm.value = {
        source_name: res.data.name,
        db_type: config.db_type || 'mysql',
        host: config.host || '',
        port: config.port || 3306,
        database: config.database || '',
        username: config.username || '',
        password: config.password || ''
      }
      
      currentSourceId.value = null
      currentSourceName.value = ''
      isEditing.value = true
      editingSourceId.value = row.id
      connected.value = false
      tableList.value = []
      selectedTables.value = []
      
      ElMessage.success(`正在编辑数据源「${row.name}」`)
    }
  } catch (error) {
    ElMessage.error('加载数据源失败: ' + (error.response?.data?.detail || error.message))
  }
}

const quickTestConnection = async (row) => {
  row._testing = true
  
  try {
    const res = await testSavedConnection(row.id)
    
    if (res.data && res.data.connected) {
      ElMessage.success(`数据源「${row.name}」连接成功！`)
    } else {
      ElMessage.error(`数据源「${row.name}」连接失败`)
    }
  } catch (error) {
    ElMessage.error('连接失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    setTimeout(() => {
      row._testing = false
    }, 500)
  }
}

const saveOnlyConfig = async () => {
  if (!validateForm()) return
  
  saving.value = true
  
  try {
    const res = await saveDataSource({
      name: connectionForm.value.source_name,
      db_type: connectionForm.value.db_type,
      host: connectionForm.value.host,
      port: connectionForm.value.port,
      username: connectionForm.value.username,
      password: connectionForm.value.password,
      database: connectionForm.value.database
    })
    
    if (res.data) {
      ElMessage.success(`数据源「${res.data.name}」配置已保存！`)
      resetForm()
      loadSourceList()
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const updateSourceConfig = async () => {
  if (!validateForm()) return
  
  saving.value = true
  
  try {
    const res = await updateDataSource(editingSourceId.value, {
      name: connectionForm.value.source_name,
      db_type: connectionForm.value.db_type,
      host: connectionForm.value.host,
      port: connectionForm.value.port,
      username: connectionForm.value.username,
      password: connectionForm.value.password,
      database: connectionForm.value.database
    })
    
    if (res.data) {
      ElMessage.success(`数据源「${res.data.name}」配置已更新！`)
      resetForm()
      loadSourceList()
    }
  } catch (error) {
    ElMessage.error('更新失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const testConnection = async () => {
  if (!validateForm()) return

  testing.value = true
  try {
    let res
    
    if (currentSourceId.value) {
      res = await testSavedConnection(currentSourceId.value)
    } else {
      res = await testConnectionApi({
        db_type: connectionForm.value.db_type,
        host: connectionForm.value.host,
        port: connectionForm.value.port,
        database: connectionForm.value.database,
        username: connectionForm.value.username,
        password: connectionForm.value.password
      })
    }

    if (res.data && res.data.connected) {
      connected.value = true
      ElMessage.success('连接成功！')
    } else {
      connected.value = false
      ElMessage.error(res.message || '连接失败')
    }
  } catch (error) {
    connected.value = false
    ElMessage.error('连接失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    testing.value = false
  }
}

const validateForm = () => {
  const f = connectionForm.value
  if (!f.source_name) { ElMessage.warning('请输入数据源名称'); return false }
  if (!f.host) { ElMessage.warning('请输入主机地址'); return false }
  if (!f.database) { ElMessage.warning('请输入数据库名'); return false }
  if (!f.username) { ElMessage.warning('请输入用户名'); return false }
  if (!f.password) { ElMessage.warning('请输入密码'); return false }
  return true
}

const loadTables = async () => {
  if (!validateForm()) return

  loadingTables.value = true
  try {
    let res
    
    if (currentSourceId.value) {
      res = await getSavedSourceTables(currentSourceId.value)
    } else {
      res = await getTables({
        db_type: connectionForm.value.db_type,
        host: connectionForm.value.host,
        port: connectionForm.value.port,
        database: connectionForm.value.database,
        username: connectionForm.value.username,
        password: connectionForm.value.password
      })
    }

    if (res.data && res.data.tables) {
      tableList.value = res.data.tables
      ElMessage.success(`成功加载 ${res.data.total} 个表`)
    }
  } catch (error) {
    ElMessage.error('加载表列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loadingTables.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedTables.value = selection.map(item => item.name)
}

const previewTableData = async (tableName) => {
  previewVisible.value = true
  previewLoading.value = true
  try {
    let res
    
    if (currentSourceId.value) {
      res = await previewSavedTable(currentSourceId.value, {
        table_name: tableName,
        limit: 10
      })
    } else {
      res = await previewTable({
        db_type: connectionForm.value.db_type,
        host: connectionForm.value.host,
        port: connectionForm.value.port,
        database: connectionForm.value.database,
        username: connectionForm.value.username,
        password: connectionForm.value.password,
        table_name: tableName,
        limit: 10
      })
    }

    if (res.data) {
      previewData.value = res.data
    }
  } catch (error) {
    ElMessage.error('预览失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    previewLoading.value = false
  }
}

const importSelectedTables = async () => {
  if (selectedTables.value.length === 0) {
    ElMessage.warning('请至少选择一个表')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定将选中的 ${selectedTables.value.length} 个表导入为数据集吗？`,
      '确认导入',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  importing.value = true
  try {
    let res
    
    if (currentSourceId.value) {
      res = await importTablesFromSource(currentSourceId.value, {
        selected_tables: selectedTables.value,
        name_prefix: namePrefix.value
      })
    } else {
      res = await saveAndImport({
        source_name: connectionForm.value.source_name,
        db_type: connectionForm.value.db_type,
        host: connectionForm.value.host,
        port: connectionForm.value.port,
        database: connectionForm.value.database,
        username: connectionForm.value.username,
        password: connectionForm.value.password,
        selected_tables: selectedTables.value,
        name_prefix: namePrefix.value
      })
    }

    if (res.data) {
      ElMessage.success(`成功导入 ${res.data.imported_count} 个数据集！`)
      tableList.value = []
      selectedTables.value = []
      namePrefix.value = ''
      
      if (!currentSourceId.value) {
        connected.value = false
      }
      
      loadSourceList()
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    importing.value = false
  }
}

const loadSourceList = async () => {
  try {
    const res = await getDataSourceList({ page: 1, page_size: 100 })
    if (res.data && res.data.items) {
      sourceList.value = res.data.items.map(item => ({
        ...item,
        _testing: false
      }))
    }
  } catch (error) {
    console.error('加载数据源列表失败:', error)
  }
}

const viewSourceDatasets = async (row) => {
  try {
    const res = await getSourceDatasets(row.id)
    if (res.data) {
      sourceDatasets.value = res.data
      sourceDatasetsVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载数据集失败')
  }
}

const goToDataset = (id) => {
  router.push(`/datasets/${id}`)
}

const deleteSource = async (row) => {
  try {
    await ElMessageBox.confirm(
      `删除数据源「${row.name}」将同时删除其关联的所有数据集，确定继续吗？`,
      '高危操作确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'danger' }
    )

    await deleteDataSource(row.id)
    ElMessage.success('数据源已删除')
    
    if (currentSourceId.value === row.id) {
      resetForm()
    }
    
    loadSourceList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(async () => {
  loadSourceList()
  
  const sourceId = route.query.id
  const mode = route.query.mode
  
  if (sourceId) {
    const parsedId = parseInt(sourceId)
    // 验证解析后的ID是否有效
    if (!isNaN(parsedId)) {
      if (mode === 'edit') {
        await editDataSource({ id: parsedId })
      } else {
        await useDataSource({ id: parsedId })
      }
    } else {
      console.warn('[WARN] URL参数中的sourceId无效:', sourceId)
      ElMessage.warning('数据源ID无效，请重新选择')
    }
  }
})
</script>

<style scoped lang="scss">
.data-source-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.connection-card {
  height: 100%;
}

.table-card {
  min-height: 500px;
}

.empty-card {
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.import-options {
  margin-top: 15px;
}

.preview-loading {
  padding: 20px;
}

/* 表格行悬浮效果 */
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
</style>
