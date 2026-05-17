# 错误修复部署指南

## 📋 问题总结

### 问题1：脱敏规则管理500错误
**错误信息**：
```
Unknown column 'desensitization_rules.desensitization_method' in 'field list'
```

**原因**：数据库表中缺少 `desensitization_method` 字段

**影响**：点击"脱敏规则管理"页面时报500错误

---

### 问题2：数据源配置Timestamp序列化错误
**错误信息**：
```
Object of type Timestamp is not JSON serializable
```

**原因**：从MySQL读取的数据包含pandas Timestamp类型，无法直接序列化为JSON保存到数据库

**影响**：新增数据源配置并导入表时报错

---

## 🔧 修复方案

### 修复1：添加数据库字段

**文件**：`backend/migrate_add_desensitization_method.py`

该脚本会：
1. 检查 `desensitization_method` 字段是否存在
2. 如果不存在，添加该字段到 `desensitization_rules` 表
3. 更新现有内置规则的 `desensitization_method` 值

### 修复2：转换Timestamp类型

**文件**：`backend/app/api/datasource.py`

添加了 `convert_timestamp_to_string()` 函数：
- 递归转换字典、列表中的Timestamp对象
- 将 `pd.Timestamp` 和 `datetime` 转换为ISO格式字符串
- 在保存数据集时自动调用该函数

---

## 🚀 部署步骤

### 步骤1：停止后端服务

如果后端服务正在运行，请先停止（Ctrl+C）

### 步骤2：运行数据库迁移脚本

```bash
cd D:\user\work\2604AI比赛-code\code1\backend

# 运行迁移脚本，添加 desensitization_method 字段
python migrate_add_desensitization_method.py
```

**预期输出**：
```
开始数据库迁移...
正在添加 desensitization_method 字段...
✅ desensitization_method 字段添加成功！
正在更新现有规则的 desensitization_method 字段...
✅ 已更新 21 个规则的 desensitization_method 字段

🎉 数据库迁移完成！

请运行以下命令更新规则数据：
python update_desensitization_rules.py
```

### 步骤3：更新规则数据

```bash
# 运行规则更新脚本，添加新的多语言规则
python update_desensitization_rules.py
```

**预期输出**：
```
开始更新 32 个内置规则...
  ✓ 更新规则: 完全遮盖 (ID: 1)
  ✓ 更新规则: 姓名仿真 (ID: 2)
  ...
  + 创建规则: 姓名仿真-韩语 (ID: 22)
  ...

✅ 规则更新完成！
   - 新建: 11 个
   - 更新: 21 个
   - 总计: 32 个
```

### 步骤4：重启后端服务

```bash
# 启动后端服务
python run.py
```

### 步骤5：刷新前端页面

在浏览器中按 `Ctrl + F5` 强制刷新，清除缓存。

---

## ✅ 验证清单

部署完成后，请验证以下内容：

### 验证1：脱敏规则管理
- [ ] 访问"脱敏规则管理"页面
- [ ] 页面正常加载，无500错误
- [ ] 能看到所有32个内置规则
- [ ] "脱敏方式"列正确显示（完全遮盖/仿真造数/部分遮盖）
- [ ] 点击"查看详情"能正常显示规则信息

### 验证2：数据源配置
- [ ] 访问"数据源配置"页面
- [ ] 点击"新增数据源"
- [ ] 填写数据库连接信息（localhost:3308, root/msps）
- [ ] 点击"测试连接"，显示连接成功
- [ ] 选择要导入的表
- [ ] 点击"保存并导入"
- [ ] 导入成功，无Timestamp序列化错误
- [ ] 能在"数据集管理"看到导入的数据集

### 验证3：创建脱敏任务
- [ ] 访问"脱敏任务" → "创建任务"
- [ ] 选择一个数据集
- [ ] 能看到"脱敏方式"下拉框
- [ ] 选择脱敏方式后，规则下拉框可用
- [ ] 规则列表正确筛选
- [ ] 能正常预览和提交任务

---

## 🔍 故障排查

### 问题：迁移脚本报错

**可能原因**：
1. 数据库连接失败
2. 权限不足

**解决方法**：
```bash
# 检查数据库连接
mysql -h localhost -P 3308 -u root -pmsps

# 手动添加字段
USE desensitization;
ALTER TABLE desensitization_rules ADD COLUMN desensitization_method VARCHAR(50) NULL AFTER category;
```

### 问题：仍然报500错误

**可能原因**：
1. 后端服务未重启
2. 浏览器缓存未清除

**解决方法**：
1. 确认后端服务已重启
2. 清除浏览器缓存（Ctrl + Shift + Delete）
3. 强制刷新页面（Ctrl + F5）

### 问题：Timestamp错误仍然存在

**可能原因**：
1. 代码未重新加载
2. 还有其他地方使用了preview_data

**解决方法**：
1. 重启后端服务
2. 检查日志文件确认错误位置
3. 查看 `backend/logs/error_2026-05-16.log`

---

## 📊 相关文件清单

### 新增文件
1. `backend/migrate_add_desensitization_method.py` - 数据库迁移脚本
2. `backend/update_desensitization_rules.py` - 规则更新脚本
3. `backend/RULES_UPDATE_GUIDE.md` - 规则更新说明
4. `frontend/DESSENSITIZATION_TASK_LAYERED_SELECTION.md` - 分层选择功能说明

### 修改文件
1. `backend/app/models/desensitization.py` - 添加 desensitization_method 字段
2. `backend/app/services/desensitization_engine.py` - 添加多语言规则
3. `backend/app/api/datasource.py` - 添加Timestamp转换函数
4. `frontend/src/views/desensitization/RuleManage.vue` - 优化详情对话框
5. `frontend/src/views/desensitization/CreateTask.vue` - 实现分层选择
6. `frontend/src/views/detection/RuleManage.vue` - 添加查看详情功能
7. `frontend/src/views/detection/TaskDetail.vue` - 添加手动刷新按钮

---

## 📝 注意事项

1. **备份数据库**：在执行迁移脚本前，建议先备份数据库
   ```bash
   mysqldump -h localhost -P 3308 -u root -pmsps desensitization > backup_$(date +%Y%m%d).sql
   ```

2. **执行顺序**：必须先运行迁移脚本，再运行规则更新脚本

3. **不要跳过步骤**：每个步骤都很重要，跳过可能导致问题

4. **检查日志**：如果遇到问题，查看日志文件定位问题
   - API日志：`backend/logs/api_2026-05-16.log`
   - 错误日志：`backend/logs/error_2026-05-16.log`
   - 应用日志：`backend/logs/app_2026-05-16.log`

---

## 🎉 完成标志

当以下所有条件满足时，表示修复完成：

- ✅ 脱敏规则管理页面正常访问
- ✅ 数据源配置能正常导入表
- ✅ 创建脱敏任务支持分层选择
- ✅ 所有新功能正常工作
- ✅ 无500错误和序列化错误

---

**更新时间**: 2026-05-16  
**版本**: v2.2  
**修复人员**: AI Assistant
