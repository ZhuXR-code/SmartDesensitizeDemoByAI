# 脱敏文件下载格式选择功能

## 功能概述

在脱敏详情页面中，用户可以选择下载两种不同格式的脱敏文件：

1. **对比数据文件**：包含原始值和脱敏后值的对比，方便审核和验证
2. **纯脱敏文件**：只包含脱敏后的数据，可直接使用

## 实现内容

### 1. 数据库修改

#### 新增字段
在 `ai_desensitization_tasks` 表中添加新字段：
```sql
ALTER TABLE ai_desensitization_tasks 
ADD COLUMN output_file_pure_path VARCHAR(500) DEFAULT '' COMMENT '纯脱敏文件路径';
```

#### 迁移脚本
- SQL脚本：`backend/add_pure_output_file_path.sql`
- Python脚本：`backend/migrate_add_pure_output_file_path.py`

执行迁移：
```bash
cd backend
python migrate_add_pure_output_file_path.py
```

### 2. 后端修改

#### 模型层 (`backend/app/models/ai.py`)
在 `AiDesensitizationTask` 类中添加字段：
```python
output_file_pure_path = Column(String(500), default="", comment="纯脱敏文件路径")
```

#### 服务层 (`backend/app/services/ai_service.py`)
修改 `run_desensitization` 方法，同时生成两种文件：

1. **对比文件**（compare）：
   - 文件名：`ai_desensitize_compare_{task_id}_{timestamp}.xlsx`
   - 格式：包含"列名(原始)"和"列名(脱敏后)"两列
   
2. **纯脱敏文件**（pure）：
   - 文件名：`ai_desensitize_{task_id}_{timestamp}.xlsx`
   - 格式：只包含列名和脱敏后的值

保存两个文件路径到数据库：
```python
task.output_file_path = compare_output_path  # 对比文件路径
task.output_file_pure_path = pure_output_path  # 纯脱敏文件路径
```

#### API层 (`backend/app/api/ai.py`)
修改 `get_desensitization_task` API，返回两个文件路径：
```python
{
    "output_file_path": task.output_file_path,
    "output_file_pure_path": task.output_file_pure_path or ""
}
```

### 3. 前端修改

#### UI组件 (`frontend/src/views/ai/AiDetection.vue`)

##### 1. 添加下载格式选择对话框
```vue
<el-dialog v-model="downloadDialogVisible" title="选择下载格式" width="500px">
  <el-radio-group v-model="downloadFormat">
    <el-radio value="compare" border>
      <span style="font-weight: 600;">对比数据文件</span>
      <span style="font-size: 12px; color: #909399;">包含原始值和脱敏后值的对比，方便审核和验证</span>
    </el-radio>
    
    <el-radio value="pure" border>
      <span style="font-weight: 600;">纯脱敏文件</span>
      <span style="font-size: 12px; color: #909399;">只包含脱敏后的数据，可直接使用</span>
    </el-radio>
  </el-radio-group>
  
  <template #footer>
    <el-button @click="downloadDialogVisible = false">取消</el-button>
    <el-button type="primary" @click="confirmDownload">下载</el-button>
  </template>
</el-dialog>
```

##### 2. 修改下载按钮触发方式
将原来的直接下载改为显示选择对话框：
```vue
<!-- 之前 -->
<el-button @click="downloadFile(detailData.task.output_file_path)">下载</el-button>

<!-- 之后 -->
<el-button @click="showDownloadDialog">下载</el-button>
```

##### 3. 添加相关逻辑
```javascript
// 状态变量
const downloadDialogVisible = ref(false)
const downloadFormat = ref('compare')

// 显示下载对话框
const showDownloadDialog = () => {
  downloadFormat.value = 'compare' // 默认选择对比文件
  downloadDialogVisible.value = true
}

// 确认下载
const confirmDownload = () => {
  if (!detailData.value?.task) return
  
  let filePath = ''
  if (downloadFormat.value === 'compare') {
    filePath = detailData.value.task.output_file_path
  } else if (downloadFormat.value === 'pure') {
    filePath = detailData.value.task.output_file_pure_path
  }
  
  if (!filePath) {
    ElMessage.warning('该文件不存在')
    return
  }
  
  downloadFile(filePath)
  downloadDialogVisible.value = false
}
```

## 用户使用流程

1. 用户点击脱敏任务列表中的"查看"按钮
2. 打开脱敏详情对话框
3. 点击"输出文件"区域的"下载"按钮
4. 弹出"选择下载格式"对话框
5. 选择需要的文件格式：
   - **对比数据文件**：用于审核、验证脱敏效果
   - **纯脱敏文件**：用于直接使用脱敏后的数据
6. 点击"下载"按钮，开始下载选定的文件

## 技术细节

### 文件命名规则
- 对比文件：`ai_desensitize_compare_{task_id}_{timestamp}.xlsx`
- 纯脱敏文件：`ai_desensitize_{task_id}_{timestamp}.xlsx`

### 文件格式示例

#### 对比文件
| 行号 | 姓名(原始) | 姓名(脱敏后) | 手机号(原始) | 手机号(脱敏后) |
|------|-----------|-------------|-------------|---------------|
| 0    | 张三      | 张*         | 13812345678 | 138****5678   |
| 1    | 李四      | 李*         | 13987654321 | 139****4321   |

#### 纯脱敏文件
| 姓名 | 手机号       |
|------|-------------|
| 张*  | 138****5678 |
| 李*  | 139****4321 |

### 兼容性处理
- 如果某个文件路径为空（例如旧数据），会提示"该文件不存在"
- 默认选择"对比数据文件"，保持与原有行为一致
- 后端API返回时使用 `or ""` 确保不会返回 `null`

## 测试建议

1. **新建脱敏任务测试**：
   - 创建新的脱敏任务并执行
   - 验证是否生成了两个文件
   - 检查数据库中两个字段都有值

2. **下载功能测试**：
   - 点击"下载"按钮，验证对话框正常显示
   - 分别选择两种格式下载
   - 验证下载的文件内容正确

3. **边界情况测试**：
   - 测试只有对比文件的情况（旧数据）
   - 测试只有纯脱敏文件的情况
   - 测试两个文件都不存在的情况

4. **UI体验测试**：
   - 验证对话框样式美观
   - 验证选项描述清晰易懂
   - 验证默认选项合理

## 注意事项

1. **数据库迁移**：必须先执行迁移脚本添加新字段，否则会导致错误
2. **文件清理**：定期清理旧的脱敏文件时，需要同时清理两种文件
3. **存储空间**：每个脱敏任务会生成两个文件，注意磁盘空间管理
4. **向后兼容**：对于已有的脱敏任务，`output_file_pure_path` 可能为空，前端已做兼容处理

## 相关文件清单

### 后端文件
- `backend/app/models/ai.py` - 数据库模型
- `backend/app/services/ai_service.py` - 业务逻辑
- `backend/app/api/ai.py` - API接口
- `backend/add_pure_output_file_path.sql` - SQL迁移脚本
- `backend/migrate_add_pure_output_file_path.py` - Python迁移脚本

### 前端文件
- `frontend/src/views/ai/AiDetection.vue` - 主界面

## 完成时间
2026-05-18
