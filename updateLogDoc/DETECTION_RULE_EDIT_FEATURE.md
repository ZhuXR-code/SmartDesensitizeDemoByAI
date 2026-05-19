# 识别规则编辑功能说明

## 📋 功能概述

为敏感数据识别规则管理页面添加了**编辑功能**，允许用户修改自定义添加的识别规则。

## ✨ 功能特性

### 1. 编辑按钮
- **位置**：识别规则管理页面的操作列
- **显示条件**：仅对自定义规则（非内置规则）显示"编辑"按钮
- **按钮样式**：橙色警告类型链接按钮

### 2. 编辑对话框
- **动态标题**：根据模式显示"新建识别规则"或"编辑识别规则"
- **表单复用**：与新建规则使用相同的表单组件
- **数据回填**：点击编辑时自动填充当前规则的所有字段

### 3. 支持的编辑字段
- ✅ 规则名称
- ✅ 适用语言（中文/英语/日语/韩语/法语/德语）
- ✅ 规则类型（正则表达式/关键词）
- ✅ 匹配模式（正则表达式模式下）
- ✅ 关键词列表（关键词模式下）
- ✅ 示例数据

### 4. 安全保护
- 🔒 **内置规则不可编辑**：系统内置规则不显示编辑按钮
- 🔒 **后端验证**：API层再次验证，防止修改内置规则
- 🔒 **取消重置**：点击取消按钮会重置表单状态

## 🔧 技术实现

### 后端 API

**文件**: `backend/app/api/detection.py`

```python
@router.put("/rules/{rule_id}", response_model=ResponseModel)
async def update_rule(rule_id: int, data: DetectionRuleCreate, db: Session = Depends(get_db)):
    """更新自定义识别规则"""
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    # 不允许修改内置规则
    if rule.is_builtin:
        raise HTTPException(status_code=403, detail="内置规则不可修改")
    
    rule.name = data.name
    rule.description = data.description
    rule.language = data.language
    rule.rule_type = data.rule_type
    rule.pattern = data.pattern or ""
    rule.keywords = data.keywords
    rule.example = data.example
    
    db.commit()
    db.refresh(rule)
    
    return ResponseModel(data={"id": rule.id, "name": rule.name}, message="规则更新成功")
```

**特性**：
- 使用 PUT 方法进行更新
- 验证规则是否存在
- 检查是否为内置规则（禁止修改）
- 更新所有可编辑字段
- 返回成功消息

### 前端 API

**文件**: `frontend/src/api/detection.js`

```javascript
export function updateDetectionRule(id, data) {
  return request.put(`/api/detection/rules/${id}`, data)
}
```

### 前端页面

**文件**: `frontend/src/views/detection/RuleManage.vue`

#### 新增状态变量
```javascript
const isEditMode = ref(false)          // 是否为编辑模式
const editingRuleId = ref(null)        // 正在编辑的规则ID
```

#### 新增函数

**1. handleEdit(row)** - 打开编辑对话框
```javascript
const handleEdit = (row) => {
  isEditMode.value = true
  editingRuleId.value = row.id
  
  // 填充表单数据
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
```

**2. submitCreate()** - 提交表单（支持新建和编辑）
```javascript
const submitCreate = async () => {
  try {
    if (isEditMode.value) {
      // 编辑模式
      await updateDetectionRule(editingRuleId.value, createForm.value)
      ElMessage.success('更新成功')
    } else {
      // 新建模式
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
```

**3. resetForm()** - 重置表单
```javascript
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
```

**4. handleCancel()** - 取消操作
```javascript
const handleCancel = () => {
  showCreateDialog.value = false
  resetForm()
}
```

#### UI 改动

**操作列宽度调整**：
```vue
<el-table-column label="操作" width="250">
```
从 200px 增加到 250px，以容纳新增的编辑按钮。

**编辑按钮**：
```vue
<el-button 
  v-if="!row.is_builtin" 
  link 
  type="warning" 
  @click="handleEdit(row)"
>
  编辑
</el-button>
```

**动态对话框标题**：
```vue
<el-dialog v-model="showCreateDialog" :title="isEditMode ? '编辑识别规则' : '新建识别规则'" width="600px">
```

**取消按钮**：
```vue
<el-button @click="handleCancel">取消</el-button>
```

## 🐛 已知问题修复

### 问题1：编辑时关键词/正则表达式字段为空

**现象**：
- 新建规则时输入了关键词或正则表达式
- 点击编辑按钮后，表单中对应的字段显示为空

**原因**：
后端 `GET /api/detection/rules` 接口返回规则列表时，**没有包含 `pattern` 和 `keywords` 字段**，导致前端无法获取这些数据进行回填。

**修复**：
在 `backend/app/api/detection.py` 的 `list_rules` 函数中，为内置规则和自定义规则的返回数据添加这两个字段：

```python
# 内置规则
all_rules.append({
    "id": r["id"],
    "name": r["name"],
    "language": r["language"],
    "rule_type": r["rule_type"],
    "pattern": r.get("pattern", ""),      # ✅ 新增
    "keywords": r.get("keywords"),         # ✅ 新增
    "example": r.get("example"),
    "is_builtin": True
})

# 自定义规则
all_rules.append({
    "id": r.id + 10000,
    "name": r.name,
    "language": r.language,
    "rule_type": r.rule_type,
    "pattern": r.pattern,                  # ✅ 新增
    "keywords": r.keywords,                # ✅ 新增
    "example": r.example,
    "is_builtin": False
})
```

