# 报告PDF导出功能

## 📋 功能概述

为脱敏任务报告添加了**PDF格式导出**功能，用户可以选择下载HTML或PDF格式的报告。

## ✨ 新增功能

### 1. PDF报告生成

**技术实现：**
- 使用 `weasyprint` 库将HTML转换为PDF
- 保持与HTML报告相同的样式和布局
- 自动生成HTML和PDF两种格式

### 2. 格式选择下拉菜单

**位置：**
- 任务列表页面 - "下载报告"按钮改为下拉菜单
- 任务详情页面 - "下载报告"按钮改为下拉菜单

**选项：**
- HTML格式（默认）
- PDF格式

## 🔧 技术实现

### 后端实现

#### 1. 安装依赖

**文件：** `backend/requirements.txt`

```txt
weasyprint==60.2
```

安装命令：
```bash
pip install weasyprint
```

**注意：** weasyprint 可能需要系统安装一些依赖库：
- Windows: 通常无需额外安装
- Linux: 需要安装 Pango, Cairo等
- macOS: 需要安装 Pango, GDK-PixBuf等

#### 2. 报告生成器增强

**文件：** `backend/app/services/report_generator.py`

添加 `export_pdf()` 方法：

```python
def export_pdf(self, report: ValidationReport, output_path: str):
    """导出PDF格式报告"""
    try:
        from weasyprint import HTML
        html_content = self._render_html(report)
        # 生成PDF
        html_doc = HTML(string=html_content, base_url=".")
        html_doc.write_pdf(output_path)
        return output_path
    except ImportError:
        raise ImportError("请安装 weasyprint: pip install weasyprint")
    except Exception as e:
        raise Exception(f"PDF生成失败: {str(e)}")
```

#### 3. API接口更新

**文件：** `backend/app/api/desensitization.py`

**下载报告接口：**
```
GET /api/desensitization/tasks/{task_id}/download-report?format=html|pdf
```

**参数：**
- `format`: 报告格式，可选值：
  - `html`（默认）- HTML格式
  - `pdf` - PDF格式

**功能：**
- 首次生成时同时创建HTML和PDF文件
- 根据 `format` 参数返回对应格式的文件
- 如果PDF生成失败，仍然提供HTML格式

### 前端实现

#### 1. API封装

**文件：** `frontend/src/api/desensitization.js`

```javascript
export function downloadReport(id, format = 'html') {
  return request.get(`/api/desensitization/tasks/${id}/download-report`, {
    params: { format },
    responseType: 'blob'
  })
}
```

#### 2. 任务列表页面

**文件：** `frontend/src/views/desensitization/TaskList.vue`

使用 `el-dropdown` 组件提供格式选择：

```vue
<el-dropdown @command="(cmd) => downloadReportWithFormat(row, cmd)">
  <el-button type="warning" size="small">
    下载报告<el-icon class="el-icon--right"><arrow-down /></el-icon>
  </el-button>
  <template #dropdown>
    <el-dropdown-menu>
      <el-dropdown-item command="html">HTML格式</el-dropdown-item>
      <el-dropdown-item command="pdf">PDF格式</el-dropdown-item>
    </el-dropdown-menu>
  </template>
</el-dropdown>
```

#### 3. 任务详情页面

**文件：** `frontend/src/views/desensitization/TaskDetail.vue`

同样的下拉菜单设计：

```vue
<el-dropdown @command="downloadReportWithFormat">
  <el-button type="warning">
    下载报告<el-icon class="el-icon--right"><arrow-down /></el-icon>
  </el-button>
  <template #dropdown>
    <el-dropdown-menu>
      <el-dropdown-item command="html">HTML格式</el-dropdown-item>
      <el-dropdown-item command="pdf">PDF格式</el-dropdown-item>
    </el-dropdown-menu>
  </template>
</el-dropdown>
```

## 📊 界面效果

### 任务列表页面

