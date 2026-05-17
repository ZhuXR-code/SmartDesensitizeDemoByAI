# 自动识别并脱敏功能实现文档

## 📋 功能概述

在创建脱敏任务时，新增"自动识别并脱敏"模式。选择此模式后：
- ✅ 所有语言配置、规则配置全部置灰无法选择
- ✅ 系统在处理过程中自动为每个字段智能匹配最合适的脱敏规则
- ✅ 每行数据的每个字段可能使用不同的规则
- ✅ 脱敏结果会展示具体使用的语言和规则信息
- ✅ 预览和试脱敏部分也会显示详细的规则信息

## 🎯 核心特性

### 1. 两种模式对比

| 特性 | 手动配置模式 | 自动识别模式 |
|------|------------|------------|
| 规则配置 | 用户手动选择 | 系统自动匹配 |
| 语言选择 | 用户指定 | 自动检测 |
| 灵活性 | 固定规则 | 动态匹配 |
| 适用场景 | 明确知道数据类型 | 数据混杂、未知类型 |
| 规则一致性 | 全表统一规则 | 每行每列可能不同 |

### 2. 自动识别流程

```
原始数据 → DetectionEngine扫描 → 匹配检测规则 → 映射脱敏规则 → 执行脱敏 → 展示结果
```

**详细步骤：**
1. 读取数据样本（前10行用于预览）
2. 对每个单元格调用`DetectionEngine.scan_text()`
3. 获取置信度最高的检测结果
4. 通过映射表找到对应的脱敏规则ID
5. 执行脱敏操作
6. 返回包含rule_info的预览数据

### 3. 规则映射关系

| 检测规则ID | 检测类型 | 脱敏规则ID | 脱敏方式 |
|-----------|---------|-----------|---------|
| 1 | 手机号 | 3 | 手机号仿真 |
| 2 | 身份证 | 4 | 身份证号仿真 |
| 3 | 邮箱 | 19 | 邮箱部分遮盖 |
| 4 | 银行卡 | 5 | 银行卡号仿真 |
| 5 | 地址 | 6 | 地址仿真 |
| 6 | 姓名 | 2 | 姓名仿真 |
| 7 | 国家 | 7 | 国家仿真 |
| 13 | 姓名 | 13 | 姓名部分遮盖 |
| 15 | 手机号 | 14 | 手机号部分遮盖 |
| 16 | 身份证 | 15 | 身份证部分遮盖 |
| 17 | 银行卡 | 16 | 银行卡号部分遮盖 |
| 18 | 地址 | 17 | 地址部分遮盖 |
| 19 | 国家 | 18 | 国家部分遮盖 |

**默认规则**: 未检测到敏感信息时，使用规则ID=1（完全遮盖）

## 🔧 技术实现

### 前端实现

#### 1. 模式选择UI
**文件**: `frontend/src/views/desensitization/CreateTask.vue`

```vue
<el-radio-group v-model="desensitizationMode" @change="onModeChange">
  <el-radio label="manual">手动配置规则</el-radio>
  <el-radio label="auto">自动识别并脱敏</el-radio>
</el-radio-group>
```

#### 2. 条件渲染
- **手动模式**: 显示完整的字段配置表格（语言、方式、规则）
- **自动模式**: 显示说明提示，隐藏配置项

#### 3. 预览增强
自动模式下，预览表格每个单元格显示：
```vue
<div class="cell-content">
  <div class="original">原: {{ original }}</div>
  <div class="desensitized">脱: {{ desensitized }}</div>
  
  <!-- 规则信息标签 -->
  <div class="rule-info">
    <el-tag>{{ language }}</el-tag>
    <el-tag type="primary">{{ rule_name }}</el-tag>
  </div>
</div>
```

#### 4. 统计信息
```javascript
autoDetectStats = {
  total_fields: 150,           // 检测字段总数
  language_dist: {             // 语言分布
    zh: 80,
    en: 50,
    ja: 20
  },
  unique_rules: 12             // 使用的唯一规则数
}
```