**验证**：
1. 新建一个关键词类型的规则，输入多个关键词
2. 点击编辑按钮
3. 确认关键词字段正确显示之前输入的关键词
4. 同样测试正则表达式类型规则

---

### 问题2：查看详情时关键词列表显示优化

**需求**：
用户希望在查看关键词类型规则的详情时，能够清晰地看到所有关键词列表。

**优化内容**：

1. **布局优化**：使用 flexbox 布局，关键词自动换行
2. **样式美化**：
   - 标签大小从 `small` 改为 `default`，更易读
   - 使用绿色主题（`type="success"`）突出关键词
   - 使用朴素效果（`effect="plain"`）更清爽
   - 标签间距统一为 6px
3. **统计信息**：显示关键词总数，方便用户了解规则规模

**优化前**：
```vue
<el-tag v-for="kw in currentRule.keywords" :key="kw" size="small" style="margin: 2px;">
  {{ kw }}
</el-tag>
```

**优化后**：
```vue
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
```

**效果展示**：
```
关键词列表：
┌──────────┐ ┌──────────┐ ┌──────────┐
│  军人    │ │  军官    │ │  士兵    │
└──────────┘ └──────────┘ └──────────┘
共 3 个关键词
```

---

## 📝 使用流程

### 编辑自定义规则

1. **进入规则管理页面**
   - 导航到：敏感数据识别 → 识别规则管理

2. **找到要编辑的规则**
   - 在规则列表中查找目标规则
   - 确认"来源"列为"自定义"

3. **点击编辑按钮**
   - 在操作列点击橙色的"编辑"按钮
   - 对话框标题显示"编辑识别规则"
   - 表单自动填充当前规则的数据

4. **修改规则信息**
   - 修改需要更新的字段
   - 可以切换规则类型（正则/关键词）
   - 注意：切换类型时相关字段会变化

5. **保存或取消**
   - 点击"确定"：保存修改并刷新列表
   - 点击"取消"：放弃修改，关闭对话框

## ⚠️ 注意事项

### 1. ID偏移量机制
**为什么需要ID偏移？**
- 内置规则ID范围：1-100（在代码中定义）
- 自定义规则ID范围：从数据库自增（可能从1开始）
- **问题**：如果自定义规则ID也是1，会与内置规则冲突
- **解决方案**：前端显示时，自定义规则ID + 10000，避免ID冲突

**后端自动处理**：
```python
# 更新/删除接口会自动识别并转换ID
actual_id = rule_id - 10000 if rule_id >= 10000 else rule_id
```

### 2. 内置规则不可编辑
- 系统内置规则（如手机号、身份证等）不显示编辑按钮
- 即使通过其他方式尝试修改，后端也会拒绝请求

### 3. 表单验证
- 规则名称、语言、规则类型为必填项
- 正则模式下，pattern字段有效
- 关键词模式下，keywords数组有效

### 4. 数据一致性
- 修改规则后，已创建的识别任务不会自动更新
- 新任务会使用更新后的规则
- 建议在无任务运行时修改规则

## 🧪 测试建议

### 功能测试
1. ✅ 新建一个自定义规则
2. ✅ 编辑刚创建的规则，修改名称
3. ✅ 编辑规则，切换规则类型（正则→关键词）
4. ✅ 编辑规则，修改语言和示例
5. ✅ 确认内置规则没有编辑按钮
6. ✅ 点击取消按钮，确认表单重置
7. ✅ 编辑后确认列表数据已更新

### 边界测试
1. 尝试修改不存在的规则ID
2. 尝试修改已被删除的规则
3. 网络异常时的错误提示
4. 并发编辑同一规则的情况

## 📊 界面截图说明

### 操作列布局
```
| 查看详情 | 编辑 | 删除 |
```
- **查看详情**：蓝色，所有规则可见
- **编辑**：橙色，仅自定义规则可见
- **删除**：红色，仅自定义规则可见

### 对话框标题
- **新建模式**：`新建识别规则`
- **编辑模式**：`编辑识别规则`

## 🔄 与相关功能的集成

### 规则集管理
- 编辑规则后，引用该规则的规则集会自动使用新版本
- 无需手动更新规则集

### 识别任务
- 新建任务时使用最新的规则配置
- 运行中的任务不受影响

### 脱敏推荐
- 规则修改可能影响自动检测的推荐结果
- 建议在修改后重新测试自动检测功能

## 📅 更新日志

**版本**: v1.0  
**日期**: 2026-05-17  
**作者**: AI Assistant

### 新增功能
- ✅ 自定义识别规则编辑功能
- ✅ 动态对话框标题（新建/编辑）
- ✅ 表单数据回填
- ✅ 取消操作表单重置
- ✅ 内置规则保护机制

### 技术优化
- 复用新建表单组件，减少代码冗余
- 统一的状态管理（isEditMode）
- 完善的错误处理和用户提示

---

**相关文件**：
- `backend/app/api/detection.py` - 后端API
- `frontend/src/api/detection.js` - 前端API封装
- `frontend/src/views/detection/RuleManage.vue` - 规则管理页面