```
┌──────────────────────────────────────────────────────────────┐
│ 操作                                                         │
├──────────────────────────────────────────────────────────────┤
│ [详情] [下载副本] [下载报告 ▼]                               │
│                              ├─ HTML格式                     │
│                              └─ PDF格式                      │
└──────────────────────────────────────────────────────────────┘
```

### 任务详情页面

```
┌────────────────────────────────────────────────────────────┐
│ [🔄 刷新] [✅ 停止自动刷新] [⬇️ 下载副本] [📄 下载报告 ▼]   │
│                                                    ├─ HTML格式│
│                                                    └─ PDF格式 │
└────────────────────────────────────────────────────────────┘
```

## 🚀 部署步骤

### 1. 安装Python依赖

```bash
cd D:\user\work\2604AI比赛-code\code1\backend
pip install weasyprint==60.2
```

### 2. 重启后端服务

```bash
python run.py
```

### 3. 刷新前端页面

前端代码已更新，刷新浏览器即可看到新功能。

## 💡 使用示例

### 场景1：下载HTML报告

1. 进入脱敏任务列表或详情页
2. 点击"下载报告"下拉菜单
3. 选择"HTML格式"
4. 浏览器下载 `.html` 文件

### 场景2：下载PDF报告

1. 进入脱敏任务列表或详情页
2. 点击"下载报告"下拉菜单
3. 选择"PDF格式"
4. 浏览器下载 `.pdf` 文件

### 场景3：首次生成报告

1. 点击下载任一格式的报告
2. 系统自动生成HTML和PDF两种格式
3. 返回请求的格式文件
4. 后续下载可直接使用已生成的文件

## 📝 文件修改清单

### 后端文件

1. ✅ `backend/requirements.txt` - 添加 weasyprint 依赖
2. ✅ `backend/app/services/report_generator.py` - 添加 export_pdf() 方法
3. ✅ `backend/app/api/desensitization.py` - 更新下载接口支持格式参数

### 前端文件

1. ✅ `frontend/src/api/desensitization.js` - 更新 downloadReport() 支持格式参数
2. ✅ `frontend/src/views/desensitization/TaskList.vue` - 添加格式选择下拉菜单
3. ✅ `frontend/src/views/desensitization/TaskDetail.vue` - 添加格式选择下拉菜单

## 🎯 功能特点

### 1. 智能生成

- **一次性生成**：首次下载时同时生成HTML和PDF
- **缓存复用**：后续下载直接使用已生成的文件
- **容错处理**：PDF生成失败时仍提供HTML格式

### 2. 用户体验

- **格式选择**：清晰的下拉菜单，一目了然
- **统一入口**：HTML和PDF从同一按钮访问
- **明确提示**：下载成功时显示具体格式

### 3. 文件格式

**HTML报告：**
- 文件名：`report_{id}_{timestamp}.html`
- MIME类型：`text/html`
- 特点：可交互、可搜索、体积小

**PDF报告：**
- 文件名：`report_{id}_{timestamp}.pdf`
- MIME类型：`application/pdf`
- 特点：固定布局、易打印、专业外观

## ⚠️ 注意事项

1. **首次生成可能较慢**
   - PDF生成需要额外时间（通常1-3秒）
   - 请耐心等待

2. **PDF样式可能略有差异**
   - 由于PDF渲染引擎的限制
   - 某些CSS效果可能不完全一致

3. **文件大小**
   - PDF文件通常比HTML大2-5倍
   - 包含完整的字体和样式信息

4. **依赖安装**
   - 确保已安装 weasyprint
   - 某些系统可能需要额外的系统库

## 🔮 后续优化方向

1. **异步生成**
   - 后台异步生成PDF
   - 避免阻塞用户请求

2. **格式预览**
   - 在页面内直接预览报告
   - 无需下载即可查看

3. **批量导出**
   - 支持同时导出多个任务的报告
   - 打包为ZIP文件

4. **自定义模板**
   - 允许用户自定义报告样式
   - 选择不同的PDF主题

5. **水印功能**
   - 添加公司Logo水印
   - 防止报告被滥用

---

**版本：** v1.0  
**更新日期：** 2026-05-16  
**作者：** AI Assistant
