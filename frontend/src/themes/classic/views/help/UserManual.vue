<template>
  <div class="user-manual">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户操作手册</span>
          <el-tag type="success">无需编程基础</el-tag>
        </div>
      </template>

      <el-alert
        title="欢迎使用敏感信息脱敏平台"
        description="本手册面向所有用户，无需编写代码即可完成敏感数据的识别与脱敏。平台支持多语言识别、智能脱敏、报告导出等强大功能。"
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-collapse v-model="activeNames">
        <!-- 快速开始 -->
        <el-collapse-item name="1">
          <template #title>
            <div class="collapse-title">
              <el-icon><Star /></el-icon>
              <span>快速开始（三步完成脱敏）</span>
            </div>
          </template>

          <el-steps :active="3" simple>
            <el-step title="导入数据" icon="Upload" />
            <el-step title="识别敏感信息" icon="Search" />
            <el-step title="执行脱敏" icon="Lock" />
          </el-steps>

          <div class="step-detail">
            <h4>第1步：导入数据</h4>
            <p>点击左侧菜单 <el-tag size="small">数据集管理</el-tag>，选择以下方式之一：</p>
            <ul>
              <li><strong>文件上传</strong>：支持 Excel、CSV、JSON、文本、Markdown、日志文件</li>
              <li><strong>数据库连接</strong>：连接 MySQL/PostgreSQL/Oracle/SQL Server，选择表导入</li>
              <li><strong>剪贴板粘贴</strong>：直接粘贴表格数据</li>
            </ul>

            <h4>第2步：识别敏感信息</h4>
            <p>进入 <el-tag size="small">敏感数据识别 → 识别任务</el-tag>：</p>
            <ol>
              <li>点击"创建识别任务"</li>
              <li>选择数据集和识别规则</li>
              <li>点击"开始识别"，等待完成</li>
              <li>查看识别报告，了解发现了哪些敏感数据</li>
            </ol>

            <h4>第3步：执行脱敏</h4>
            <p>在识别结果页面，点击 <el-button type="primary" size="small">一键跳转脱敏</el-button>：</p>
            <ol>
              <li>系统自动推荐每列的脱敏规则</li>
              <li>预览脱敏效果（前后对比）</li>
              <li>确认满意后，点击"开始脱敏"</li>
              <li>下载脱敏后的数据文件或导出报告</li>
            </ol>
          </div>
        </el-collapse-item>

        <!-- 数据源配置 -->
        <el-collapse-item name="2">
          <template #title>
            <div class="collapse-title">
              <el-icon><Link /></el-icon>
              <span>数据源配置详解</span>
            </div>
          </template>

          <el-tabs type="border-card">
            <el-tab-pane label="文件上传">
              <h4>支持的文件格式</h4>
              <el-row :gutter="10">
                <el-col :span="4" v-for="fmt in fileFormats" :key="fmt.name">
                  <el-card shadow="hover" class="format-card">
                    <el-icon :size="24"><Document /></el-icon>
                    <div>{{ fmt.name }}</div>
                    <div class="format-ext">{{ fmt.ext }}</div>
                  </el-card>
                </el-col>
              </el-row>

              <h4>操作步骤</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="(step, idx) in fileSteps"
                  :key="idx"
                  :type="step.type"
                  :icon="step.icon"
                >
                  {{ step.content }}
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>

            <el-tab-pane label="数据库连接">
              <h4>支持的数据库</h4>
              <el-row :gutter="10">
                <el-col :span="6" v-for="db in databases" :key="db.name">
                  <el-card shadow="hover" class="db-card">
                    <el-icon :size="24"><Connection /></el-icon>
                    <div>{{ db.name }}</div>
                    <div class="db-port">端口: {{ db.port }}</div>
                  </el-card>
                </el-col>
              </el-row>

              <h4>连接步骤</h4>
              <el-steps direction="vertical" :active="5">
                <el-step title="填写连接信息">
                  <template #description>
                    输入数据源名称、数据库类型、主机地址、端口、数据库名、用户名和密码
                  </template>
                </el-step>
                <el-step title="测试连接">
                  <template #description>
                    点击"测试连接"按钮，确认能正常连接到数据库
                  </template>
                </el-step>
                <el-step title="加载表列表">
                  <template #description>
                    点击"加载表列表"，系统会读取数据库中的所有表
                  </template>
                </el-step>
                <el-step title="选择表">
                  <template #description>
                    勾选需要导入的表（支持多选），可设置数据集名称前缀
                  </template>
                </el-step>
                <el-step title="导入">
                  <template #description>
                    点击"导入选中表到数据集"，完成导入
                  </template>
                </el-step>
              </el-steps>

              <el-alert
                title="安全提示"
                type="warning"
                show-icon
                :closable="false"
                style="margin-top: 15px"
              >
                <p>建议为平台创建专用的数据库只读账号，限制访问权限，定期更换密码。</p>
              </el-alert>
            </el-tab-pane>

            <el-tab-pane label="剪贴板粘贴">
              <p>适合快速测试小量数据：</p>
              <ol>
                <li>在 Excel 或其他表格软件中复制数据</li>
                <li>进入"数据集管理" → "导入数据"</li>
                <li>选择"剪贴板粘贴"标签</li>
                <li>粘贴数据，选择格式（CSV/JSON）</li>
                <li>命名并导入</li>
              </ol>
            </el-tab-pane>
          </el-tabs>
        </el-collapse-item>

        <!-- 敏感数据识别 -->
        <el-collapse-item name="3">
          <template #title>
            <div class="collapse-title">
              <el-icon><Search /></el-icon>
              <span>敏感数据识别详解</span>
            </div>
          </template>

          <h4>支持的敏感类型（按语言）</h4>
          <el-table :data="sensitiveTypes" style="width: 100%">
            <el-table-column prop="language" label="语言" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.tagType">{{ scope.row.language }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="types" label="支持的敏感类型" />
          </el-table>

          <h4 style="margin-top: 20px">识别任务流程</h4>
          <el-steps :active="4" simple>
            <el-step title="选择数据集" />
            <el-step title="选择规则集" />
            <el-step title="配置语言策略" />
            <el-step title="开始识别" />
          </el-steps>

          <div class="detail-section">
            <h4>语言策略说明</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="自动检测">
                系统自动判断每行数据的语言，使用对应语言的识别规则（推荐）
              </el-descriptions-item>
              <el-descriptions-item label="指定语言">
                强制使用某种语言的规则，适合已知数据语言的场景
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="detail-section">
            <h4>识别报告内容</h4>
            <ul>
              <li><strong>敏感类型分布饼图</strong>：直观展示发现了哪些类型的敏感数据</li>
              <li><strong>每列敏感密度柱状图</strong>：了解哪些列包含最多敏感信息</li>
              <li><strong>明细列表</strong>：每条敏感数据的具体位置（列名、行号、命中规则）</li>
              <li><strong>脱敏建议</strong>：系统推荐每列应该使用的脱敏方式</li>
            </ul>
          </div>
        </el-collapse-item>

        <!-- 数据脱敏 -->
        <el-collapse-item name="4">
          <template #title>
            <div class="collapse-title">
              <el-icon><Lock /></el-icon>
              <span>数据脱敏详解</span>
            </div>
          </template>

          <h4>脱敏规则类型</h4>
          <el-table :data="desensitizationRules" style="width: 100%">
            <el-table-column prop="name" label="规则名称" width="150" />
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例" width="250" />
          </el-table>

          <div class="detail-section">
            <h4>创建脱敏任务的两种方式</h4>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>方式一：从识别结果跳转（推荐）</span>
                  </template>
                  <ol>
                    <li>在识别结果页点击"一键跳转脱敏"</li>
                    <li>系统自动加载需要脱敏的列</li>
                    <li>自动推荐每列的脱敏规则</li>
                    <li>无需重复配置，直接进入预览</li>
                  </ol>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>方式二：手动创建</span>
                  </template>
                  <ol>
                    <li>进入"数据脱敏 → 脱敏任务"</li>
                    <li>点击"创建脱敏任务"</li>
                    <li>选择数据来源（数据集）</li>
                    <li>手动为每列配置脱敏规则</li>
                    <li>或使用"智能推荐"一键配置</li>
                  </ol>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <div class="detail-section">
            <h4>脱敏效果确认</h4>
            <p>在确认页面，系统会展示 <strong>10-20 条数据的前后对比</strong>：</p>
            <ul>
              <li>检查脱敏效果是否符合预期</li>
              <li>如不满意，返回上一步调整规则</li>
              <li>确认无误后，选择输出方式</li>
            </ul>
          </div>

          <div class="detail-section">
            <h4>输出方式</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="生成副本（推荐）">
                保留原始数据，生成新的脱敏文件。文件名带"_脱敏后_时间戳"后缀。
              </el-descriptions-item>
              <el-descriptions-item label="覆盖原数据">
                <span style="color: #f56c6c; font-weight: bold">高危操作！</span>
                直接修改原始数据，系统会显示红色警告并要求二次确认。
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-collapse-item>

        <!-- 报告管理 -->
        <el-collapse-item name="5">
          <template #title>
            <div class="collapse-title">
              <el-icon><Document /></el-icon>
              <span>报告管理</span>
            </div>
          </template>

          <h4>报告类型</h4>
          <el-table :data="reportTypes" style="width: 100%">
            <el-table-column prop="type" label="报告类型" width="150" />
            <el-table-column prop="format" label="支持格式" width="150" />
            <el-table-column prop="description" label="说明" />
          </el-table>

          <div class="detail-section">
            <h4>在线预览</h4>
            <p>在任务详情页面，点击 <el-button type="primary" size="small">在线预览</el-button> 按钮：</p>
            <ul>
              <li>浏览器新标签页打开HTML格式的报告</li>
              <li>包含完整的统计图表和数据表格</li>
              <li>无需下载，直接查看</li>
            </ul>
          </div>

          <div class="detail-section">
            <h4>下载报告</h4>
            <p>在任务详情页面，点击 <el-button type="warning" size="small">下载报告</el-button> 按钮：</p>
            <ul>
              <li><strong>HTML格式</strong>：下载.html文件，可用浏览器打开</li>
              <li><strong>Markdown格式</strong>：下载.md文件，适合存档和版本管理</li>
            </ul>
            <el-alert
              title="提示"
              type="info"
              show-icon
              :closable="false"
              style="margin-top: 10px"
            >
              <p>Markdown格式报告可以用任何文本编辑器打开，也支持导入到GitHub、GitLab等平台。</p>
            </el-alert>
          </div>
        </el-collapse-item>

        <!-- 管理功能 -->
        <el-collapse-item name="6">
          <template #title>
            <div class="collapse-title">
              <el-icon><Setting /></el-icon>
              <span>管理功能</span>
            </div>
          </template>

          <h4>识别规则管理</h4>
          <p>进入 <el-tag size="small">敏感数据识别 → 识别规则管理</el-tag>：</p>
          <ul>
            <li>查看所有内置规则，按语言/类型筛选</li>
            <li>创建自定义规则（正则表达式或关键词）</li>
            <li>测试规则效果</li>
            <li>创建规则集（将多个规则组合使用）</li>
            <li>导入/导出规则集（便于团队协作）</li>
          </ul>

          <h4>脱敏规则管理</h4>
          <p>进入 <el-tag size="small">数据脱敏 → 脱敏规则管理</el-tag>：</p>
          <ul>
            <li>查看所有内置脱敏规则</li>
            <li>创建自定义脱敏规则</li>
            <li>管理脱敏密钥（用于关联仿真）</li>
          </ul>

          <h4>系统设置</h4>
          <p>管理员可配置：</p>
          <ul>
            <li>数据自动清理周期</li>
            <li>日志级别</li>
            <li>平台默认规则启停</li>
          </ul>
        </el-collapse-item>

        <!-- 页面风格切换 -->
        <el-collapse-item name="7">
          <template #title>
            <div class="collapse-title">
              <el-icon><Brush /></el-icon>
              <span>页面风格切换</span>
            </div>
          </template>

          <el-alert
            title="个性化界面体验"
            description="平台提供四种精心设计的页面风格，您可以根据个人喜好随时切换。"
            type="info"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />

          <h4>支持的风格</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <el-card shadow="hover" class="theme-card">
                <div class="theme-preview classic-preview">
                  <div class="preview-sidebar"></div>
                  <div class="preview-content"></div>
                </div>
                <div class="theme-name">
                  <el-icon><Sunny /></el-icon>
                  <span>经典风格</span>
                </div>
                <div class="theme-desc">简洁明快的蓝白配色，清晰易读，适合日常办公</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="theme-card">
                <div class="theme-preview dark-purple-preview">
                  <div class="preview-sidebar"></div>
                  <div class="preview-content"></div>
                </div>
                <div class="theme-name">
                  <el-icon><Moon /></el-icon>
                  <span>暗紫风格</span>
                </div>
                <div class="theme-desc">深邃紫雾玻璃质感，神秘优雅，适合夜间使用</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="theme-card">
                <div class="theme-preview black-gold-preview">
                  <div class="preview-sidebar"></div>
                  <div class="preview-content"></div>
                </div>
                <div class="theme-name">
                  <el-icon><Star /></el-icon>
                  <span>黑金风格</span>
                </div>
                <div class="theme-desc">青苔紫夜奢华质感，沉稳大气，彰显专业品质</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="theme-card">
                <div class="theme-preview vue-classic-preview">
                  <div class="preview-sidebar"></div>
                  <div class="preview-content"></div>
                </div>
                <div class="theme-name">
                  <el-icon><Connection /></el-icon>
                  <span>Vue经典</span>
                </div>
                <div class="theme-desc">传统Vue蓝白风格，经典侧边栏布局，熟悉可靠</div>
              </el-card>
            </el-col>
          </el-row>

          <div class="detail-section">
            <h4>如何切换风格</h4>
            <el-steps direction="vertical" :active="3">
              <el-step title="找到切换入口">
                <template #description>
                  在页面右上角，用户信息左侧，找到当前风格显示按钮（如 <el-tag size="small" type="primary">经典</el-tag>）
                </template>
              </el-step>
              <el-step title="点击展开菜单">
                <template #description>
                  点击风格按钮，会弹出下拉菜单，显示所有可选风格
                </template>
              </el-step>
              <el-step title="选择新风格">
                <template #description>
                  点击想要切换的风格（经典 / Vue经典 / 暗紫 / 黑金），页面会立即应用新风格
                </template>
              </el-step>
            </el-steps>
          </div>

          <div class="detail-section">
            <h4>风格特点对比</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="经典风格">
                采用传统的蓝白配色方案，界面清晰明亮，适合白天办公使用，长时间操作不易疲劳
              </el-descriptions-item>
              <el-descriptions-item label="暗紫风格">
                采用暮色紫雾玻璃质感设计，深色背景搭配金色文字，降低屏幕亮度刺激，适合夜间或暗光环境
              </el-descriptions-item>
              <el-descriptions-item label="黑金风格">
                采用青苔紫夜奢华质感，深色基底搭配淡金装饰，视觉效果沉稳大气，适合演示汇报场景
              </el-descriptions-item>
              <el-descriptions-item label="GitHub风格">
                采用极简GitHub代码平台设计风格，深色侧边栏搭配浅色内容区，蓝绿功能色，简洁高效，适合开发者使用
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <el-alert
            title="提示"
            type="success"
            show-icon
            :closable="false"
            style="margin-top: 15px"
          >
            <p>切换风格后页面会自动刷新以应用新风格的全部样式（包括布局、配色和组件），您的选择会自动保存，下次登录时恢复上次的风格。</p>
          </el-alert>
        </el-collapse-item>

        <!-- 平台运营成效 -->
        <el-collapse-item name="8">
          <template #title>
            <div class="collapse-title">
              <el-icon><TrendCharts /></el-icon>
              <span>平台运营成效</span>
            </div>
          </template>

          <el-alert
            title="领导决策视图"
            description="平台运营成效页面提供全局数据大盘，帮助管理者快速了解平台运行状态和安全保护成效。"
            type="success"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />

          <h4>页面布局（从上到下）</h4>
          <el-timeline>
            <el-timeline-item type="primary" icon="DataBoard">
              <strong>核心指标总览</strong>
              <p>顶部展示6个关键KPI卡片：数据集总数、识别任务、脱敏任务、敏感信息发现、识别准确率、脱敏覆盖率</p>
            </el-timeline-item>
            <el-timeline-item type="success" icon="TrophyBase">
              <strong>平台核心价值总结</strong>
              <p>展示智能自动化率、识别-脱敏一体化、关联造数应用三大核心价值指标</p>
            </el-timeline-item>
            <el-timeline-item type="warning" icon="DocumentChecked">
              <strong>数据合规保障 + 平台优势</strong>
              <p>左侧展示数据合规指标（字段保护率、任务完成率、累计行数、闭环率、数据源规模、处理效率、审计报告），右侧展示平台核心优势结论</p>
            </el-timeline-item>
            <el-timeline-item type="primary" icon="Cpu">
              <strong>技术创新与先进性</strong>
              <p>展示关联仿真脱敏、多语言智能识别、高性能异步处理三大技术亮点</p>
            </el-timeline-item>
            <el-timeline-item type="info" icon="TrendCharts">
              <strong>安全保护成效 + 效率趋势</strong>
              <p>敏感数据安全保护成效饼图 + 近7天自动化处理效率折线图</p>
            </el-timeline-item>
          </el-timeline>

          <div class="detail-section">
            <h4>合规指标详解</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="敏感字段保护率">
                已配置脱敏规则的敏感字段占全部敏感字段的比例
              </el-descriptions-item>
              <el-descriptions-item label="脱敏任务完成率">
                已完成的脱敏任务占全部脱敏任务的比例
              </el-descriptions-item>
              <el-descriptions-item label="累计处理行数">
                平台累计处理的敏感数据记录总量
              </el-descriptions-item>
              <el-descriptions-item label="识别-脱敏闭环率">
                已完成脱敏的敏感信息占全部识别出的敏感信息的比例，体现端到端处理能力
              </el-descriptions-item>
              <el-descriptions-item label="数据源接入规模">
                已接入的数据源数量，体现平台数据纳管广度
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <el-alert
            title="提示"
            type="info"
            show-icon
            :closable="false"
            style="margin-top: 15px"
          >
            <p>所有运营数据均为实时计算，数据刷新频率为每分钟自动更新。上方显示"实时数据"标签和更新时间。</p>
          </el-alert>
        </el-collapse-item>

        <!-- AI智能功能亮点 -->
        <el-collapse-item name="9">
          <template #title>
            <div class="collapse-title">
              <el-icon><Cpu /></el-icon>
              <span>AI智能功能亮点</span>
            </div>
          </template>

          <el-alert
            title="不止于脱敏，更是全流程智能数据安全治理"
            description="相比传统仅提供单一脱敏功能的工具，本平台基于AI技术构建了从识别到脱敏的完整闭环，实现真正的智能化数据安全治理。"
            type="success"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />

          <h4>🚀 全流程自动化（传统工具 vs 本平台）</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="传统脱敏工具">
              仅提供脱敏功能，用户需手动识别敏感字段、手动配置规则、手动上传数据，流程断裂，效率低下
            </el-descriptions-item>
            <el-descriptions-item label="本平台">
              <el-tag type="success">识别→推荐→脱敏→报告</el-tag> 全流程自动化，AI自动识别敏感数据并推荐最优脱敏规则，一键完成从发现到保护的全过程
            </el-descriptions-item>
          </el-descriptions>

          <div class="detail-section">
            <h4>🌍 多语言智能识别（行业首创）</h4>
            <p>传统工具仅支持中文或英文，本平台基于字符集特征分析技术，<strong>自动检测6种语言</strong>：</p>
            <el-row :gutter="10">
              <el-col :span="4" v-for="lang in multilingualSupport" :key="lang.name">
                <el-card shadow="hover" class="lang-card">
                  <el-tag :type="lang.type" size="large">{{ lang.name }}</el-tag>
                  <div class="lang-desc">{{ lang.desc }}</div>
                </el-card>
              </el-col>
            </el-row>
            <el-alert
              title="技术优势"
              type="info"
              show-icon
              :closable="false"
              style="margin-top: 15px"
            >
              <p>基于字符集特征自动判断每行数据语言，无需用户手动选择，准确率超过95%，大幅降低多语言数据处理门槛。</p>
            </el-alert>
          </div>

          <div class="detail-section">
            <h4>⚡ 高性能异步处理（速度领先）</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="处理速度">
                后台异步处理，支持实时进度查看，大文件也能流畅操作，不阻塞前端交互
              </el-descriptions-item>
              <el-descriptions-item label="实时进度">
                支持实时查看处理进度和预计完成时间，任务状态自动刷新
              </el-descriptions-item>
              <el-descriptions-item label="模型配置">
                支持云端API（OpenAI/DeepSeek/千问等）和本地部署（Ollama/LM Studio），按需选择，<el-tag type="success">灵活可控</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="detail-section">
            <h4>🔐 独创关联仿真脱敏（跨表一致性保障）</h4>
            <p>传统随机脱敏会导致同一数据在不同表中脱敏结果不同，破坏数据关联关系。本平台独创的<strong>基于密钥的确定性脱敏算法</strong>：</p>
            <ul>
              <li>同一原始值 + 同一密钥 = 始终生成相同的脱敏结果</li>
              <li>支持 <el-tag type="primary">30组独立密钥</el-tag>，实现不同业务场景的安全隔离</li>
              <li>保证跨表、跨库数据关联关系的完整性</li>
              <li>既保护隐私，又保留数据分析价值</li>
            </ul>
          </div>

          <div class="detail-section">
            <h4>🎯 智能规则推荐（降低人工配置成本）</h4>
            <p>基于AI分析识别结果，系统自动为每列数据推荐最优脱敏规则：</p>
            <el-timeline>
              <el-timeline-item type="primary" icon="Search">
                <strong>自动识别字段类型</strong>
                <p>系统分析列名、数据格式、内容特征，判断字段类型（姓名、手机号、身份证号等）</p>
              </el-timeline-item>
              <el-timeline-item type="success" icon="MagicStick">
                <strong>智能匹配脱敏规则</strong>
                <p>根据字段类型自动推荐最适合的脱敏方式（遮盖、仿真、关联仿真等）</p>
              </el-timeline-item>
              <el-timeline-item type="warning" icon="View">
                <strong>预览确认后执行</strong>
                <p>展示10-20条数据前后对比，用户确认无误后执行全量脱敏，避免误操作</p>
              </el-timeline-item>
            </el-timeline>
          </div>

          <div class="detail-section">
            <h4>📊 可视化安全确认（零风险操作）</h4>
            <p>脱敏前强制展示数据前后对比，确保用户对脱敏效果满意后才执行全量处理，<strong>从根本上避免误操作导致的数据损坏</strong>。</p>
          </div>

          <el-alert
            title="总结"
            type="success"
            show-icon
            :closable="false"
            style="margin-top: 15px"
          >
            <p>本平台不仅是脱敏工具，更是基于AI技术的<strong>全流程数据安全治理平台</strong>。从多语言智能识别、自动规则推荐、高性能异步处理到独创关联仿真，每个环节都体现了智能化、自动化、安全化的设计理念，真正实现"让数据安全治理变得简单"。</p>
          </el-alert>
        </el-collapse-item>

        <!-- 任务监控与刷新 -->
        <el-collapse-item name="10">
          <template #title>
            <div class="collapse-title">
              <el-icon><RefreshRight /></el-icon>
              <span>任务监控与刷新</span>
            </div>
          </template>

          <el-alert
            title="实时监控任务状态"
            description="平台提供手动刷新和自动刷新两种任务监控方式，确保您随时掌握任务执行进度。"
            type="info"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />

          <h4>脱敏任务列表页面</h4>
          <p>进入 <el-tag size="small">数据脱敏 → 脱敏任务</el-tag>，在页面右上角可以看到以下控制项：</p>

          <div class="detail-section">
            <h4>🔄 手动刷新</h4>
            <p>点击 <el-button size="small"><el-icon><Refresh /></el-icon> 刷新</el-button> 按钮，立即获取最新任务状态和进度。</p>
            <ul>
              <li>适合需要精确控制刷新时机的场景</li>
              <li>刷新时按钮显示加载状态，避免重复点击</li>
              <li>刷新成功后会弹出提示</li>
            </ul>
          </div>

          <div class="detail-section">
            <h4>⏱️ 自动刷新（推荐）</h4>
            <p>开启 <el-switch v-model="demoAutoRefresh" active-text="自动刷新" inline-prompt style="vertical-align: middle;" /> 开关后：</p>
            <ul>
              <li>当列表中存在<strong>进行中（running）</strong>或<strong>待处理（pending）</strong>的任务时，系统会自动每3秒刷新一次</li>
              <li>所有任务完成后，自动刷新会自动停止，节省资源</li>
              <li>智能更新机制：只更新状态/进度变化的行，避免整表闪烁</li>
              <li>离开页面后自动停止刷新，避免后台不必要的请求</li>
            </ul>
            <el-alert
              title="使用建议"
              type="success"
              show-icon
              :closable="false"
              style="margin-top: 10px"
            >
              <p>建议保持自动刷新开启，这样您可以实时看到任务进度变化，无需手动操作。</p>
            </el-alert>
          </div>

          <div class="detail-section">
            <h4>📋 任务详情页面</h4>
            <p>点击任务列表中的 <el-button type="primary" size="small">详情</el-button> 按钮进入任务详情页：</p>
            <ul>
              <li>详情页同样支持手动刷新和自动刷新功能</li>
              <li>自动刷新会实时更新任务进度、已处理行数、处理速度等指标</li>
              <li>任务完成后会自动弹出完成提示</li>
              <li>可在详情页直接下载脱敏结果和报告</li>
            </ul>
          </div>

          <div class="detail-section">
            <h4>任务状态说明</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="待处理 (pending)">
                <el-tag type="info">待处理</el-tag> 任务已创建，等待系统调度执行
              </el-descriptions-item>
              <el-descriptions-item label="进行中 (running)">
                <el-tag type="warning">进行中</el-tag> 任务正在执行，显示实时进度
              </el-descriptions-item>
              <el-descriptions-item label="已完成 (completed)">
                <el-tag type="success">已完成</el-tag> 任务执行成功，可以下载结果
              </el-descriptions-item>
              <el-descriptions-item label="失败 (failed)">
                <el-tag type="danger">失败</el-tag> 任务执行失败，请查看错误信息并重试
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-collapse-item>

        <!-- 常见问题 -->
        <el-collapse-item name="11">
          <template #title>
            <div class="collapse-title">
              <el-icon><QuestionFilled /></el-icon>
              <span>常见问题</span>
            </div>
          </template>

          <el-collapse>
            <el-collapse-item title="支持多大的数据文件？">
              <p>默认支持最大 100MB 的文件。对于更大的数据，建议：</p>
              <ul>
                <li>使用数据库连接直接导入</li>
                <li>将大文件拆分成多个小文件</li>
                <li>联系管理员调整上传限制</li>
              </ul>
            </el-collapse-item>

            <el-collapse-item title="识别结果不准确怎么办？">
              <ol>
                <li>检查是否选择了正确的语言策略</li>
                <li>尝试创建自定义规则，更精确地匹配您的数据格式</li>
                <li>调整规则集的组成，只使用需要的规则</li>
              </ol>
            </el-collapse-item>

            <el-collapse-item title="脱敏后的数据还能恢复吗？">
              <ul>
                <li><strong>遮盖模式</strong>：不能恢复，原始数据已永久替换</li>
                <li><strong>仿真模式</strong>：不能反向恢复，但相同原始数据+相同密钥会生成相同的假数据</li>
                <li><strong>建议</strong>：脱敏前务必备份原始数据，或使用"生成副本"模式</li>
              </ul>
            </el-collapse-item>

            <el-collapse-item title="关联仿真是什么意思？">
              <p>关联仿真确保：</p>
              <ul>
                <li>相同的原始数据（如"张三"）在不同表中脱敏后得到相同的假数据（如"李四"）</li>
                <li>这样保持了数据表之间的关联关系</li>
                <li>需要选择相同的脱敏密钥才能实现</li>
              </ul>
            </el-collapse-item>

            <el-collapse-item title="数据库连接不上怎么办？">
              <ol>
                <li>检查主机地址和端口是否正确</li>
                <li>确认数据库服务是否启动</li>
                <li>检查用户名密码是否正确</li>
                <li>确认数据库是否允许远程连接</li>
                <li>检查防火墙是否放行了对应端口</li>
              </ol>
            </el-collapse-item>

            <el-collapse-item title="支持哪些浏览器？">
              <p>推荐使用：</p>
              <ul>
                <li>Google Chrome（最新版）</li>
                <li>Microsoft Edge（最新版）</li>
                <li>Mozilla Firefox（最新版）</li>
              </ul>
            </el-collapse-item>

            <el-collapse-item title="Markdown报告有什么优势？">
              <ul>
                <li><strong>纯文本</strong>：可以用任何文本编辑器打开和编辑</li>
                <li><strong>版本友好</strong>：适合用Git进行版本管理</li>
                <li><strong>平台兼容</strong>：支持GitHub、GitLab、Notion等平台渲染</li>
                <li><strong>转换灵活</strong>：可以轻松转换为PDF、Word等其他格式</li>
                <li><strong>轻量级</strong>：文件体积小，便于传输和存储</li>
              </ul>
            </el-collapse-item>
          </el-collapse>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Star, Link, Search, Lock, Setting, QuestionFilled,
  Document, Connection, Brush, Sunny, Moon,
  TrendCharts, DataBoard, TrophyBase, DocumentChecked, Cpu,
  Refresh, RefreshRight, MagicStick
} from '@element-plus/icons-vue'

