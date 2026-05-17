# 问题修复指南

## 🔧 问题1：自动刷新时脱敏结果示例没有及时刷新

### 问题描述
在脱敏任务详情页点击"自动刷新"后，虽然任务状态和进度会更新，但"脱敏结果示例"表格不会实时刷新显示新的脱敏结果。

### 原因分析
原代码只在任务状态变为"completed"时才重新加载结果列表，忽略了任务进行中（processing状态）时脱敏结果也在不断增加的情况。

### 修复方案
✅ **已修复** - 修改了 `frontend/src/views/desensitization/TaskDetail.vue` 中的 `startAutoRefresh()` 函数

**修复逻辑：**
```javascript
// 检查任务状态、进度或处理行数是否变化
const statusChanged = newTask.status !== task.value.status
const progressChanged = newTask.progress !== task.value.progress
const processedRowsChanged = newTask.processed_rows !== task.value.processed_rows

// 如果任何一项发生变化，重新加载结果
if (statusChanged || progressChanged || processedRowsChanged) {
  await loadResults()
}
```

**效果：**
- ✅ 任务进行中：每3秒自动刷新脱敏结果列表
- ✅ 任务完成时：显示"任务已完成！"提示
- ✅ 避免无效刷新：只有数据变化时才重新加载

---

## 🔧 问题2：下载PDF报告404错误

### 错误信息
```
GET http://localhost:8080/api/desensitization/tasks/5/download-report?format=pdf 404 (Not Found)
```

### 原因分析
1. **后端服务未重启** - 新添加的 `format` 参数还没有生效
2. **weasyprint库未安装** - PDF生成功能依赖此库

### 解决步骤

#### 步骤1：安装weasyprint依赖

```bash
cd D:\user\work\2604AI比赛-code\code1\backend
pip install weasyprint==60.2
```

**Windows用户注意：**
- weasyprint 在Windows上通常可以直接安装
- 如果遇到依赖问题，可能需要安装 GTK+ 运行时
- 下载地址：https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

#### 步骤2：重启后端服务

**停止当前运行的后端服务**（Ctrl+C）

**重新启动：**
```bash
cd D:\user\work\2604AI比赛-code\code1\backend
python run.py
```

**确认启动成功：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 步骤3：刷新前端页面

在浏览器中按 **Ctrl+F5** 强制刷新前端页面，清除缓存。

#### 步骤4：测试PDF下载

1. 进入脱敏任务列表或详情页
2. 点击"下载报告"下拉菜单
3. 选择"PDF格式"
4. 应该能成功下载PDF文件

---

## 📋 验证清单

### 验证问题1修复
- [ ] 创建一个脱敏任务
- [ ] 进入任务详情页
- [ ] 点击"开启自动刷新"按钮
- [ ] 观察"脱敏结果示例"表格是否每3秒自动更新
- [ ] 确认任务进行中能看到新增的脱敏结果

### 验证问题2修复
- [ ] 确认weasyprint已安装：`pip show weasyprint`
- [ ] 确认后端服务已重启
- [ ] 点击下载报告 → PDF格式
- [ ] 确认能成功下载PDF文件
- [ ] 用PDF阅读器打开文件，检查内容是否正确

---

## ⚠️ 常见问题

### Q1: 安装weasyprint时报错
**错误信息：**
```
ERROR: Could not find a version that satisfies the requirement weasyprint
```

**解决方案：**
```bash
# 升级pip
python -m pip install --upgrade pip

# 然后重新安装
pip install weasyprint==60.2
```

### Q2: Windows上weasyprint无法正常工作
**症状：** PDF生成失败，报错缺少GTK+

**解决方案：**
1. 下载GTK+运行时：https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. 安装最新版本的 `gtk3-runtime-xxx-win64.exe`
3. 重启电脑
4. 重新测试PDF下载

### Q3: 后端重启后仍然404
**可能原因：**
- 端口被占用，实际启动在不同端口
- 代码有语法错误，服务启动失败

**检查方法：**
```bash
# 查看后端控制台输出，确认启动成功
# 检查是否有错误信息

# 测试API是否可访问
curl http://localhost:8000/api/desensitization/tasks/5/download-report?format=html
```

### Q4: 自动刷新太频繁，影响性能
**调整刷新间隔：**

修改 `frontend/src/views/desensitization/TaskDetail.vue` 第184行：
```javascript
}, 3000)  // 改为 5000（5秒）或 10000（10秒）
```

---

## 🎯 快速修复命令

一键执行所有修复步骤：

```bash
# 1. 进入后端目录
cd D:\user\work\2604AI比赛-code\code1\backend

# 2. 安装weasyprint
pip install weasyprint==60.2

# 3. 重启后端服务（先Ctrl+C停止当前服务，然后执行）
python run.py
```

然后在浏览器中按 **Ctrl+F5** 刷新前端页面。

---

## 📊 修复后的预期效果

### 自动刷新功能
```
时间线：
0s  - 开启自动刷新
3s  - 刷新任务状态 + 加载脱敏结果（看到前100条）
6s  - 刷新任务状态 + 加载脱敏结果（看到前300条）
9s  - 刷新任务状态 + 加载脱敏结果（看到前600条）
... - 持续更新直到任务完成
完成 - 显示"任务已完成！"提示
```

### PDF下载功能
```
操作流程：
1. 点击"下载报告"下拉菜单
2. 选择"PDF格式"
3. 后端生成HTML和PDF文件（首次约2-5秒）
4. 浏览器下载 report_xxx_xxx.pdf 文件
5. 用Adobe Reader或其他PDF阅读器打开
6. 看到完整的脱敏报告，包含所有指标
```

---

**版本：** v1.0  
**更新日期：** 2026-05-16  
**适用问题：** 自动刷新不更新结果、PDF下载404错误
