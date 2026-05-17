# 数据库迁移指南 - 添加 report_path 字段

## ❗ 问题说明

访问脱敏任务列表时出现 500 错误，原因是数据库中缺少 `report_path` 字段。

## 🔧 解决方案

### 方案一：执行数据库迁移脚本（推荐）

1. 打开命令行/PowerShell
2. 进入 backend 目录：
   ```bash
   cd D:\user\work\2604AI比赛-code\code1\backend
   ```

3. 执行迁移脚本：
   ```bash
   python migrate_add_report_path.py
   ```

4. 预期输出：
   ```
   添加 report_path 字段到 desensitization_tasks 表...
   ✓ report_path 字段添加成功
   数据库迁移完成！
   ```

5. 重启后端服务

### 方案二：手动执行SQL

如果迁移脚本无法执行，可以手动在数据库中执行以下SQL：

```sql
ALTER TABLE desensitization_tasks 
ADD COLUMN report_path VARCHAR(500) COMMENT '报告文件路径';
```

### 方案三：代码兼容模式（已实现）

**当前已采用此方案作为临时解决方案**

代码已经修改为使用 `getattr()` 安全地访问 `report_path` 字段：
- 如果字段存在，正常读取
- 如果字段不存在，返回 None
- 不会抛出异常导致500错误

**优点：**
- ✅ 无需立即执行数据库迁移
- ✅ 系统可以正常运行
- ✅ 下载功能仍然可用（报告会实时生成）

**缺点：**
- ⚠️ 报告路径不会保存到数据库
- ⚠️ 每次下载报告都会重新生成
- ⚠️ 性能稍差

## 📝 已修改的代码

### 1. 任务列表接口 (`list_tasks`)

```python
# 安全地添加 report_path 字段（如果存在）
try:
    item["report_path"] = getattr(t, 'report_path', None)
except:
    item["report_path"] = None
```

### 2. 任务详情接口 (`get_task`)

```python
# 安全地添加 report_path 字段（如果存在）
try:
    result["report_path"] = getattr(task, 'report_path', None)
except:
    result["report_path"] = None
```

### 3. 下载报告接口 (`download_report`)

```python
# 检查是否有 report_path 字段
report_path = None
try:
    report_path = getattr(task, 'report_path', None)
except:
    report_path = None

# ... 生成报告 ...

# 尝试保存报告路径到数据库（如果字段存在）
try:
    task.report_path = html_path
    db.commit()
except:
    pass  # 如果字段不存在，忽略错误
```

### 4. 生成报告接口 (`generate_report`)

```python
# 尝试保存报告路径到数据库（如果字段存在）
try:
    task.report_path = html_path
    db.commit()
except:
    pass  # 如果字段不存在，忽略错误
```

## ✅ 验证修复

1. 重启后端服务后，访问脱敏任务列表
2. 应该不再出现 500 错误
3. 可以正常查看任务列表和详情
4. 可以下载副本和报告

## 🎯 建议操作

虽然代码已经做了兼容处理，但**强烈建议执行数据库迁移**，原因：

1. **性能优化**：报告路径保存到数据库后，无需重复生成
2. **功能完整**：充分利用所有功能特性
3. **数据持久化**：报告路径永久保存，便于后续查询

## 📊 迁移前后对比

| 项目 | 迁移前（兼容模式） | 迁移后（完整模式） |
|------|------------------|------------------|
| 任务列表访问 | ✅ 正常 | ✅ 正常 |
| 任务详情访问 | ✅ 正常 | ✅ 正常 |
| 下载副本 | ✅ 正常 | ✅ 正常 |
| 下载报告 | ✅ 正常（每次重新生成） | ✅ 正常（缓存复用） |
| 报告路径保存 | ❌ 不保存 | ✅ 保存到数据库 |
| 性能 | 一般 | 更优 |

## 🚀 快速执行步骤

```bash
# 1. 进入backend目录
cd D:\user\work\2604AI比赛-code\code1\backend

# 2. 执行迁移
python migrate_add_report_path.py

# 3. 重启服务
python run.py
```

---

**更新日期：** 2026-05-16  
**状态：** ✅ 已修复（兼容模式）  
**建议：** 执行数据库迁移以获得最佳性能