const activeNames = ref(['1'])
const demoAutoRefresh = ref(true)

const fileFormats = [
  { name: 'Excel', ext: '.xlsx / .xls' },
  { name: 'CSV', ext: '.csv' },
  { name: '文本', ext: '.txt' },
  { name: 'JSON', ext: '.json' },
  { name: 'Markdown', ext: '.md' },
  { name: '日志', ext: '.log' }
]

const fileSteps = [
  { content: '进入"数据集管理"页面，点击"导入数据"', type: 'primary', icon: 'Location' },
  { content: '选择"文件上传"标签', type: 'primary', icon: 'Document' },
  { content: '拖拽文件到上传区域，或点击选择文件', type: 'primary', icon: 'Upload' },
  { content: '系统自动识别文件格式和编码', type: 'success', icon: 'Check' },
  { content: '给数据集命名，点击确认导入', type: 'success', icon: 'CircleCheck' }
]

const databases = [
  { name: 'MySQL', port: 3306 },
  { name: 'PostgreSQL', port: 5432 },
  { name: 'Oracle', port: 1521 },
  { name: 'SQL Server', port: 1433 }
]

const sensitiveTypes = [
  { language: '中文', types: '姓名、手机号、身份证号、银行卡号、地址、邮箱', tagType: 'danger' },
  { language: '英文', types: '姓名、手机号、邮箱、信用卡号、护照号', tagType: 'primary' },
  { language: '日文', types: '姓名、手机号、地址', tagType: 'warning' },
  { language: '韩文', types: '姓名、手机号', tagType: 'success' },
  { language: '法文', types: '姓名、邮箱', tagType: 'info' },
  { language: '德文', types: '姓名、邮箱', tagType: 'info' }
]

