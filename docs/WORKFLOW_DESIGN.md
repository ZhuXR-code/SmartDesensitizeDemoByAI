# 工作流重构设计方案

> **版本：** v1.0
> **目标：** 将平台从"功能模块导航"重构为"任务驱动的工作流"

---

## 一、问题诊断

### 1.1 当前架构的核心问题

```
当前导航结构（按技术模块组织）：
┌─────────────────────────────────────┐
│  首页                               │
│  数据集管理                         │
│    ├── 数据集列表                   │
│    ├── 导入数据                     │
│    └── 数据源配置                   │
│  敏感数据识别                       │
│    ├── 识别规则管理                 │
│    ├── 规则集管理                   │
│    ├── 识别任务                     │
│    └── 识别结果                     │
│  数据脱敏                           │
│    ├── 脱敏规则管理                 │
│    ├── 脱敏任务                     │
│    └── ...                          │
│  AI智能                             │
│  运营报表                           │
│  帮助中心                           │
└─────────────────────────────────────┘
```

| 问题 | 表现 | 影响 |
|------|------|------|
| **技术视角而非用户视角** | 菜单按"数据集/识别/脱敏/AI"组织 | 用户需要先理解平台技术架构才能操作 |
| **流程断裂** | 识别→脱敏需要手动跳转页面 | 核心链路有断点，用户易迷失 |
| **信息孤岛** | 每个模块各自为政 | 无法在一个页面看到完整项目状态 |
| **重复导航** | 规则管理散落在多个子菜单中 | 用户需要反复切换页面 |
| **配置与执行混合** | 规则管理、密钥管理、任务创建混在一起 | 新手用户感到困惑 |

### 1.2 已有探索的局限性

平台已经在首页添加了"操作流程时间轴"和"步骤条"组件，但这些只是**首页上的视觉引导**，本质仍然是5个独立的链接按钮，没有真正将工作流集成到操作体验中。

---

## 二、设计方案：三维度工作流模型

### 2.1 核心设计理念

```
  用户角色维度         操作流程维度           功能深度维度
  ┌───────────┐      ┌──────────────┐      ┌──────────────┐
  │ 新手用户   │ ──→  │  快速工作流    │ ──→  │ 一步直达结果  │
  │ 普通用户   │ ──→  │  项目工作流    │ ──→  │ 全流程可控   │
  │ 技术专家   │ ──→  │  配置工作流    │ ──→  │ 精细化调控   │
  └───────────┘      └──────────────┘      └──────────────┘
```

**核心理念**：同一套底层功能，通过三个不同深度的工作流入口呈现，满足不同用户场景。

---

### 2.2 方案一：快速工作流（Express Workflow）

**适用场景**：用户想快速做一次"导入→识别→脱敏→报告"的完整流程

**交互形式**：首页大卡片 + 右侧悬浮引导

**设计细节**：

```
┌────────────────────────────────────────────────────────────────────┐
│ 📋 快速脱敏任务                                                    │
│                                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Step 1   │→│ Step 2   │→│ Step 3   │→│ Step 4   │          │
│  │ 📤       │  │ 🔍       │  │ 🔒       │  │ 📊       │          │
│  │ 选择数据  │  │ 扫描敏感  │  │ 脱敏配置  │  │ 完成&报告 │          │
│  │ [文件/DB]│  │ [规则/AI] │  │ [策略]   │  │ [下载]   │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │              │              │              │               │
│       ▼              ▼              ▼              ▼               │
│  ┌─────────────┐ ┌──────────┐ ┌────────────┐ ┌──────────────┐    │
│  │ 上传/选择    │ │ 选择识别  │ │ 配置脱敏    │ │ 查看结果     │    │
│  │ 数据集      │ │ 方式并执行 │ │ 规则       │ │ 下载文件     │    │
│  │ 自动开始识别 │ │ 自动预览  │ │ 一键执行   │ │ 生成报告     │    │
│  └─────────────┘ └──────────┘ └────────────┘ └──────────────┘    │
│                                                                    │
│  当前步骤: [=====░░░░░░░░░░░] 2/4                                   │
│                                                                    │
│  [上一步]                          [下一步 →]                       │
└────────────────────────────────────────────────────────────────────┘
```