### 后端实现

#### 1. Schema扩展
**文件**: `backend/app/schemas/desensitization.py`

```python
class PreviewRequest(BaseModel):
    dataset_id: int
    field_rules: Optional[Dict[str, int]] = {}  # 手动模式
    auto_detect: Optional[bool] = False         # 自动模式标记
    key_id: Optional[int] = None
    limit: int = 10

class DesensitizationTaskCreate(BaseModel):
    # ... 其他字段
    field_rules: Optional[Dict[str, int]] = {}
    auto_detect: Optional[bool] = False
```

#### 2. API路由
**文件**: `backend/app/api/desensitization.py`

```python
@router.post("/preview")
async def preview_desensitization(data: PreviewRequest):
    if data.auto_detect:
        previews = engine.preview_auto_desensitization(df, key_id, limit)
    else:
        previews = engine.preview_desensitization(df, field_rules, key_id, limit)
```

#### 3. 引擎方法
**文件**: `backend/app/services/desensitization_engine.py`

##### preview_auto_desensitization()
```python
def preview_auto_desensitization(self, df, key_id, limit):
    """自动识别预览"""
    detection_engine = DetectionEngine()
    
    for each cell in sample_data:
        matches = detection_engine.scan_text(original, column_name)
        best_match = max(matches, key=lambda m: m.confidence)
        rule_id = self._find_rule_by_detection(best_match)
        desensitized = self.desensitize(original, rule_id, key_id)
        
        return {
            "original": original,
            "desensitized": desensitized,
            "rule_info": {
                "rule_id": rule_id,
                "rule_name": "...",
                "language": "...",
                "confidence": 0.95
            }
        }
```

##### process_auto_desensitization()
```python
def process_auto_desensitization(self, df, key_id, progress_callback):
    """全量数据自动脱敏处理"""
    # 与preview逻辑相同，但处理全部数据
    # 支持进度回调
```

##### 辅助方法
```python
def _find_rule_by_detection(self, match):
    """检测规则ID → 脱敏规则ID映射"""
    mapping = {1: 3, 2: 4, ...}
    return mapping.get(match.rule_id)

def _get_rule_info(self, rule_id):
    """获取规则详细信息"""
    return {"name": "...", "language": "..."}
```

#### 4. 任务执行
**文件**: `backend/app/api/desensitization.py`

```python
def run_desensitization_task(task_id, db):
    # 检查是否为自动模式
    is_auto_detect = task.logs and "auto_detect=true" in task.logs
    
    if is_auto_detect:
        result_df, matches = engine.process_auto_desensitization(df, key_id, callback)
    else:
        result_df, matches = engine.process_dataframe(df, field_rules, key_id, callback)
```

**注意**: 使用`task.logs`字段临时存储`auto_detect`标记（因为数据库模型中没有该字段）

## 📊 数据流

### 预览流程
```
用户点击"下一步"
  ↓
前端发送 {auto_detect: true, dataset_id: 1, limit: 10}
  ↓
后端调用 preview_auto_desensitization()
  ↓
DetectionEngine.scan_text() 识别每个单元格
  ↓
映射到脱敏规则并执行
  ↓
返回包含rule_info的预览数据
  ↓
前端展示 + 统计信息
```

### 任务执行流程
```
用户点击"开始脱敏"
  ↓
前端发送 {auto_detect: true, dataset_id: 1, ...}
  ↓
后端创建任务，设置 logs="auto_detect=true"
  ↓
后台任务 run_desensitization_task()
  ↓
检测到 auto_detect 标记
  ↓
调用 process_auto_desensitization()
  ↓
逐行逐列自动识别并脱敏
  ↓
保存结果文件和匹配记录
  ↓
任务完成
```

## 🎨 UI/UX设计

### 1. 模式切换
- 清晰的单选按钮组
- 切换时显示提示信息
- 自动模式下配置区域隐藏

