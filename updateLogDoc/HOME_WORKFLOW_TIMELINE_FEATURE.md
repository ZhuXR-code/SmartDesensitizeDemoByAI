# 首页操作流程时间轴功能

## 📋 功能概述

在平台首页添加了**可视化操作流程指引**，采用时间轴样式展示从数据导入到报告生成的完整操作路径，并提供一键跳转功能。

## ✨ 功能特性

### 1. 时间轴布局
- **水平时间轴**：5个步骤横向排列，清晰展示操作流程
- **连接线设计**：步骤之间用箭头连接线串联，体现流程关系
- **渐变色彩**：每个步骤使用不同的渐变色，视觉层次分明

### 2. 交互体验
- **点击跳转**：点击任意步骤可直接跳转到对应页面
- **悬停效果**：
  - 步骤卡片上浮（`translateY(-3px)`）
  - 数字圆圈放大（`scale(1.1)`）
  - 标题颜色变蓝
  - 阴影加深

### 3. 响应式设计
- **大屏（>1200px）**：5个步骤横向排列，显示连接线
- **中屏（768-1200px）**：每行2个步骤，隐藏连接线
- **小屏（<768px）**：单列垂直排列

## 🎯 操作流程步骤

| 步骤 | 标题 | 描述 | 标签 | 跳转路径 |
|------|------|------|------|----------|
| 1️⃣ | 导入数据 | 上传Excel/CSV文件或从数据库导入 | 支持多种格式 | `/datasets/upload` |
| 2️⃣ | 识别敏感数据 | 智能扫描并发现敏感信息 | 多语言支持 | `/detection/tasks/create` |
| 3️⃣ | 配置脱敏规则 | 选择或自定义脱敏方式 | 智能推荐 | `/desensitization/rules` |
| 4️⃣ | 执行脱敏处理 | 预览确认后批量脱敏 | 可视化对比 | `/desensitization/tasks/create` |
| 5️⃣ | 查看报告 | 生成HTML或Markdown格式报告 | 多格式导出 | `/report/platform` |

## 🎨 视觉设计

### 配色方案

```javascript
// 每个步骤的渐变色
const colors = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',  // 紫色 - 导入
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',  // 粉红 - 识别
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',  // 蓝色 - 配置
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',  // 橙黄 - 执行
  'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'   // 绿色 - 报告
]
```

### 组件结构

```
┌─────────────────────────────────────────────────────┐
│ 🚀 平台操作流程                    [快速开始]        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  (1) ───→ (2) ───→ (3) ───→ (4) ───→ (5)          │
│   │         │         │         │         │         │
│ 导入     识别      配置      执行      查看          │
│ 数据     敏感      脱敏      脱敏      报告          │
│          数据      规则      处理                    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 🔧 技术实现

### 1. 数据结构

**文件**: `frontend/src/views/Dashboard.vue`

```javascript
const workflowSteps = [
  {
    title: '导入数据',
    description: '上传Excel/CSV文件或从数据库导入',
    tagText: '支持多种格式',
    tagType: 'primary',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    route: '/datasets/upload'
  },
  // ... 其他步骤
]
```

### 2. 模板结构

```vue
<div class="workflow-timeline">
  <div 
    v-for="(step, index) in workflowSteps" 
    :key="index"
    class="workflow-step"
    @click="handleWorkflowClick(step)"
  >
    <!-- 连接线 -->
    <div v-if="index < workflowSteps.length - 1" class="step-connector">
      <div class="connector-line"></div>
      <div class="connector-arrow">→</div>
    </div>
    
    <!-- 步骤内容 -->
    <div class="step-content">
      <div class="step-number" :style="{ background: step.color }">
        {{ index + 1 }}
      </div>
      <div class="step-info">
        <div class="step-title">{{ step.title }}</div>
        <div class="step-desc">{{ step.description }}</div>
        <el-tag size="small" :type="step.tagType" effect="plain">
          {{ step.tagText }}
        </el-tag>
      </div>
    </div>
  </div>
</div>
```

### 3. 跳转逻辑

```javascript
import { useRouter } from 'vue-router'

const router = useRouter()