**技术实现要点**：
- 新建 `WorkflowExpress.vue` 组件，内含4个步骤的 `el-steps` 组件
- 每个步骤内嵌现有子组件或新建轻量版组件
- 使用 Pinia store 管理跨步骤状态（数据集ID、识别结果ID、配置选择）
- 完成后自动跳转到报告页

**路由设计**：
```
/workflow/express          → 快速工作流首页（步骤1）
/workflow/express/step-2   → 步骤2：识别配置
/workflow/express/step-3   → 步骤3：脱敏配置
/workflow/express/step-4   → 步骤4：完成
```

---

### 2.3 方案二：项目工作流（Project Workflow）⭐ 推荐

**适用场景**：需要管理多个数据集的复杂脱敏任务、跨表关联、多人协作

**核心概念**：引入**"项目（Project）"**作为一级业务实体，将数据集、识别任务、脱敏任务、报告全部关联到一个项目下。

#### 2.3.1 项目生命周期

```
                      ┌──────────────┐
                      │  创建项目      │
                      │  填写名称/描述 │
                      └──────┬───────┘
                             │
                             ▼
                      ┌──────────────┐
                      │  导入数据集    │ ← 可导入多个
                      │  文件/DB/粘贴  │
                      └──────┬───────┘
                             │
                             ▼
               ┌─────────────────────────┐
               │    识别敏感数据           │
               │  ┌───────────────────┐   │
               │  │ 规则引擎识别  │ AI识别│  │ ← 可并行
               │  └───────────────────┘   │
               └──────────┬──────────────┘
                          │
                          ▼
               ┌─────────────────────────┐
               │    复核确认               │
               │  ┌───────────────────┐   │
               │  │ 字段级复核 │ 批量确认│  │
               │  └───────────────────┘   │
               └──────────┬──────────────┘
                          │
                          ▼
               ┌─────────────────────────┐
               │    配置脱敏策略           │
               │  ┌───────────────────┐   │
               │  │ 逐字段配置 │ 智能推荐│  │
               │  └───────────────────┘   │
               └──────────┬──────────────┘
                          │
                          ▼
               ┌─────────────────────────┐
               │    执行脱敏               │
               │  ┌───────────────────┐   │
               │  │ 预览确认→批量执行   │   │
               │  └───────────────────┘   │
               └──────────┬──────────────┘
                          │
                          ▼
               ┌─────────────────────────┐
               │    完成 & 报告            │
               │  ┌───────────────────┐   │
               │  │ 下载文件 │ 查看报告  │   │
               │  └───────────────────┘   │
               └─────────────────────────┘
```

#### 2.3.2 页面设计

##### 页面1：工作台（Workbench）— 替换现有首页 Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔒 敏感信息智能识别与脱敏平台                     [主题切换] [帮助] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  🚀 快速开始                                                  │   │
│  │  ┌──────────────────┐  ┌──────────────────┐                   │   │
│  │  │  📋 新建快速任务    │  │  📁 新建项目      │                   │   │
│  │  │  单次导入→脱敏     │  │  多数据集复杂流程  │                   │   │
│  │  │  [一键直达]       │  │  [全流程管理]    │                   │   │
│  │  └──────────────────┘  └──────────────────┘                   │   │
│  │  ┌──────────────────┐  ┌──────────────────┐                   │   │
│  │  │  📤 导入数据       │  │  ⚙️ 配置管理      │                   │   │
│  │  │  直接上传文件      │  │  规则/密钥/AI设置  │                   │   │
│  │  └──────────────────┘  └──────────────────┘                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  📋 我的项目                    [+ 新建项目]  [查看全部 →]    │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │  项目名称        │ 数据集 │ 状态     │ 进度 │ 更新时间  │  │   │
│  │  ├────────────────────────────────────────────────────────┤  │   │
│  │  │  客户数据脱敏-Q2  │ 3个   │ ⚡进行中  │ 60%  │ 2026-05-19│  │   │
│  │  │  财务报表脱敏     │ 1个   │ 📋待开始  │ 0%   │ 2026-05-18│  │   │
│  │  │  测试数据生成     │ 5个   │ ✅已完成  │ 100% │ 2026-05-15│  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  📊 平台概览                                                   │   │
│  │  总数据集: 28  识别任务: 156  脱敏任务: 89  发现敏感: 12,345  │   │
│  │  [查看完整报表 →]                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

