# DeepSeek 思考模式功能说明

## 功能概述

本次更新添加了两个重要功能：
1. **DeepSeek 思考模式开关** - 允许用户控制 DeepSeek 模型是否进行深度推理
2. **任务打断功能（预留）** - 为将来实现任务取消功能预留接口

## 一、DeepSeek 思考模式

### 1.1 功能说明

当使用 DeepSeek 模型时，用户可以开启或关闭"思考模式"：
- **开启（深度推理）**：模型会进行更深入的分析和推理，适合复杂的敏感数据识别任务
- **关闭（快速响应）**：模型快速响应，适合简单的数据识别场景

### 1.2 技术实现

#### 前端修改
- 文件：`frontend/src/views/ai/AiDetection.vue`
- 添加了 `enable_thinking` 字段到 detectForm
- 添加了计算属性 `isDeepSeekModel` 判断当前选择的模型是否为 DeepSeek
- 仅在选择了 DeepSeek 模型时显示思考模式开关

#### 后端修改
1. **数据库模型** (`backend/app/models/ai.py`)
   - `AiConfig` 表添加 `enable_thinking` 字段
   - `AiDetectionTask` 表添加 `enable_thinking` 字段

2. **AI 服务** (`backend/app/services/ai_service.py`)
   - 加载配置时读取 `enable_thinking` 参数
   - 在 `_call_llm` 方法中，当 provider 为 'deepseek' 时，添加 `enable_thinking` 参数到 API 请求

3. **数据库迁移脚本** (`backend/add_enable_thinking_field.py`)
   - 自动检测并添加字段到数据库表

### 1.3 使用方法

1. 运行数据库迁移脚本：
```bash
cd backend
python add_enable_thinking_field.py
```

2. 在 AI 智能识别页面：
   - 选择 DeepSeek 模型
   - 会看到"DeepSeek思考模式"选项
   - 根据需要开启或关闭

### 1.4 API 调用示例

当 enable_thinking=true 时，发送给 DeepSeek API 的请求包含：
```json
{
  "model": "deepseek-chat",
  "messages": [...],
  "temperature": 0.3,
  "max_tokens": 4096,
  "enable_thinking": true
}
```

## 二、任务打断功能

### 2.1 当前状态

目前前端已添加"打断"按钮和交互逻辑，但后端尚未实现真正的任务取消功能。

当前点击"打断"按钮时会提示：
> "当前版本暂不支持打断功能，任务将在后台继续运行"

### 2.2 预留接口

前端代码中预留了调用位置：
```javascript
// TODO: 调用后端API取消任务
// await cancelAiDetectionTask(row.id)
```

### 2.3 未来实现方案

要实现完整的任务打断功能，需要：

1. **后端实现**：
   - 在 AI 服务中添加任务状态检查机制
   - 实现中断信号处理
   - 添加取消任务的 API 端点

2. **前端实现**：
   - 创建 `cancelAiDetectionTask` API 函数
   - 实现实时任务状态轮询

3. **技术挑战**：
   - AI 调用是同步的，需要在每次调用前检查取消标志
   - 需要在线程间共享取消状态
   - 需要考虑资源清理和数据一致性

## 三、注意事项

1. **兼容性**：enable_thinking 参数仅对 DeepSeek 模型生效，其他模型会忽略此参数
2. **默认值**：新配置的 enable_thinking 默认为 false（关闭状态）
3. **性能影响**：开启思考模式会增加响应时间，但可能提高识别准确率
4. **API 支持**：确保使用的 DeepSeek API 版本支持 enable_thinking 参数

## 四、相关文件清单

### 前端文件
- `frontend/src/views/ai/AiDetection.vue` - AI智能识别页面

### 后端文件
- `backend/app/models/ai.py` - 数据库模型
- `backend/app/services/ai_service.py` - AI服务核心逻辑
- `backend/add_enable_thinking_field.py` - 数据库迁移脚本（新建）

## 五、测试建议

1. 测试 DeepSeek 模型的思考模式开关是否正常显示
2. 验证开启/关闭思考模式后 API 请求参数的变化
3. 确认其他模型不受 enable_thinking 参数影响
4. 测试数据库迁移脚本的正确性