const desensitizationRules = [
  { name: '部分遮盖', description: '保留前后几位，中间用*代替', example: '13800138000 → 138****8000' },
  { name: '等长遮盖', description: '全部替换为等长的*', example: '张三 → **' },
  { name: '固定遮盖', description: '替换为固定字符串', example: '任意内容 → ***' },
  { name: '随机仿真', description: '生成格式相同但随机的假数据', example: '13800138000 → 13987654321' },
  { name: '关联仿真', description: '相同原始数据总是生成相同的假数据', example: '张三(表A) → 李四; 张三(表B) → 李四' }
]

const reportTypes = [
  { type: '识别报告', format: 'HTML / Markdown', description: '展示敏感数据识别结果和分布统计' },
  { type: '脱敏报告', format: 'HTML / Markdown', description: '展示脱敏处理详情、准确率、性能指标' }
]

const multilingualSupport = [
  { name: '中文', desc: '姓名、手机号、身份证', type: 'danger' },
  { name: '英文', desc: '姓名、邮箱、信用卡', type: 'primary' },
  { name: '日文', desc: '姓名、手机号、地址', type: 'warning' },
  { name: '韩文', desc: '姓名、手机号', type: 'success' },
  { name: '法文', desc: '姓名、邮箱', type: 'info' },
  { name: '德文', desc: '姓名、邮箱', type: 'info' }
]
</script>