##### 页面2：项目详情（Project Detail）— 项目的全生命周期视图

```
┌─────────────────────────────────────────────────────────────────────┐
│  项目: 客户数据脱敏-Q2                         状态: ⚡进行中       │
│  描述: 对Q2客户信息表进行脱敏处理，确保合规                    [设置]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  处理进度                                                     │   │
│  │  [导入] ──→ [识别 ●●●●○] ──→ [复核] ──→ [脱敏] ──→ [报告]     │   │
│  │               正在识别中...  75%                                │   │
│  │  [██████████████░░░░░░░░░░░░░░░░░]                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐          │
│  │ 📤 数据   │ 🔍 识别   │ ✅ 复核   │ 🔒 脱敏   │ 📊 报告   │          │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┤          │
│  │ 3个数据集 │ 1个任务   │ 0/15已复  │ 待开始    │ 待生成    │          │
│  │          │ 15项敏感  │ 核        │          │          │          │
│  │          │ 发现      │          │          │          │          │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┤          │
│  │ [管理数据]│ [查看结果]│ [去复核]  │ [配置]   │ [预览]    │          │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  项目内数据集                                                    │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ ☑ customers.xlsx   │ 10,000行 │ 已识别 │ 待脱敏 │ [详情] │  │   │
│  │  │ ☑ orders.csv       │ 50,000行 │ 未识别 │ 待脱敏 │ [详情] │  │   │
│  │  │ ☑ employees.xlsx   │ 500行    │ 已脱敏 │ 已报告 │ [详情] │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  │  [+ 添加数据集]                                                │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

##### 页面3：任务中心（Task Center）— 统一的任务管理

```
┌─────────────────────────────────────────────────────────────────────┐
│  📋 任务中心                                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  [全部任务] [识别任务] [脱敏任务] [AI任务] [项目视图]         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  🔍 搜索...    [按状态: 全部 ▼]  [按项目: 全部 ▼]            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  ID │ 任务名称         │ 类型 │ 项目 │ 状态    │ 进度 │ 操作  │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  42 │ 客户表-规则识别   │ 识别 │ 客户Q2│ ✅完成 │ 100%│ [详情]│   │
│  │  43 │ 客户表-AI识别     │ AI   │ 客户Q2│ ⚡运行 │ 75% │ [取消]│   │
│  │  44 │ 订单表-脱敏       │ 脱敏 │ 客户Q2│ ⏳排队 │ 0%  │ [详情]│   │
│  │  45 │ 员工表-AI脱敏     │ AI   │ 客户Q2│ 📋待定 │ -   │ [配置]│   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  运行中任务实时看板                                             │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │  ⚡ 客户表-AI识别                                         │  │   │
│  │  │  数据集: customers.xlsx (10,000行)                        │  │   │
│  │  │  进度: [████████████░░░░░░░░░░] 75%  已发现: 12项敏感     │  │   │
│  │  │  当前处理: 第7,532行/10,000行  耗时: 45秒                 │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

#### 2.3.3 项目数据模型设计

