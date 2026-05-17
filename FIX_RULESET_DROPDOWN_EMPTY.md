# 识别任务规则集下拉框为空问题修复

## 🐛 问题描述

**现象**：用户新建了敏感数据识别的规则集，但在创建识别任务时，规则集下拉框显示为空，无法选择已创建的规则集。

**影响**：用户无法在创建任务时选择自定义规则集，只能使用默认的全部规则。

## 🔍 问题原因

**根本原因**：前端导入的API函数名与实际导出的函数名不一致。

### 代码对比

**错误的导入**（`CreateTask.vue` 第91行）：
```javascript
import { getDetectionRuleSets, createDetectionTask } from '@/api/detection'
```

**实际的导出**（`detection.js` 第19行）：
```javascript
export function getRuleSets(params) {
  return request.get('/api/detection/rule-sets', { params })
}
```

**问题**：
- 导入的函数名：`getDetectionRuleSets`
- 导出的函数名：`getRuleSets`
- **名称不匹配导致导入失败，函数为 `undefined`**

### 调用失败

在第132行调用时：
```javascript
const res = await getDetectionRuleSets()  // ❌ getDetectionRuleSets is not defined
```

由于函数未正确导入，调用时会报错，导致规则集列表无法加载。

## ✅ 修复方案

### 修改文件

**文件**: `frontend/src/views/detection/CreateTask.vue`

### 修改内容

#### 1. 修正导入语句（第91行）

**修改前**：
```javascript
import { getDetectionRuleSets, createDetectionTask } from '@/api/detection'
```

**修改后**：
```javascript
import { getRuleSets, createDetectionTask } from '@/api/detection'
```

#### 2. 修正函数调用（第130-137行）

**修改前**：
```javascript
const loadRuleSets = async () => {
  try {
    const res = await getDetectionRuleSets()
    ruleSets.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}
```

**修改后**：
```javascript
const loadRuleSets = async () => {
  try {
    const res = await getRuleSets()
    ruleSets.value = res.data || []
    console.log('加载规则集成功:', ruleSets.value)
  } catch (e) {
    console.error('加载规则集失败:', e)
  }
}
```

**改进点**：
1. ✅ 修正函数名为 `getRuleSets`
2. ✅ 添加成功日志，方便调试
3. ✅ 优化错误日志，更清晰地显示错误信息

## 📋 API函数命名规范

为了保持一致性，项目中规则集相关的API函数命名如下：

| 功能 | 函数名 | 请求方法 | 路径 |
|------|--------|----------|------|
| 获取规则集列表 | `getRuleSets` | GET | `/api/detection/rule-sets` |
| 创建规则集 | `createRuleSet` | POST | `/api/detection/rule-sets` |
| 更新规则集 | `updateRuleSet` | PUT | `/api/detection/rule-sets/{id}` |
| 删除规则集 | `deleteRuleSet` | DELETE | `/api/detection/rule-sets/{id}` |
| 获取规则集详情 | `getRuleSetDetail` | GET | `/api/detection/rule-sets/{id}` |

**注意**：
- ✅ 统一使用 `RuleSet` 而非 `DetectionRuleSet`
- ✅ 保持简洁明了的命名风格
- ✅ 与后端API路径保持一致

## 🧪 验证步骤

### 1. 创建规则集
1. 进入"敏感数据识别 → 规则集管理"
2. 点击"新建规则集"
3. 填写规则集名称、描述
4. 选择要包含的规则
5. 保存规则集

### 2. 创建识别任务
1. 进入"敏感数据识别 → 识别任务 → 创建任务"
2. 选择一个数据集
3. 点击"下一步"
4. **检查规则集下拉框**：应该能看到刚才创建的规则集
5. 选择规则集（可选）
6. 完成其他配置
7. 启动任务

### 3. 控制台验证
打开浏览器开发者工具（F12），查看Console：
```
加载规则集成功: [{id: 1, name: "我的规则集", ...}]
```

## 🔧 相关代码位置

### 前端文件

1. **API定义**
   - 文件：`frontend/src/api/detection.js`
   - 函数：`getRuleSets`（第19-21行）

2. **任务创建页面**
   - 文件：`frontend/src/views/detection/CreateTask.vue`
   - 导入：第91行
   - 调用：第132行
   - 下拉框：第38-45行

### 后端API

- 路由：`backend/app/api/detection.py`
- 接口：`GET /api/detection/rule-sets`（第121-132行）

## 💡 预防措施

### 1. 统一的命名规范
建立前端API函数的命名规范：
```javascript
// ✅ 推荐：简洁明了
export function getRuleSets() { ... }
export function createRuleSet() { ... }

// ❌ 避免：冗余前缀
export function getDetectionRuleSets() { ... }
export function createDetectionRuleSet() { ... }
```

### 2. IDE辅助
- 使用TypeScript或JSDoc类型提示
- 启用IDE的导入检查功能
- 配置ESLint规则检测未使用的导入

### 3. 代码审查
- PR中重点检查API导入是否正确
- 测试所有涉及API调用的功能
- 添加单元测试覆盖API调用

### 4. 日志记录
在关键API调用处添加日志：
```javascript
console.log('加载规则集成功:', ruleSets.value)
console.error('加载规则集失败:', e)
```

## 📝 类似问题排查

如果遇到其他下拉框为空的问题，可以按以下步骤排查：

1. **检查导入语句**
   ```javascript
   // 确认导入的函数名是否正确
   import { correctFunctionName } from '@/api/xxx'
   ```

2. **检查API导出**
   ```javascript
   // 确认API文件中是否正确导出
   export function correctFunctionName() { ... }
   ```

3. **检查控制台错误**
   - 打开浏览器Console
   - 查找 `is not defined` 或 `is not a function` 错误

4. **检查网络请求**
   - 打开Network面板
   - 确认API请求是否发送
   - 检查响应状态码和数据

5. **添加调试日志**
   ```javascript
   console.log('API返回数据:', res.data)
   ```

## 📅 修复记录

**日期**: 2026-05-17  
**版本**: v1.0  
**修复人**: AI Assistant

### 修改文件
- ✅ `frontend/src/views/detection/CreateTask.vue`

### 修改内容
- ✅ 修正API函数导入名称
- ✅ 修正API函数调用
- ✅ 添加调试日志

### 测试结果
- ✅ 规则集下拉框正常显示
- ✅ 可以选择已创建的规则集
- ✅ 任务创建功能正常

---

**相关文件**：
- [检测模块API](./frontend/src/api/detection.js)
- [创建任务页面](./frontend/src/views/detection/CreateTask.vue)
- [规则集管理页面](./frontend/src/views/detection/RuleSetManage.vue)