const handleWorkflowClick = (step) => {
  if (step.route) {
    router.push(step.route)
  }
}
```

### 4. CSS样式关键点

**时间轴容器**：
```css
.workflow-timeline {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  padding: 20px 10px;
  position: relative;
}
```

**连接线**：
```css
.step-connector {
  position: absolute;
  top: 25px;
  left: 50%;
  right: -50%;
  height: 2px;
  z-index: 1;
  pointer-events: none;
}

.connector-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(to right, #dcdfe6 0%, #dcdfe6 100%);
  transform: translateY(-50%);
}
```

**悬停动画**：
```css
.workflow-step:hover {
  transform: translateY(-3px);
}

.workflow-step:hover .step-number {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}

.workflow-step:hover .step-title {
  color: #409EFF;
}
```

## 📱 响应式适配

### 大屏（>1200px）
```
┌───────┐ → ┌───────┐ → ┌───────┐ → ┌───────┐ → ┌───────┐
│ Step1 │   │ Step2 │   │ Step3 │   │ Step4 │   │ Step5 │
└───────┘   └───────┘   └───────┘   └───────┘   └───────┘
```

### 中屏（768-1200px）
```
┌───────┐   ┌───────┐
│ Step1 │   │ Step2 │
└───────┘   └───────┘

┌───────┐   ┌───────┐
│ Step3 │   │ Step4 │
└───────┘   └───────┘

┌───────┐
│ Step5 │
└───────┘
```

### 小屏（<768px）
```
┌───────┐
│ Step1 │
└───────┘
┌───────┐
│ Step2 │
└───────┘
┌───────┐
│ Step3 │
└───────┘
┌───────┐
│ Step4 │
└───────┘
┌───────┐
│ Step5 │
└───────┘
```

## 🎯 用户价值

### 1. 新手引导
- **清晰路径**：新用户一目了然了解平台使用流程
- **降低门槛**：减少学习成本，快速上手
- **减少困惑**：明确下一步该做什么

### 2. 效率提升
- **快速跳转**：点击即可到达目标页面，无需查找菜单
- **流程优化**：按步骤操作，避免遗漏关键环节
- **减少错误**：引导正确操作顺序

### 3. 视觉吸引
- **美观设计**：渐变色+时间轴，视觉效果出色
- **交互反馈**：悬停动画增强用户体验
- **专业形象**：提升平台整体质感

## 🧪 测试场景

### 功能测试
1. ✅ 点击每个步骤能正确跳转到对应页面
2. ✅ 悬停时显示动画效果（上浮、放大、变色）
3. ✅ 不同屏幕尺寸下布局正确
4. ✅ 连接线在大屏正常显示，中小屏隐藏

### 兼容性测试
1. ✅ Chrome浏览器
2. ✅ Firefox浏览器
3. ✅ Safari浏览器
4. ✅ Edge浏览器
5. ✅ 移动端浏览器

### 性能测试
1. ✅ 页面加载速度无明显影响
2. ✅ 动画流畅无卡顿
3. ✅ 内存占用合理

## 📝 维护建议

### 修改步骤
如需修改操作步骤，编辑 `workflowSteps` 数组：

```javascript
const workflowSteps = [
  {
    title: '新步骤名称',
    description: '步骤描述',
    tagText: '标签文本',
    tagType: 'primary|success|warning|danger|info',
    color: '渐变色CSS',
    route: '/跳转路径'
  }
]
```

### 添加步骤
直接在数组中添加新对象即可，系统会自动调整布局。

### 删除步骤
从数组中移除对应对象，注意保持流程的连贯性。

## 🔗 相关文件

- **前端页面**: `frontend/src/views/Dashboard.vue`
- **路由配置**: `frontend/src/router/index.js`
- **图标库**: Element Plus Icons

## 📅 更新日志

**版本**: v1.0  
**日期**: 2026-05-17  
**作者**: AI Assistant

### 新增功能
- ✅ 首页操作流程时间轴
- ✅ 5个标准操作步骤
- ✅ 点击跳转功能
- ✅ 悬停动画效果
- ✅ 响应式布局
- ✅ 连接线设计

### 技术亮点
- Flexbox弹性布局
- CSS渐变色彩
- Vue Router集成
- 媒体查询适配
- 平滑过渡动画

---

**相关文档**：
- [用户使用手册](../docs/USER_MANUAL.md)
- [平台运营成效报告](../frontend/src/views/report/PlatformReport.vue)