```javascript
// Project → 核心业务实体
{
  id: 1,
  name: "客户数据脱敏-Q2",
  description: "对Q2客户信息表进行脱敏处理",
  status: "active",          // active | completed | archived
  progress: 60,              // 0-100
  created_at: "2026-05-19T10:00:00",
  
  // 关联数据
  datasets: [                // 项目内的数据集
    { id: 10, name: "customers.xlsx", row_count: 10000, status: "detected" },
    { id: 11, name: "orders.csv", row_count: 50000, status: "imported" }
  ],
  
  // 关联任务
  tasks: [                   // 项目内的所有任务（识别+脱敏+AI）
    { id: 42, type: "detection", dataset_id: 10, status: "completed" },
    { id: 43, type: "ai_detection", dataset_id: 10, status: "running" },
    { id: 44, type: "desensitization", dataset_id: 10, status: "pending" }
  ],
  
  // 项目配置（可复用）
  config: {
    detection_rule_set_id: 1,
    ai_config_id: 2,
    desensitization_key_id: 1,
    output_format: "xlsx"
  }
}
```

---

### 2.4 方案三：配置工作流（Config Workflow）

**适用场景**：技术专家配置规则、密钥、AI模型参数

**设计原则**：将现有的"识别规则管理/规则集管理/脱敏规则管理/AI配置管理/脱敏密钥管理"等**配置类页面**统一归入"配置中心"，并在导航中与日常操作流分离。

```
配置中心（统一入口）
├── 📋 识别规则库
│   ├── 内置规则库（只读）
│   └── 自定义规则（增删改）
├── 📋 规则集管理
│   ├── 新建规则集
│   └── 为规则集配置规则组合
├── 📋 脱敏规则库
│   ├── 内置脱敏规则（只读）
│   └── 自定义脱敏规则
├── 📋 脱敏密钥管理
│   ├── 默认密钥组
│   └── 自定义密钥组
├── 🤖 AI模型配置
│   ├── 模型列表
│   └── 连接测试
└── 📁 数据源管理
    ├── 数据库连接配置
    └── 连接测试
```

**UI交互改进**：
- 配置中心页面采用**卡片式布局**，每个配置项一张卡片
- 提供"配置检查"功能，一键检测是否有配置缺失（如未配置AI密钥时给出提示）
- 配置项与工作流关联：在快速/项目工作流中，如果某配置缺失，自动提示跳转到配置中心

---

## 三、导航重构方案

### 3.1 新导航结构

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔒 敏感信息智能识别与脱敏平台                     [主题] [帮助]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐                                                      │
│  │  首页     │  ← 工作台（项目列表 + 快速开始）                    │
│  ├──────────┤                                                      │
│  │  快速脱敏  │  ← 快速工作流（4步一气呵成）                      │
│  ├──────────┤                                                      │
│  │  我的项目  │  ← 项目列表 + 项目详情管理                         │
│  ├──────────┤                                                      │
│  │  任务中心  │  ← 统一查看所有任务运行状态                        │
│  ├──────────┤                                                      │
│  │  报告中心  │  ← 所有报告的聚合视图                              │
│  ├──────────┤                                                      │
│  │  配置中心  │  ← 规则/密钥/AI/数据源等配置管理                   │
│  ├──────────┤                                                      │
│  │  运营大盘  │  ← 平台运营KPI报表/领导视图                        │
│  └──────────┘                                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 新旧映射关系

| 新导航 | 原始导航 | 说明 |
|--------|---------|------|
| **首页** | 首页（Dashboard） | 改造为Workbench，增加项目列表和快速开始 |
| **快速脱敏** | —（新增） | 4步引导式快速工作流，调用现有功能 |
| **我的项目** | —（新增） | 项目管理页面，聚合数据集/任务/报告 |
| **任务中心** | 识别任务列表 + 脱敏任务列表 + AI任务列表 | 统一聚合所有任务类型 |
| **报告中心** | 运营报表（部分） | 整合规则校验报告+脱敏报告+AI报告 |
| **配置中心** | 数据集管理规则管理+AI配置管理+数据源配置 | 纯配置类页面统一归集 |
| **运营大盘** | 运营报表 | 领导视图，单独保留 |

### 3.3 路由映射