<style scoped>
.user-manual {
  padding: 20px 20px 20px 6em;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  padding-left: 1.5em;
}

:deep(.el-collapse-item__content) {
  padding-left: 1.5em;
}

.step-detail {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-top: 15px;
}

.step-detail h4 {
  margin-top: 15px;
  margin-bottom: 10px;
  color: #409eff;
}

.step-detail h4:first-child {
  margin-top: 0;
}

.step-detail ul, .step-detail ol {
  margin-left: 20px;
  line-height: 2;
}

.format-card, .db-card {
  text-align: center;
  padding: 10px;
}

.format-ext, .db-port {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.detail-section {
  margin-top: 20px;
}

/* 主题预览卡片 */
.theme-card {
  text-align: center;
}

.theme-preview {
  height: 80px;
  border-radius: 8px;
  display: flex;
  margin-bottom: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.preview-sidebar {
  width: 30%;
  height: 100%;
}

.preview-content {
  width: 70%;
  height: 100%;
}

.classic-preview {
  background: #f0f2f5;
}
.classic-preview .preview-sidebar {
  background: #001529;
}
.classic-preview .preview-content {
  background: #f0f2f5;
}

.dark-purple-preview {
  background: #210124;
}
.dark-purple-preview .preview-sidebar {
  background: linear-gradient(180deg, rgba(33, 1, 36, 0.95) 0%, rgba(66, 13, 75, 0.92) 100%);
}
.dark-purple-preview .preview-content {
  background: linear-gradient(180deg, #210124 0%, #210635 100%);
}

.black-gold-preview {
  background: #1a011c;
}
.black-gold-preview .preview-sidebar {
  background: linear-gradient(180deg, rgba(33, 1, 36, 0.95) 0%, rgba(57, 79, 73, 0.92) 100%);
}
.black-gold-preview .preview-content {
  background: linear-gradient(135deg, #210124 0%, #1a011c 100%);
}

.github-preview {
  background: #f6f8fa;
}
.github-preview .preview-sidebar {
  background: #1b1f23;
}
.github-preview .preview-content {
  background: #f6f8fa;
}

.theme-name {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 6px;
}

.theme-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

/* 语言支持卡片 */
.lang-card {
  text-align: center;
  padding: 15px 10px;
}

.lang-desc {
  font-size: 12px;
  color: #606266;
  margin-top: 8px;
  line-height: 1.4;
}
</style>