### 2. 预览展示
- 原数据和脱敏数据上下排列
- 规则信息用Tag标签展示
- 颜色区分：语言(info蓝色)、规则(primary主色)

### 3. 统计面板
- 灰色背景卡片
- 三列布局展示关键指标
- 语言分布用多个Tag展示

### 4. 成功提示
- 绿色Alert提示框
- 明确告知用户自动识别已完成

## ✅ 测试要点

### 功能测试
1. **模式切换**
   - [ ] 切换到自动模式，配置区域隐藏
   - [ ] 切换回手动模式，配置区域显示

2. **预览功能**
   - [ ] 自动模式下点击"下一步"能正常预览
   - [ ] 每个单元格显示rule_info
   - [ ] 统计信息正确计算

3. **任务创建**
   - [ ] 自动模式能成功创建任务
   - [ ] 任务执行时使用正确的处理方法
   - [ ] 结果文件中数据已脱敏

4. **规则匹配**
   - [ ] 手机号正确识别并脱敏
   - [ ] 身份证正确识别并脱敏
   - [ ] 未识别字段使用默认规则

### 边界测试
1. **空数据处理**
   - [ ] 空单元格跳过处理
   - [ ] "nan"字符串跳过处理

2. **混合数据**
   - [ ] 同一列不同行使用不同规则
   - [ ] 不同语言数据正确识别

3. **性能测试**
   - [ ] 大数据集预览速度可接受
   - [ ] 进度回调正常工作

## 🐛 已知限制

1. **规则映射不完整**
   - 当前只映射了13种常见检测规则
   - 新增检测规则需要同步更新映射表

2. **日志字段滥用**
   - 使用`task.logs`存储`auto_detect`标记
   - 建议后续在数据库模型中添加专用字段

3. **置信度阈值**
   - 当前没有设置最低置信度
   - 低置信度匹配可能导致错误脱敏

4. **性能考虑**
   - 自动识别比手动配置慢（需要调用DetectionEngine）
   - 大数据集建议使用异步任务

## 🚀 部署步骤

1. **后端修改**
   ```bash
   # 已修改的文件
   backend/app/schemas/desensitization.py
   backend/app/api/desensitization.py
   backend/app/services/desensitization_engine.py
   ```

2. **前端修改**
   ```bash
   # 已修改的文件
   frontend/src/views/desensitization/CreateTask.vue
   ```

3. **重启服务**
   ```bash
   cd backend
   python run.py
   
   # 前端会自动热重载
   ```

4. **验证功能**
   - 访问创建脱敏任务页面
   - 选择"自动识别并脱敏"模式
   - 点击下一步查看预览
   - 确认rule_info正确显示

## 📝 使用示例

### 场景1: 多语言混合数据
```
数据集包含：
- 中文姓名：张三、李四
- 英文邮箱：john@example.com
- 日本地址：東京都渋谷区

自动识别结果：
张三     → 李伟      (中文, 姓名仿真)
john@..  → mary@..   (英语, 邮箱部分遮盖)
東京都.. → 大阪府..  (日语, 地址仿真)
```

### 场景2: 不确定数据类型
```
用户不知道某列是什么数据
手动模式：需要逐个尝试规则
自动模式：系统自动识别为手机号并脱敏
```

### 场景3: 数据质量检查
```
通过查看rule_info中的confidence字段
可以评估数据识别的准确性
低置信度的数据可能需要人工复核
```

## 🔮 未来优化

1. **添加置信度阈值配置**
   - 用户可设置最低置信度
   - 低于阈值的字段标记为"待确认"

2. **规则映射配置化**
   - 将映射关系存储在数据库中
   - 支持用户自定义映射

3. **批量学习优化**
   - 根据用户反馈优化识别算法
   - 建立领域特定的识别模型

4. **性能优化**
   - 缓存检测结果
   - 并行处理多列数据

---

**实现时间**: 2026-05-16  
**版本**: v1.0  
**维护者**: AI Assistant