```
Old Route                    New Route
─────────────────────────────────────────────────────
/dashboard                   → /workbench

/datasets/list               → /workbench (嵌入在项目内)
/datasets/upload             → /workflow/express (快速流程)
/datasets/sources            → /settings/data-sources

/detection/rules             → /settings/detection-rules
/detection/rule-sets         → /settings/rule-sets
/detection/tasks             → /tasks?type=detection
/detection/tasks/create      → /workflow/express (步骤2)
/detection/tasks/:id         → /tasks/detection/:id

/desensitization/rules       → /settings/desensitization-rules
/desensitization/tasks       → /tasks?type=desensitization
/desensitization/tasks/create→ /workflow/express (步骤3)
/desensitization/tasks/:id   → /tasks/desensitization/:id

/ai/detection                → /workflow/express (AI选项)
/ai/config                   → /settings/ai-config

/report/platform             → /reports/operations
/report/dashboard            → /reports/validation
```

---

## 四、核心组件设计

### 4.1 组件树

```
App.vue
└── Layout.vue
    ├── Sidebar.vue (新导航)
    ├── Header.vue (面包屑+主题切换+操作提示)
    └── RouterView
        ├── Workbench.vue (新)
        │   ├── QuickStartCards.vue (新)
        │   ├── ProjectList.vue (新)
        │   └── PlatformOverview.vue (重用现有)
        │
        ├── WorkflowExpress.vue (新)
        │   ├── StepImport.vue (包装现有DatasetUpload)
        │   ├── StepDetect.vue (包装现有CreateDetectionTask)
        │   ├── StepDesensitize.vue (包装现有CreateDesensitizationTask)
        │   └── StepComplete.vue (包装现有报告组件)
        │
        ├── ProjectDetail.vue (新)
        │   ├── ProjectHeader.vue (新)
        │   ├── ProjectTimeline.vue (新)
        │   ├── ProjectDatasetList.vue (新)
        │   ├── ProjectTaskList.vue (新)
        │   └── ProjectReportList.vue (新)
        │
        ├── TaskCenter.vue (新)
        │   ├── TaskFilters.vue (新)
        │   ├── TaskTable.vue (新)
        │   └── TaskRunningBoard.vue (新)
        │
        ├── ReportCenter.vue (新)
        │   ├── ReportList.vue (新)
        │   └── ReportPreview.vue (重用现有)
        │
        ├── SettingsCenter.vue (新)
        │   ├── DetectionRules.vue (现有)
        │   ├── RuleSets.vue (现有)
        │   ├── DesensitizationRules.vue (现有)
        │   ├── DesensitizationKeys.vue (现有)
        │   ├── AiConfig.vue (现有)
        │   └── DataSources.vue (现有)
        │
        └── PlatformReport.vue (保留现有)
```

### 4.2 关键新组件设计

#### 4.2.1 Workbench.vue — 工作台

```vue
<template>
  <div class="workbench">
    <!-- 快捷操作区 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="startExpress">
          <el-icon size="32" color="#409EFF"><Lightning /></el-icon>
          <h3>快速脱敏</h3>
          <p>4步完成导入→识别→脱敏→报告</p>
          <el-tag size="small" type="primary">推荐</el-tag>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="createProject">
          <el-icon size="32" color="#67C23A"><FolderAdd /></el-icon>
          <h3>新建项目</h3>
          <p>管理复杂脱敏任务全流程</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/datasets/upload')">
          <el-icon size="32" color="#E6A23C"><Upload /></el-icon>
          <h3>导入数据</h3>
          <p>上传文件或连接数据库</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/settings')">
          <el-icon size="32" color="#909399"><Setting /></el-icon>
          <h3>配置管理</h3>
          <p>规则、密钥、AI模型配置</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近项目列表 -->
    <el-card class="section">
      <template #header>
        <div class="section-header">
          <span>📋 我的项目</span>
          <el-button text type="primary" @click="$router.push('/projects')">
            查看全部
          </el-button>
        </div>
      </template>
      <ProjectTable :projects="recentProjects" />
    </el-card>

    <!-- 平台概览（简约版） -->
    <el-card class="section">
      <template #header>
        <div class="section-header">
          <span>📊 平台概览</span>
          <el-button text type="primary" @click="$router.push('/reports/operations')">
            查看完整报表
          </el-button>
        </div>
      </template>
      <PlatformOverview :compact="true" />
    </el-card>
  </div>
</template>
```

