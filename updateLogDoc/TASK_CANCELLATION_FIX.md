# 任务取消功能优化说明

## 问题描述

用户反馈：点击"打断"按钮后，等待一分钟任务仍然显示"处理中"状态。

## 原因分析

### 根本原因
之前的实现在**每行数据处理前**检查取消信号，但如果某一行的某一列正在等待AI API响应（超时时间120秒），就无法及时响应取消请求。

**执行流程：**
```
处理第N行数据
  ├─ 检查取消信号 ✓
  ├─ 处理第1列 → 调用AI API (可能等待120秒) ← 卡在这里
  ├─ 处理第2列 → 调用AI API
  └─ ...
处理第N+1行数据
  ├─ 检查取消信号 ← 要等到这里才能检测到
```

如果某次AI调用很慢，用户需要等待该次调用完成（最多120秒）才能看到取消效果。

## 解决方案

### 1. 降低AI调用超时时间
**文件**: `backend/app/services/ai_service.py`

将AI API调用的超时时间从 **120秒** 降低到 **30秒**：
```python
resp = requests.post(url, headers=headers, json=payload, timeout=30)
```

**效果**: 即使AI响应很慢，最多等待30秒就能超时并继续检查取消信号。

### 2. 增加检查频率
在**每一列**处理前都检查取消信号：

```python
for idx, row in enumerate(rows):
    # 检查点1: 每行开始前
    if task_manager.is_cancelled(task_id):
        停止任务
    
    for col in columns:
        # 检查点2: 每列处理前（新增）
        if task_manager.is_cancelled(task_id):
            停止任务
        
        # 调用AI检测
        result = self.detect_value(col, value)
```

**效果**: 检查频率从"每行一次"提升到"每列一次"，响应更快。

### 3. 紧急修复脚本
创建了 `force_cancel_task.py` 脚本，可以直接修改数据库强制取消任务。

**使用方法**:
```bash
cd backend
python force_cancel_task.py "001-不联-不联"
```

## 当前状态的优化效果

### 优化前
- ❌ 检查频率：每行一次
- ❌ AI超时：120秒
- ❌ 最坏情况：等待120秒才能响应取消

### 优化后
- ✅ 检查频率：每列一次（提升N倍，N=列数）
- ✅ AI超时：30秒（降低75%）
- ✅ 最坏情况：最多等待30秒

**示例**：
假设数据集有100行、10列：
- 优化前：最多等待120秒
- 优化后：最多等待30秒，且每处理一列就检查一次

## 立即解决当前卡住的任务

### 方法1：使用紧急修复脚本（推荐）

```bash
cd D:\user\work\2604AI比赛-code\code03\backend
python force_cancel_task.py "001-不联-不联"
```

脚本会：
1. 查找任务名称为"001-不联-不联"的任务
2. 显示当前状态
3. 强制将状态改为"cancelled"
4. 设置完成时间

### 方法2：重启后端服务

如果任务是因为后台线程卡住，重启后端服务可以释放资源：

```bash
# 停止后端服务（Ctrl+C）
# 然后重新启动
cd backend
python run.py
```

**注意**: 重启后任务状态仍然是"running"，需要配合方法1使用。

### 方法3：等待当前AI调用超时

由于已经将超时时间改为30秒，如果任务正在等待AI响应，最多再等30秒就会超时，然后检测到取消信号并停止。

## 长期优化建议

### 1. 异步中断机制（高级）
使用asyncio和aiohttp实现真正的异步中断：
```python
import asyncio
import aiohttp

async def detect_value_async(column_name, value, cancel_event):
    if cancel_event.is_set():
        return None
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=30) as resp:
                if cancel_event.is_set():
                    return None
                return await resp.json()
        except asyncio.TimeoutError:
            return None
```

### 2. 批量处理优化
将多列数据合并为一次AI调用，减少API调用次数：
```python
# 一次性检测整行数据
prompt = f"""
请检测以下整行数据的敏感信息：
{row_data}
返回JSON格式的检测结果...
"""
```

### 3. 进度持久化
定期保存进度，即使任务被取消也能保留已处理的结果。

## 相关文件

### 新增文件
- `backend/force_cancel_task.py` - 紧急修复脚本

### 修改文件
- `backend/app/services/ai_service.py`
  - 降低AI超时时间：120秒 → 30秒
  - 增加取消检查频率：每行 → 每列

## 验证步骤

1. **启动一个新任务**进行测试
2. 等待任务开始运行
3. 点击"打断"按钮
4. 观察任务是否在30秒内变为"已取消"状态
5. 查看日志确认取消过程

## 日志示例

优化后的日志输出：
```
INFO: 用户请求取消任务 | 任务ID: 123 | 任务名称: 001-不联-不联
INFO: 任务取消请求已提交 | 任务ID: 123
INFO: 任务已被用户取消 | 任务ID: 123 | 行: 45, 列: customer_name
```

可以看到具体在哪一行哪一列被取消的。