#### 4.2.2 WorkflowExpress.vue — 快速脱敏工作流

使用 `el-steps` 组件做顶层导航，内部每个步骤是一个独立的面板：

```vue
<template>
  <div class="workflow-express">
    <!-- 步骤指示器 -->
    <el-steps :active="currentStep" align-center finish-status="success">
      <el-step title="选择数据" icon="Upload" />
      <el-step title="识别敏感数据" icon="Search" />
      <el-step title="配置脱敏" icon="Lock" />
      <el-step title="完成报告" icon="Document" />
    </el-steps>

    <!-- 步骤内容 -->
    <div class="step-content">
      <!-- 步骤1: 选择数据源 -->
      <StepImport
        v-if="currentStep === 0"
        v-model:dataset="selectedDataset"
        @next="goToStep(1)"
      />

      <!-- 步骤2: 识别敏感数据 -->
      <StepDetect
        v-if="currentStep === 1"
        :dataset="selectedDataset"
        v-model:result="detectionResult"
        @prev="goToStep(0)"
        @next="goToStep(2)"
      />

      <!-- 步骤3: 配置脱敏 -->
      <StepDesensitize
        v-if="currentStep === 2"
        :detection-result="detectionResult"
        @prev="goToStep(1)"
        @next="goToStep(3)"
      />

      <!-- 步骤4: 完成 -->
      <StepComplete
        v-if="currentStep === 3"
        :task-result="desensitizationResult"
        @prev="goToStep(2)"
        @restart="reset"
      />
    </div>
  </div>
</template>
```

**状态管理（Pinia Store）**：

```javascript
// stores/workflow.js
export const useWorkflowStore = defineStore('workflow', () => {
  const currentStep = ref(0)
  const selectedDataset = ref(null)      // 步骤1结果
  const detectionResult = ref(null)      // 步骤2结果
  const desensitizationConfig = ref({})  // 步骤3配置
  const desensitizationResult = ref(null)// 步骤4结果

  // 跨步骤数据传递
  function setDataset(dataset) {
    selectedDataset.value = dataset
  }
  function setDetectionResult(result) {
    detectionResult.value = result
  }
  function setDesensitizationConfig(config) {
    desensitizationConfig.value = config
  }

  // 重置
  function reset() {
    currentStep.value = 0
    selectedDataset.value = null
    detectionResult.value = null
    desensitizationConfig.value = {}
    desensitizationResult.value = null
  }

  return {
    currentStep, selectedDataset, detectionResult,
    desensitizationConfig, desensitizationResult,
    setDataset, setDetectionResult, setDesensitizationConfig, reset
  }
})
```

#### 4.2.3 ProjectDetail.vue — 项目详情

```
┌────────────────────────────────────────────────────────────────────┐
│  Header: 项目名称 + 状态标签 + 进度百分比 + 操作按钮                │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  时间轴进度条 (Process Timeline) — 5阶段可视化                      │
│  [导入] ── [识别] ── [复核] ── [脱敏] ── [报告]                     │
│  每个阶段可点击跳转（如果已到达该阶段）                               │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  五选项卡 (el-tabs):                                               │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐          │
│  │ 📤 数据集 │ 🔍 识别   │ ✅ 复核   │ 🔒 脱敏   │ 📊 报告   │          │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┤          │
│  │ 列表+管理  │ 任务状态  │ 复核进度  │ 任务状态  │ 报告列表  │          │
│  │ 添加数据  │ 查看详情  │ 去复核    │ 配置     │ 预览下载  │          │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘          │
│                                                                     │
│  每个tab内嵌对应的现有功能组件的轻量版                                │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

#### 4.2.4 TaskCenter.vue — 任务中心

```vue
<template>
  <div class="task-center">
    <!-- 运行中任务实时看板 -->
    <el-card v-if="runningTasks.length" class="running-board">
      <template #header>
        <span class="running-title">⚡ 运行中任务</span>
      </template>
      <el-row :gutter="16">
        <el-col v-for="task in runningTasks" :key="task.id" :span="8">
          <el-card shadow="always" class="task-card">
            <div class="task-name">{{ task.name }}</div>
            <el-progress :percentage="task.progress" :status="task.status" />
            <div class="task-meta">
              <span>已处理: {{ task.processed_rows }}/{{ task.total_rows }}行</span>
              <el-button text size="small" @click="cancelTask(task.id)">取消</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 任务列表 -->
    <el-card>
      <template #header>
        <div class="task-filters">
          <el-radio-group v-model="filter.type">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="detection">识别</el-radio-button>
            <el-radio-button value="desensitization">脱敏</el-radio-button>
            <el-radio-button value="ai_detection">AI识别</el-radio-button>
            <el-radio-button value="ai_desensitization">AI脱敏</el-radio-button>
          </el-radio-group>
          <el-select v-model="filter.status" placeholder="状态筛选" clearable>
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-select v-model="filter.project" placeholder="项目筛选" clearable>
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
      </template>
      <el-table :data="filteredTasks">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="任务名称" min-width="180" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="taskTypeTag(row.type)">{{ taskTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="所属项目" width="160" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.progress || 0" :width="120" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewTask(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
```

---

## 五、数据库层面改造

### 5.1 新增 projects 表

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '项目名称',
    description TEXT COMMENT '项目描述',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/completed/archived',
    progress INTEGER DEFAULT 0 COMMENT '进度百分比 0-100',
    config JSON COMMENT '项目默认配置(规则集ID/密钥ID等)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME COMMENT '完成时间'
);
```

### 5.2 为现有表添加 project_id 外键

```sql
ALTER TABLE datasets ADD COLUMN project_id INTEGER REFERENCES projects(id);
ALTER TABLE detection_tasks ADD COLUMN project_id INTEGER REFERENCES projects(id);
ALTER TABLE desensitization_tasks ADD COLUMN project_id INTEGER REFERENCES projects(id);
ALTER TABLE ai_detection_tasks ADD COLUMN project_id INTEGER REFERENCES projects(id);
ALTER TABLE ai_desensitization_tasks ADD COLUMN project_id INTEGER REFERENCES projects(id);
```

### 5.3 数据迁移策略

- 现有未关联的数据自动归入"未分组"（project_id = NULL）
- 新建项目时必须选择一个已经导入的数据集
- 支持在项目创建后添加更多数据集

---

## 六、API 接口扩展

### 6.1 新增接口

```
GET    /api/projects                    → 项目列表
POST   /api/projects                    → 创建项目
GET    /api/projects/:id                → 项目详情（含数据集+任务聚合）
PUT    /api/projects/:id                → 更新项目
DELETE /api/projects/:id                → 删除项目
GET    /api/projects/:id/stats          → 项目统计（进度/发现数等）
POST   /api/projects/:id/datasets       → 项目添加数据集
DELETE /api/projects/:id/datasets/:dsId → 项目移除数据集

GET    /api/tasks                       → 统一任务列表（含所有类型）
GET    /api/tasks/stats                 → 任务统计（运行中/完成等）
```

### 6.2 现有接口增强

```
现有接口的所有列表API增加 project_id 过滤参数
GET /api/detection/tasks?project_id=1
GET /api/desensitization/tasks?project_id=1
```

---

## 七、实施路线图

### Phase 1：最小可行方案（1-2周）

| 任务 | 说明 |
|------|------|
| 重构导航 | 修改 Layout.vue 中的菜单项，按新结构组织 |
| 改造首页为工作台 | 将 Dashboard.vue 替换为 Workbench.vue，包含快捷操作+项目列表 |
| 新建 TaskCenter | 聚合所有任务列表到一个统一视图 |
| 新建 SettingsCenter | 将规则/密钥/AI配置等页面归入统一入口 |

**变更文件清单**：
```
修改: frontend/src/router/index.js
修改: frontend/src/components/Layout.vue         (菜单项)
修改: frontend/src/themes/*/views/Dashboard.vue  (改为Workbench)
新建: frontend/src/views/workbench/Workbench.vue
新建: frontend/src/views/workbench/QuickStartCards.vue
新建: frontend/src/views/task/TaskCenter.vue
新建: frontend/src/views/settings/SettingsCenter.vue
```

### Phase 2：核心工作流（2-3周）

| 任务 | 说明 |
|------|------|
| 新建 projects 表 + API | 数据库迁移 + CRUD API |
| 快速工作流组件 | WorkflowExpress.vue + 4个步骤子组件 |
| 项目详情页 | ProjectDetail.vue + 5个选项卡 |
| 运行中任务看板 | TaskCenter 中的实时看板 |

### Phase 3：增强体验（1-2周）

| 任务 | 说明 |
|------|------|
| 项目模板 | 预置"金融合规""医疗数据"等模板 |
| 一键智能推荐 | 根据数据集内容自动推荐规则集和策略 |
| 批量操作 | 项目级别批量执行所有数据集的识别/脱敏 |
| WebSocket推送 | 任务进度从轮询改为服务端推送 |

---

## 八、用户场景验证

### 场景1：业务人员快速脱敏一个Excel文件

```
1. 登录后进入工作台
2. 点击"快速脱敏"卡片
3. 步骤1: 拖拽上传Excel文件 → 点击"下一步"
4. 步骤2: 选择"规则引擎识别" → 点击"开始识别"
   └── 实时看到进度条推进
5. 步骤3: 智能推荐脱敏规则 → 点击"预览"确认效果 → 点击"开始脱敏"
6. 步骤4: 下载脱敏文件 + 查看报告
```

**效率提升**：从需要5次页面跳转（上传→创建设识别任务→查看识别→创建脱敏任务→查看结果）→ 1次线性流程完成。

### 场景2：数据管理员管理多个数据集的脱敏项目

```
1. 进入工作台 → 点击"新建项目"
2. 填写项目信息 → 导入3个数据集
3. 在项目详情页看到5阶段进度条
4. 在"识别"选项卡中创建识别任务
5. 在"复核"选项卡中逐条确认敏感标记
6. 在"脱敏"选项卡中配置策略并执行
7. 在"报告"选项卡中下载所有报告
```

### 场景3：技术专家调整识别规则

```
1. 进入工作台 → 点击"配置管理"
2. 进入"识别规则库" → 添加自定义正则规则
3. 进入"规则集管理" → 将新规则加入"金融合规"规则集
4. 回到工作台 → 已有项目自动使用更新后的规则集
```

---

## 九、风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| 现有功能页面与工作流组件耦合 | 维护成本增加 | 工作流组件只做"编排"，内嵌现有组件，不重复实现逻辑 |
| 数据库增加 project_id 外键 | 现有接口需要适配 | 兼容 NULL 值，旧数据不受影响 |
| 用户习惯改变 | 学习成本 | 保留旧导航入口（配置中心），提供切换开关 |
| 大项目大量数据集性能 | 页面加载慢 | 项目列表分页+懒加载，进度统计用独立API |

---

## 十、总结

本方案的核心思路是**"三个维度，一个核心"**：

| 维度 | 解决的问题 | 面向用户 |
|------|-----------|---------|
| **快速工作流** | 让简单任务一步到位 | 所有用户 |
| **项目工作流** | 让复杂任务全程可控 | 数据管理员 |
| **配置工作流** | 让系统配置集中可管 | 技术专家 |

通过引入"项目"作为核心业务实体，将分散在"数据集管理/敏感数据识别/数据脱敏/AI智能"四个模块中的功能重新串联为一条完整的业务链路，同时保留技术配置的统一入口，使平台既能**快速上手**又能**深度使用**。
