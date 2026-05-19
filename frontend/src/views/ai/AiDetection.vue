 <template>
  <div class="ai-detection">
    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon size="18" style="vertical-align: middle; margin-right: 6px;"><Search /></el-icon>
                AI 智能识别
              </span>
              <div>
                <el-tag v-if="!hasConfig" type="danger" effect="dark" size="small">未配置AI</el-tag>
                <el-tag v-else type="success" effect="light" size="small">已就绪</el-tag>
              </div>
            </div>
          </template>

          <el-form :model="detectForm" label-width="120px">
            <el-form-item label="任务名称" required>
              <el-input v-model="detectForm.name" placeholder="例如：AI智能识别-客户信息表" />
            </el-form-item>
            <el-form-item label="选择数据集" required>
              <el-select v-model="detectForm.dataset_id" placeholder="请选择要识别的数据集" style="width: 100%" filterable>
                <el-option v-for="ds in datasets" :key="ds.id" :label="ds.name" :value="ds.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="选择模型">
              <div style="display: flex; gap: 8px; width: 100%;">
                <el-select v-model="detectForm.ai_config_id" placeholder="留空使用默认配置" style="flex: 1;" filterable clearable>
                  <el-option v-for="c in aiConfigs" :key="c.id" :label="(c.alias || '未命名') + ' (' + c.provider + '/' + c.model_name + ')' + (c.is_active ? ' [默认]' : '')" :value="c.id" />
                </el-select>
                <el-button :loading="testLoading" @click="testConfig(detectForm.ai_config_id)" :disabled="!detectForm.ai_config_id">测试</el-button>
              </div>
              <div class="form-tip">选择已配置的AI模型，不选则使用默认配置</div>
            </el-form-item>
            <el-form-item label="DeepSeek思考模式" v-if="isDeepSeekModel">
              <el-switch v-model="detectForm.enable_thinking" active-text="开启（深度推理）" inactive-text="关闭（快速响应）" />
              <div class="form-tip">开启后DeepSeek会进行深度思考，适合复杂分析；关闭后响应更快，适合简单识别</div>
            </el-form-item>
            <el-form-item label="联网搜索">
              <el-switch v-model="detectForm.enable_web_search" active-text="开启（参考监管法规）" inactive-text="关闭（仅模型知识）" />
              <div class="form-tip">开启后AI会联网参考人行、金监等机构的最新敏感数据标准</div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleStartDetection" :loading="detecting" :disabled="!hasConfig" size="large">
                <el-icon><Cpu /></el-icon> 开始AI智能识别
              </el-button>
              <el-button @click="$router.push('/ai/config')" size="large">
                <el-icon><Setting /></el-icon> AI设置
              </el-button>
            </el-form-item>
          </el-form>

          <el-divider />

          <div v-if="!hasConfig" class="config-warning">
            <el-alert title="请先配置AI模型" description="在使用AI智能识别前，请先在AI设置中配置API密钥和模型" type="warning" show-icon :closable="false">
              <template #actions>
                <el-button type="primary" size="small" @click="$router.push('/ai/config')">前往配置</el-button>
              </template>
            </el-alert>
          </div>
        </el-card>

        <el-card style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon size="18" style="vertical-align: middle; margin-right: 6px;"><TrendCharts /></el-icon>
                检测任务列表
              </span>
              <div style="display: flex; gap: 8px;">
                <el-button size="small" @click="loadDetectionTasks" :loading="loadingTasks">刷新</el-button>
                <el-button size="small" type="danger" @click="clearAllTasks" :disabled="detectionTasks.length === 0">清空</el-button>
              </div>
            </div>
          </template>
          <el-table :data="detectionTasks" stripe style="width: 100%" v-loading="loadingTasks">
            <el-table-column prop="name" label="任务名称" min-width="120" show-overflow-tooltip />
            <el-table-column prop="dataset_name" label="数据集" min-width="150" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small" effect="light">{{ statusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="140">
              <template #default="{ row }">
                <el-progress :percentage="row.progress || 0" :stroke-width="6" />
              </template>
            </el-table-column>
            <el-table-column prop="found_count" label="发现" width="70" align="center" />
            <el-table-column label="操作" width="80" fixed="right" align="center">
              <template #default="{ row }">
                <el-tooltip content="查看详情" placement="top">
                  <el-button size="small" link @click="viewDetectionDetail(row)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip v-if="row.status === 'running'" content="打断任务" placement="top">
                  <el-button size="small" link type="danger" @click="cancelTask(row)" :loading="cancellingId === row.id">
                    <el-icon><CircleClose /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip v-if="row.status !== 'running'" content="删除任务" placement="top">
                  <el-button size="small" link type="danger" @click="deleteDetectionTask(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingTasks && detectionTasks.length === 0" description="暂无检测任务" :image-size="60" />

          <div v-if="lastCompletedTask" class="inline-preview" style="margin-top: 12px; padding: 12px; background: #f6f8fa; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span style="font-weight: 600; font-size: 14px;">📋 最新检测结果预览 — {{ lastCompletedTask.name }}</span>
              <el-button size="small" @click="viewDetectionDetail(lastCompletedTask)">查看全部</el-button>
            </div>
            <el-table :data="lastCompletedTask.previewResults || []" size="small" max-height="200" stripe>
              <el-table-column prop="row_index" label="行号" width="60" align="center" />
              <el-table-column prop="column_name" label="列名" width="100" show-overflow-tooltip />
              <el-table-column prop="original_value" label="原始值" min-width="120" show-overflow-tooltip />
              <el-table-column prop="sensitive_type" label="类型" width="100" show-overflow-tooltip />
              <el-table-column prop="confidence" label="置信度" width="80" align="center">
                <template #header>
                  <el-tooltip placement="top" effect="light">
                    <template #content>
                      <div style="max-width: 250px; line-height: 1.6;">
                        <strong>置信度说明：</strong><br/>
                        AI模型对检测结果的可信程度<br/>
                        • 90%-100%：高度确信<br/>
                        • 70%-89%：比较确信<br/>
                        • 50%-69%：一般确信<br/>
                        • <50%：较低确信，建议人工复核
                      </div>
                    </template>
                    <span style="cursor: help;">置信度 <el-icon><QuestionFilled /></el-icon></span>
                  </el-tooltip>
                </template>
                <template #default="{ row }">
                  <span :style="{ color: row.confidence > 0.8 ? '#f56c6c' : '#e6a23c' }">{{ (row.confidence * 100).toFixed(0) }}%</span>
                </template>
              </el-table-column>
              <el-table-column prop="risk_level" label="风险" width="80" align="center">
                <template #header>
                  <el-tooltip placement="top" effect="light">
                    <template #content>
                      <div style="max-width: 250px; line-height: 1.6;">
                        <strong>风险等级说明：</strong><br/>
                        • high：高风险，建议立即处理<br/>
                        • moderate：中风险，建议尽快处理<br/>
                        • low：低风险，可以稍后处理
                      </div>
                    </template>
                    <span style="cursor: help;">风险 <el-icon><QuestionFilled /></el-icon></span>
                  </el-tooltip>
                </template>
                <template #default="{ row }">
                  <el-tag :type="riskType(row.risk_level)" size="small">{{ row.risk_level }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon size="18" style="vertical-align: middle; margin-right: 6px;"><Lock /></el-icon>
                AI 脱敏
              </span>
            </div>
          </template>

          <el-form :model="desensitizeForm" label-width="110px">
            <el-form-item label="选择检测任务" required>
              <el-select v-model="desensitizeForm.detection_task_id" placeholder="选择已完成的检测任务" style="width: 100%" filterable>
                <el-option v-for="t in completedTasks" :key="t.id" :label="t.name" :value="t.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="任务名称" required>
              <el-input v-model="desensitizeForm.name" placeholder="脱敏任务名称" />
            </el-form-item>
            <el-form-item label="选择模型">
              <div style="display: flex; gap: 8px; width: 100%;">
                <el-select v-model="desensitizeForm.ai_config_id" placeholder="留空使用默认配置" style="flex: 1;" filterable clearable>
                  <el-option v-for="c in aiConfigs" :key="c.id" :label="(c.alias || '未命名') + ' (' + c.provider + '/' + c.model_name + ')' + (c.is_active ? ' [默认]' : '')" :value="c.id" />
                </el-select>
                <el-button :loading="testLoading" @click="testConfig(desensitizeForm.ai_config_id)" :disabled="!desensitizeForm.ai_config_id">测试</el-button>
              </div>
              <div class="form-tip">选择已配置的AI模型，不选则使用默认配置（仅仿真造数模式需要）</div>
            </el-form-item>
            <el-form-item label="脱敏模式" required>
              <el-radio-group v-model="desensitizeForm.mode" class="desensitize-mode-group">
                <el-radio value="mask" border>
                  <div><strong>定长遮盖</strong></div>
                  <div style="font-size: 12px; color: #909399;">按数据类型智能遮盖，如手机号138****8000，姓名张*</div>
                </el-radio>
                <el-radio value="synthetic" border>
                  <div><strong>仿真造数</strong></div>
                  <div style="font-size: 12px; color: #909399;">AI 生成语义一致的仿真数据，保持数据格式和真实性</div>
                </el-radio>
                <el-radio value="correlated_synthetic" border>
                  <div><strong>关联仿真造数</strong></div>
                  <div style="font-size: 12px; color: #909399;">AI 生成具有关联性的仿真数据，同一个人的多个字段保持一致性</div>
                </el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="danger" @click="handleStartDesensitization" :loading="desensitizing" :disabled="!desensitizeForm.detection_task_id" size="large" style="width: 100%;">
                <el-icon><Lock /></el-icon> 执行脱敏
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon size="18" style="vertical-align: middle; margin-right: 6px;"><DataLine /></el-icon>
                脱敏任务
              </span>
              <div style="display: flex; gap: 8px;">
                <el-button size="small" @click="loadDesensitizationTasks" :loading="loadingDesTasks">刷新</el-button>
                <el-button size="small" type="danger" @click="clearAllDesTasks" :disabled="desensitizationTasks.length === 0">清空</el-button>
              </div>
            </div>
          </template>
          <el-table :data="desensitizationTasks" stripe style="width: 100%" v-loading="loadingDesTasks">
            <el-table-column prop="name" label="任务" min-width="80" show-overflow-tooltip />
            <el-table-column prop="mode" label="模式" width="100">
              <template #default="{ row }">
                <el-tag 
                  :type="row.mode === 'mask' ? 'primary' : (row.mode === 'synthetic' ? 'warning' : 'success')" 
                  size="small"
                >
                  {{ row.mode === 'mask' ? '遮盖' : (row.mode === 'synthetic' ? '仿真' : '关联仿真') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="70">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.progress || 0" :stroke-width="6" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-tooltip content="查看详情" placement="top">
                  <el-button size="small" link @click="viewDesensitizationDetail(row)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="删除任务" placement="top">
                  <el-button size="small" link type="danger" @click="deleteDesensitizationTask(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingDesTasks && desensitizationTasks.length === 0" description="暂无脱敏任务" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="detailVisible" :title="detailTitle" width="90%" top="5vh" @close="handleDialogClose">
      <template v-if="detailType === 'detection' && detailData">
        <!-- 任务信息头部 -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="margin: 0;">任务信息</h3>
          <div style="display: flex; gap: 8px; align-items: center;">
            <el-tag v-if="detailData.task.status === 'running'" type="warning" effect="dark">
              <el-icon class="is-loading"><Loading /></el-icon>
              处理中...
            </el-tag>
            <el-tag v-else-if="detailData.task.status === 'completed'" type="success" effect="dark">
              <el-icon><CircleCheck /></el-icon>
              已完成
            </el-tag>
            <el-tag v-else-if="detailData.task.status === 'failed'" type="danger" effect="dark">
              <el-icon><CircleClose /></el-icon>
              已失败
            </el-tag>
            <el-tag v-else-if="detailData.task.status === 'cancelled'" type="info" effect="dark">
              <el-icon><CircleClose /></el-icon>
              已取消
            </el-tag>
            <el-button 
              size="small" 
              @click="refreshDetail" 
              :loading="refreshing"
              :disabled="detailData.task.status !== 'running'"
            >
              <el-icon><Refresh /></el-icon>
              {{ detailData.task.status === 'running' ? '刷新状态' : '刷新' }}
            </el-button>
            <el-switch 
              v-if="detailData.task.status === 'running'"
              v-model="autoRefresh" 
              active-text="自动刷新"
              inactive-text="手动刷新"
              @change="toggleAutoRefresh"
            />
          </div>
        </div>

        <!-- 失败提示 -->
        <el-alert 
          v-if="detailData.task.status === 'failed' && detailData.task.error_message" 
          :title="'任务失败: ' + detailData.task.error_message" 
          type="error" 
          :closable="false"
          show-icon
          style="margin-bottom: 16px;"
        />

        <el-descriptions :column="2" border style="margin-bottom: 16px;">
          <el-descriptions-item label="任务名称">{{ detailData.task.name }}</el-descriptions-item>
          <el-descriptions-item label="数据集">{{ detailData.task.dataset_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detailData.task.status)" size="small">{{ statusText(detailData.task.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="耗时">{{ detailData.task.duration_seconds || '-' }} 秒</el-descriptions-item>
          <el-descriptions-item label="总行数">{{ detailData.task.total_rows || 0 }}</el-descriptions-item>
          <el-descriptions-item label="检测数据量">
            <span v-if="detailData.task.total_rows">{{ detailData.task.total_rows }} 行</span>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="发现敏感数">
            <div style="display: flex; align-items: center; gap: 8px;">
              <el-tag type="danger" effect="dark" size="large">
                {{ detailData.results ? detailData.results.length : 0 }}
              </el-tag>
              <span v-if="detailData.task.found_count !== (detailData.results ? detailData.results.length : 0)" 
                    style="font-size: 12px; color: #909399;">
                （数据库: {{ detailData.task.found_count || 0 }}）
              </span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="联网搜索" :span="2">
            <el-tag :type="detailData.task.enable_web_search ? 'success' : 'info'" size="small">
              {{ detailData.task.enable_web_search ? '已开启' : '未开启' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="detailData.task.result_summary" style="margin-bottom: 16px;">
          <h4 style="margin: 0 0 8px;">检测统计</h4>
          <el-row :gutter="12">
            <el-col :span="6">
              <el-statistic title="高风险" :value="detailData.task.result_summary.high_risk_count || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="中风险" :value="detailData.task.result_summary.moderate_risk_count || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="低风险" :value="detailData.task.result_summary.low_risk_count || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="类型数" :value="Object.keys(detailData.task.result_summary.type_distribution || {}).length" />
            </el-col>
          </el-row>
        </div>

        <h4 style="margin: 0 0 8px;">检测结果详情</h4>
        <!-- 批量操作按钮 -->
        <div v-if="detailData.results.length > 0" style="margin-bottom: 12px; display: flex; gap: 8px; align-items: center;">
          <el-checkbox v-model="selectAll" @change="handleSelectAll">全选</el-checkbox>
          <span style="color: #909399; font-size: 13px;">已选择 {{ selectedRows.length }} 条</span>
          <el-button 
            size="small" 
            type="success" 
            :disabled="selectedRows.length === 0"
            @click="batchReview(true)"
          >
            <el-icon><CircleCheck /></el-icon> 批量采纳
          </el-button>
          <el-button 
            size="small" 
            type="info" 
            :disabled="selectedRows.length === 0"
            @click="batchReview(false)"
          >
            <el-icon><CircleClose /></el-icon> 批量不采纳
          </el-button>
        </div>
        <el-table 
          :data="detailData.results" 
          stripe 
          max-height="400" 
          v-if="detailData.results.length > 0"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="50" />
          <el-table-column prop="row_index" label="行号" width="60" />
          <el-table-column prop="column_name" label="列名" width="100" />
          <el-table-column prop="original_value" label="原始值" min-width="100" show-overflow-tooltip />
          <el-table-column prop="sensitive_type" label="敏感类型" width="110" />
          <el-table-column prop="confidence" label="置信度" width="90">
            <template #header>
              <el-tooltip placement="top" effect="light">
                <template #content>
                  <div style="max-width: 250px; line-height: 1.6;">
                    <strong>置信度说明：</strong><br/>
                    AI模型对检测结果的可信程度<br/>
                    • 90%-100%：高度确信<br/>
                    • 70%-89%：比较确信<br/>
                    • 50%-69%：一般确信<br/>
                    • <50%：较低确信，建议人工复核
                  </div>
                </template>
                <span style="cursor: help;">置信度 <el-icon><QuestionFilled /></el-icon></span>
              </el-tooltip>
            </template>
            <template #default="{ row }">
              <el-tag :type="row.confidence > 0.8 ? 'danger' : 'warning'" size="small">
                {{ (row.confidence * 100).toFixed(0) }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="risk_level" label="风险" width="80">
            <template #default="{ row }">
              <el-tag :type="riskType(row.risk_level)" size="small">{{ row.risk_level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="regulation_ref" label="法规依据" min-width="130" show-overflow-tooltip />
          <el-table-column prop="reviewed" label="复核状态" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.reviewed" :type="row.review_result ? 'danger' : 'success'" size="small">
                {{ row.review_result ? '已复核(敏感)' : '已复核(非敏)' }}
              </el-tag>
              <el-tag v-else type="info" size="small">未复核</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-popover placement="left" :width="300" trigger="click">
                <template #reference>
                  <el-button size="small" link>推理</el-button>
                </template>
                <div style="font-size: 13px; line-height: 1.6; white-space: pre-wrap;">{{ row.llm_reasoning || '无' }}</div>
              </el-popover>
              <el-button v-if="!row.reviewed || row.review_result !== true" size="small" link type="success" @click="handleReview(row, true)">采纳</el-button>
              <el-button v-if="!row.reviewed || row.review_result !== false" size="small" link type="info" @click="handleReview(row, false)">不采纳</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂未发现敏感数据" :image-size="60" />

        <div style="margin-top: 16px; text-align: right; display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="exportDetection(detailData.task.id)" type="primary" plain>
            <el-icon><Download /></el-icon> 导出Excel
          </el-button>
          <el-button @click="generateReport(detailData.task.id, 'html')" :loading="reportLoading" type="success" plain>
            <el-icon><Document /></el-icon> HTML报告
          </el-button>
          <el-button @click="generateReport(detailData.task.id, 'markdown')" :loading="reportLoading" type="info" plain>
            <el-icon><Document /></el-icon> Markdown
          </el-button>
          <el-button v-if="lastReportPath" @click="previewLastReport" type="warning" plain>
            <el-icon><View /></el-icon> 预览报告
          </el-button>
        </div>
      </template>

      <template v-if="detailType === 'desensitization' && detailData">
        <!-- 任务信息头部 -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="margin: 0;">任务信息</h3>
          <div style="display: flex; gap: 8px; align-items: center;">
            <el-tag v-if="detailData.task.status === 'running'" type="warning" effect="dark">
              <el-icon class="is-loading"><Loading /></el-icon>
              处理中...
            </el-tag>
            <el-tag v-else-if="detailData.task.status === 'completed'" type="success" effect="dark">
              <el-icon><CircleCheck /></el-icon>
              已完成
            </el-tag>
            <el-tag v-else-if="detailData.task.status === 'failed'" type="danger" effect="dark">
              <el-icon><CircleClose /></el-icon>
              已失败
            </el-tag>
            <el-tag v-else-if="detailData.task.status === 'cancelled'" type="info" effect="dark">
              <el-icon><CircleClose /></el-icon>
              已取消
            </el-tag>
            <el-button 
              size="small" 
              @click="refreshDetail" 
              :loading="refreshing"
              :disabled="detailData.task.status !== 'running'"
            >
              <el-icon><Refresh /></el-icon>
              {{ detailData.task.status === 'running' ? '刷新状态' : '刷新' }}
            </el-button>
            <el-switch 
              v-if="detailData.task.status === 'running'"
              v-model="autoRefresh" 
              active-text="自动刷新"
              inactive-text="手动刷新"
              @change="toggleAutoRefresh"
            />
          </div>
        </div>

        <el-descriptions :column="2" border style="margin-bottom: 16px;">
          <el-descriptions-item label="任务名称">{{ detailData.task.name }}</el-descriptions-item>
          <el-descriptions-item label="模式">
            <el-tag 
              :type="detailData.task.mode === 'mask' ? 'primary' : (detailData.task.mode === 'synthetic' ? 'warning' : 'success')" 
              size="small"
            >
              {{ detailData.task.mode === 'mask' ? '定长遮盖' : (detailData.task.mode === 'synthetic' ? '仿真造数' : '关联仿真造数') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detailData.task.status)" size="small">{{ statusText(detailData.task.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="耗时">{{ detailData.task.duration_seconds || '-' }} 秒</el-descriptions-item>
          <el-descriptions-item label="处理数">{{ detailData.task.processed_rows || 0 }}</el-descriptions-item>
          <el-descriptions-item label="输出文件">
            <el-button v-if="detailData.task.output_file_path || detailData.task.output_file_pure_path" size="small" link type="primary" @click="showDownloadDialog">
              下载
            </el-button>
            <span v-else>-</span>
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin: 0 0 8px;">脱敏结果</h4>
        <el-table :data="detailData.results" stripe max-height="400">
          <el-table-column prop="row_index" label="行号" width="60" />
          <el-table-column prop="column_name" label="列名" width="100" />
          <el-table-column prop="original_value" label="原始值" min-width="140" show-overflow-tooltip />
          <el-table-column prop="desensitized_value" label="脱敏后" min-width="140" show-overflow-tooltip>
            <template #default="{ row }">
              <span style="color: #e6a23c; font-weight: 500;">{{ row.desensitized_value }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="method" label="方法" width="100">
            <template #default="{ row }">
              <el-tag 
                :type="row.method === 'mask' ? 'primary' : (row.method === 'synthetic' ? 'warning' : 'success')" 
                size="small"
              >
                {{ row.method === 'mask' ? '遮盖' : (row.method === 'synthetic' ? '仿真' : '关联仿真') }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 16px; text-align: right; display: flex; gap: 10px; justify-content: flex-end;">
          <el-button v-if="detailData.task.output_file_path || detailData.task.output_file_pure_path" size="small" link type="primary" @click="showDownloadDialog">
            <el-icon><Download /></el-icon> 下载Excel
          </el-button>
          <el-button @click="generateDesensitizationReport(detailData.task.id, 'html')" :loading="reportLoading" type="success" plain size="small">
            <el-icon><Document /></el-icon> HTML报告
          </el-button>
          <el-button @click="generateDesensitizationReport(detailData.task.id, 'markdown')" :loading="reportLoading" type="info" plain size="small">
            <el-icon><Document /></el-icon> Markdown
          </el-button>
          <el-button v-if="lastReportPath" @click="previewLastReport" type="warning" plain size="small">
            <el-icon><View /></el-icon> 预览报告
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 下载格式选择对话框 -->
    <el-dialog v-model="downloadDialogVisible" title="选择下载格式" width="500px">
      <div style="padding: 10px;">
        <p style="margin-bottom: 16px;">请选择要下载的脱敏文件格式：</p>
        
        <el-radio-group v-model="downloadFormat" style="display: flex; flex-direction: column; gap: 12px;">
          <el-radio value="compare" border style="width: 100%; padding: 12px;">
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <span style="font-weight: 600;">对比数据文件</span>
              <span style="font-size: 12px; color: #909399;">包含原始值和脱敏后值的对比，方便审核和验证</span>
            </div>
          </el-radio>
          
          <el-radio value="pure" border style="width: 100%; padding: 12px;">
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <span style="font-weight: 600;">纯脱敏文件</span>
              <span style="font-size: 12px; color: #909399;">只包含脱敏后的数据，可直接使用</span>
            </div>
          </el-radio>
        </el-radio-group>
      </div>
      
      <template #footer>
        <el-button @click="downloadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmDownload" :disabled="!downloadFormat">
          <el-icon><Download /></el-icon> 下载
        </el-button>
      </template>
    </el-dialog>

    <!-- 报告预览对话框 -->
    <el-dialog v-model="reportPreviewVisible" :title="reportPreviewTitle" width="90%" top="5vh">
      <iframe 
        v-if="reportPreviewUrl" 
        :src="reportPreviewUrl" 
        style="width: 100%; height: 70vh; border: none;"
        frameborder="0"
      ></iframe>
      <el-empty v-else description="报告加载中..." />
      <template #footer>
        <el-button @click="reportPreviewVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadReportFile">
          <el-icon><Download /></el-icon> 下载报告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAiDetectionTasks, createAiDetectionTask, getAiDetectionTaskDetail, exportAiDetectionResults,
  getAiDesensitizationTasks, createAiDesensitizationTask, getAiDesensitizationTaskDetail,
  getAiConfig, getAiConfigs, testAiConnection, cancelAiDetectionTask, clearAiDetectionTasks, deleteAiDetectionTask,
  generateHtmlReport, generateMarkdownReport,
  generateDesensitizationHtmlReport, generateDesensitizationMarkdownReport,
  clearAiDesensitizationTasks, deleteAiDesensitizationTask,
  reviewDetectionResult, getReviewStats
} from '@/api/ai'
import { getDatasetList } from '@/api/dataset'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import { Search, Cpu, Setting, TrendCharts, Lock, DataLine, Download, Document, Refresh, Loading, CircleCheck, CircleClose, QuestionFilled, View, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const hasConfig = ref(false)
const aiConfigs = ref([])
const datasets = ref([])
const detectionTasks = ref([])
const desensitizationTasks = ref([])
const testLoading = ref(false)
const reportLoading = ref(false)
const lastReportPath = ref('')
const lastCompletedTask = ref(null)

const completedTasks = computed(() => detectionTasks.value.filter(t => t.status === 'completed' && t.found_count > 0))

const detectForm = ref({ name: '', dataset_id: null, ai_config_id: null, enable_web_search: false, enable_thinking: false })
const desensitizeForm = ref({ name: '', detection_task_id: null, mode: 'mask', ai_config_id: null, output_format: 'xlsx' })

const detecting = ref(false)
const desensitizing = ref(false)
const loadingTasks = ref(false)
const loadingDesTasks = ref(false)
const activeTab = ref('detection')

const detailVisible = ref(false)
const detailType = ref('detection')
const detailTitle = ref('')
const detailData = ref(null)
const cancellingId = ref(null)  // 正在取消的任务ID
const refreshing = ref(false)  // 刷新中
const autoRefresh = ref(false)  // 自动刷新开关
const refreshTimer = ref(null)  // 定时器
const listRefreshTimer = ref(null)  // 列表定时器
const task = ref({})
const results = ref([])
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)

// 下载格式选择相关
const downloadDialogVisible = ref(false)
const downloadFormat = ref('compare')

// 批量操作相关
const selectAll = ref(false)
const selectedRows = ref([])

// 报告预览相关
const reportPreviewVisible = ref(false)
const reportPreviewTitle = ref('')
const reportPreviewUrl = ref('')
const currentReportPath = ref('')

const statusType = (s) => ({ completed: 'success', running: 'warning', pending: 'info', failed: 'danger', cancelled: 'info' }[s] || 'info')
const statusText = (s) => ({ completed: '完成', running: '处理中', pending: '等待', failed: '失败', cancelled: '已取消' }[s] || s)
const riskType = (r) => ({ high: 'danger', moderate: 'warning', low: 'info' }[r] || 'info')

// 判断当前选择的模型是否为 DeepSeek
const isDeepSeekModel = computed(() => {
  if (!detectForm.value.ai_config_id) return false
  const config = aiConfigs.value.find(c => c.id === detectForm.value.ai_config_id)
  return config?.provider === 'deepseek'
})

const loadDetectionTasks = async () => {
  loadingTasks.value = true
  try {
    const res = await getAiDetectionTasks()
    detectionTasks.value = res.data || []
    const completed = detectionTasks.value.filter(t => t.status === 'completed' && t.found_count > 0)
    if (completed.length > 0) {
      const latest = completed[0]
      if (!lastCompletedTask.value || lastCompletedTask.value.id !== latest.id) {
        try {
          const detail = await getAiDetectionTaskDetail(latest.id)
          latest.previewResults = (detail.data?.results || []).slice(0, 20)
        } catch { latest.previewResults = [] }
      }
      lastCompletedTask.value = latest
    }
  } catch { detectionTasks.value = []
  } finally { loadingTasks.value = false }
}

// 加载详情数据（兼容路由参数）
  const loadDetailFromRoute = async () => {
    const taskId = route.query.taskId || route.params.taskId
    if (taskId) {
      try {
        const res = await getAiDetectionTaskDetail(taskId)
        detailData.value = res.data
        detailType.value = 'detection'
        detailTitle.value = `检测详情 - ${res.data.task.name}`
        detailVisible.value = true
        
        if (res.data.task.status === 'running') {
          autoRefresh.value = true
          startAutoRefresh(taskId)
        }
      } catch { ElMessage.error('获取详情失败') }
    }
  }
  
  const loadDesensitizationTasks = async () => {
  loadingDesTasks.value = true
  try {
    const res = await getAiDesensitizationTasks()
    desensitizationTasks.value = res.data || []
  } catch { desensitizationTasks.value = []
  } finally { loadingDesTasks.value = false }
}

const handleStartDetection = async () => {
  if (!detectForm.value.name || !detectForm.value.dataset_id) {
    ElMessage.warning('请填写任务名称并选择数据集')
    return
  }
  detecting.value = true
  try {
    await createAiDetectionTask(detectForm.value)
    ElMessage.success('AI检测任务已创建，正在后台运行')
    detectForm.value.name = ''
    detectForm.value.dataset_id = null
    await loadDetectionTasks()
  } catch (e) {
    ElMessage.error('创建失败: ' + (e.message || ''))
  } finally { detecting.value = false }
}

const handleStartDesensitization = async () => {
  if (!desensitizeForm.value.name || !desensitizeForm.value.detection_task_id) {
    ElMessage.warning('请填写任务名称并选择检测任务')
    return
  }
  desensitizing.value = true
  try {
    await createAiDesensitizationTask(desensitizeForm.value)
    ElMessage.success('脱敏任务已创建，正在后台运行')
    desensitizeForm.value = { name: '', detection_task_id: null, mode: 'mask', ai_config_id: null }
    await loadDesensitizationTasks()
  } catch (e) {
    ElMessage.error('创建失败: ' + (e.message || ''))
  } finally { desensitizing.value = false }
}

const viewDetectionDetail = async (row) => {
  try {
    const res = await getAiDetectionTaskDetail(row.id)
    detailData.value = res.data
    detailType.value = 'detection'
    detailTitle.value = `检测详情 - ${res.data.task.name}`
    detailVisible.value = true
    
    // 如果任务正在运行，自动开启刷新
    if (row.status === 'running') {
      autoRefresh.value = true
      startAutoRefresh(row.id)
    }
  } catch { ElMessage.error('获取详情失败') }
}

// 刷新详情
const refreshDetail = async () => {
  if (!detailData.value || detailType.value !== 'detection') return
  
  refreshing.value = true
  try {
    const taskId = detailData.value.task.id
    const res = await getAiDetectionTaskDetail(taskId)
    detailData.value = res.data
    
    // 如果任务已完成/失败/取消，停止自动刷新
    if (['completed', 'failed', 'cancelled'].includes(res.data.task.status)) {
      stopAutoRefresh()
      autoRefresh.value = false
      
      // 刷新任务列表
      await loadDetectionTasks()
      
      if (res.data.task.status === 'completed') {
        ElMessage.success('任务已完成')
      } else if (res.data.task.status === 'failed') {
        ElMessage.error('任务执行失败')
      } else if (res.data.task.status === 'cancelled') {
        ElMessage.info('任务已取消')
      }
    } else if (res.data.task.status === 'running') {
      ElMessage.success('状态已刷新')
    }
  } catch (e) {
    ElMessage.error('刷新失败: ' + (e.message || ''))
  } finally {
    refreshing.value = false
  }
}

// 开启自动刷新
const startAutoRefresh = (taskId) => {
  stopAutoRefresh() // 先清除之前的定时器
  
  refreshTimer.value = setInterval(async () => {
    if (!detailVisible.value || detailType.value !== 'detection') {
      stopAutoRefresh()
      return
    }
    
    try {
      const res = await getAiDetectionTaskDetail(taskId)
      detailData.value = res.data
      
      // 如果任务已结束，停止自动刷新
      if (['completed', 'failed', 'cancelled'].includes(res.data.task.status)) {
        stopAutoRefresh()
        autoRefresh.value = false
        await loadDetectionTasks()
        
        if (res.data.task.status === 'completed') {
          ElMessage.success('任务已完成')
        } else if (res.data.task.status === 'failed') {
          ElMessage.error('任务执行失败')
        } else if (res.data.task.status === 'cancelled') {
          ElMessage.info('任务已取消')
        }
      }
    } catch (e) {
      console.error('自动刷新失败:', e)
      // 不显示错误提示，避免打扰用户
    }
  }, 3000) // 每3秒刷新一次
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

// 切换自动刷新
const toggleAutoRefresh = (value) => {
  if (value && detailData.value?.task?.id) {
    startAutoRefresh(detailData.value.task.id)
  } else {
    stopAutoRefresh()
  }
}

// 开启列表自动刷新
const startListAutoRefresh = () => {
  stopListAutoRefresh() // 先清除之前的定时器
  
  listRefreshTimer.value = setInterval(async () => {
    try {
      const res = await getAiDetectionTasks()
      detectionTasks.value = res.data || []
      
      // 如果没有正在运行的任务，停止自动刷新
      const hasRunningTask = detectionTasks.value.some(t => t.status === 'running')
      if (!hasRunningTask) {
        stopListAutoRefresh()
      }
    } catch (e) {
      console.error('列表自动刷新失败:', e)
    }
  }, 5000) // 每5秒刷新一次列表
}

// 停止列表自动刷新
const stopListAutoRefresh = () => {
  if (listRefreshTimer.value) {
    clearInterval(listRefreshTimer.value)
    listRefreshTimer.value = null
  }
}

const viewDesensitizationDetail = async (row) => {
  try {
    const res = await getAiDesensitizationTaskDetail(row.id)
    detailData.value = res.data
    detailType.value = 'desensitization'
    detailTitle.value = `脱敏详情 - ${res.data.task.name}`
    detailVisible.value = true
  } catch { ElMessage.error('获取详情失败') }
}

const exportDetection = async (taskId) => {
  try {
    const res = await exportAiDetectionResults(taskId)
    if (res.data?.file_path) {
      ElMessage.success('报表已生成')
    }
  } catch (e) {
    ElMessage.error('导出失败: ' + (e.message || ''))
  }
}

const generateReport = async (taskId, format) => {
  reportLoading.value = true
  try {
    const res = format === 'html' ? await generateHtmlReport(taskId) : await generateMarkdownReport(taskId)
    if (res.data?.file_path) {
      lastReportPath.value = res.data.file_path
      currentReportPath.value = res.data.file_path
      
      if (format === 'html') {
        // HTML报告可以直接预览
        reportPreviewTitle.value = '检测报告预览'
        const fname = res.data.file_path.replace(/\\/g, '/').split('/').pop()
        reportPreviewUrl.value = '/api/ai/report/' + fname + '/preview'
        reportPreviewVisible.value = true
        ElMessage.success('HTML报告已生成')
      } else {
        // Markdown下载报告
        ElMessage.success('Markdown报告已生成')
        const a = document.createElement('a')
        a.href = '/' + res.data.file_path.replace(/\\/g, '/')
        a.download = res.data.file_path.replace(/\\/g, '/').split('/').pop() || 'report.md'
        a.click()
      }
    }
  } catch (e) { ElMessage.error('报告生成失败: ' + (e.message || ''))
  } finally { reportLoading.value = false }
}

const generateDesensitizationReport = async (taskId, format) => {
  reportLoading.value = true
  try {
    const res = format === 'html' ? await generateDesensitizationHtmlReport(taskId) : await generateDesensitizationMarkdownReport(taskId)
    if (res.data?.file_path) {
      lastReportPath.value = res.data.file_path
      currentReportPath.value = res.data.file_path
      
      if (format === 'html') {
        // HTML报告可以直接预览
        reportPreviewTitle.value = '脱敏报告预览'
        const fname = res.data.file_path.replace(/\\/g, '/').split('/').pop()
        reportPreviewUrl.value = '/api/ai/report/' + fname + '/preview'
        reportPreviewVisible.value = true
        ElMessage.success('HTML脱敏报告已生成')
      } else {
        // Markdown下载报告
        ElMessage.success('Markdown脱敏报告已生成')
        const a = document.createElement('a')
        a.href = '/' + res.data.file_path.replace(/\\/g, '/')
        a.download = res.data.file_path.replace(/\\/g, '/').split('/').pop() || 'desensitization_report.md'
        a.click()
      }
    }
  } catch (e) { ElMessage.error('脱敏报告生成失败: ' + (e.message || ''))
  } finally { reportLoading.value = false }
}

// 下载报告文件
const downloadReportFile = () => {
  if (currentReportPath.value) {
    downloadFile(currentReportPath.value)
  }
}

const previewLastReport = () => {
  if (lastReportPath.value) {
    currentReportPath.value = lastReportPath.value
    reportPreviewTitle.value = '报告预览'
    const fname = lastReportPath.value.replace(/\\/g, '/').split('/').pop()
    reportPreviewUrl.value = '/api/ai/report/' + fname + '/preview'
    reportPreviewVisible.value = true
  }
}

const testConfig = async (configId) => {
  const cfg = aiConfigs.value.find(c => c.id === configId)
  if (!cfg) { ElMessage.warning('请选择配置'); return }
  testLoading.value = true
  try {
    const res = await testAiConnection(configId)
    if (res.data?.success) {
      ElMessage.success(res.data.message)
    } else {
      ElMessage.error(res.data?.message || '连接失败')
    }
  } catch (e) {
    ElMessage.error('测试异常: ' + (e.message || ''))
  } finally { testLoading.value = false }
}

// 取消/打断任务
const cancelTask = async (row) => {
  cancellingId.value = row.id
  try {
    await cancelAiDetectionTask(row.id)
    ElMessage.success('取消请求已提交，任务将在当前处理完成后停止')
    // 刷新任务列表
    await loadDetectionTasks()
  } catch (e) {
    ElMessage.error('取消失败: ' + (e.message || ''))
  } finally { cancellingId.value = null }
}

// 清空所有检测任务
const clearAllTasks = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有检测任务吗？此操作不可恢复！',
      '警告',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await clearAiDetectionTasks()
    ElMessage.success('已清空所有检测任务')
    await loadDetectionTasks()
    await loadDesensitizationTasks()
  } catch {
    ElMessage.error('清空失败')
  }
}

const clearAllDesTasks = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有脱敏任务吗？此操作不可恢复！',
      '清空确认',
      { confirmButtonText: '确定清空', cancelButtonText: '取消', type: 'warning' }
    )
    await clearAiDesensitizationTasks()
    ElMessage.success('已清空所有脱敏任务')
    await loadDesensitizationTasks()
  } catch { /* cancelled */ }
}

// 删除单个检测任务
const deleteDetectionTask = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除检测任务 "${row.name}" 吗？此操作将同时删除该任务的所有检测结果，不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteAiDetectionTask(row.id)
    ElMessage.success(`已删除任务 "${row.name}"`)
    await loadDetectionTasks()
    await loadDesensitizationTasks()
  } catch {
    // 用户取消或删除失败
  }
}

// 删除单个脱敏任务
const deleteDesensitizationTask = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除脱敏任务 "${row.name}" 吗？此操作将同时删除该任务的所有脱敏结果，不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteAiDesensitizationTask(row.id)
    ElMessage.success(`已删除任务 "${row.name}"`)
    await loadDesensitizationTasks()
  } catch {
    // 用户取消或删除失败
  }
}

const downloadFile = (path) => {
  const a = document.createElement('a')
  a.href = '/' + path.replace(/\\/g, '/')
  a.download = path.split('/').pop() || 'download'
  a.click()
}

// 人工复核检测结果
const handleReview = async (row, reviewResult) => {
  try {
    await ElMessageBox.confirm(
      reviewResult 
        ? `确定将此条数据标记为“敏感数据”吗？脱敏时将对此数据进行脱敏处理。`
        : `确定将此条数据标记为“非敏感数据”吗？脱敏时将不对此数据进行脱敏处理。`,
      '确认复核',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: reviewResult ? 'warning' : 'info'
      }
    )
    
    const res = await reviewDetectionResult(row.id, {
      review_result: reviewResult,
      review_reason: '用户人工复核'
    })
    
    ElMessage.success('复核成功')
    
    // 刷新详情
    if (detailData.value && detailData.value.task) {
      await refreshDetail()
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('复核失败: ' + (e.message || ''))
    }
  }
}

// 全选/取消全选
const handleSelectAll = (val) => {
  if (val) {
    // 全选未复核的行
    selectedRows.value = detailData.value.results.filter(r => !r.reviewed)
  } else {
    selectedRows.value = []
  }
}

// 表格选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  selectAll.value = selectedRows.value.length === detailData.value.results.filter(r => !r.reviewed).length
}

// 批量复核
const batchReview = async (reviewResult) => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要复核的数据')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      reviewResult 
        ? `确定将选中的 ${selectedRows.value.length} 条数据标记为“敏感数据”吗？`
        : `确定将选中的 ${selectedRows.value.length} 条数据标记为“非敏感数据”吗？`,
      '批量复核确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: reviewResult ? 'warning' : 'info'
      }
    )
    
    let successCount = 0
    let failCount = 0
    
    for (const row of selectedRows.value) {
      try {
        await reviewDetectionResult(row.id, {
          review_result: reviewResult,
          review_reason: '用户批量复核'
        })
        successCount++
      } catch (e) {
        console.error('复核失败:', e)
        failCount++
      }
    }
    
    if (failCount === 0) {
      ElMessage.success(`批量复核成功，共 ${successCount} 条`)
    } else {
      ElMessage.warning(`批量复核完成，成功 ${successCount} 条，失败 ${failCount} 条`)
    }
    
    // 清空选择
    selectedRows.value = []
    selectAll.value = false
    
    // 刷新详情
    if (detailData.value && detailData.value.task) {
      await refreshDetail()
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量复核失败: ' + (e.message || ''))
    }
  }
}

// 显示下载格式选择对话框
const showDownloadDialog = () => {
  downloadFormat.value = 'compare' // 默认选择对比文件
  downloadDialogVisible.value = true
}

// 确认下载
const confirmDownload = () => {
  if (!detailData.value?.task) return
  
  let filePath = ''
  if (downloadFormat.value === 'compare') {
    filePath = detailData.value.task.output_file_path
  } else if (downloadFormat.value === 'pure') {
    filePath = detailData.value.task.output_file_pure_path
  }
  
  if (!filePath) {
    ElMessage.warning('该文件不存在')
    return
  }
  
  downloadFile(filePath)
  downloadDialogVisible.value = false
}

// 监听对话框关闭，清理定时器
const handleDialogClose = () => {
  stopAutoRefresh()
  autoRefresh.value = false
  detailData.value = null
}

onMounted(async () => {
  try {
    const cfg = await getAiConfig()
    hasConfig.value = cfg.data?.has_key || false
  } catch { hasConfig.value = false }
  try {
    const cfgList = await getAiConfigs()
    aiConfigs.value = cfgList.data || []
  } catch { aiConfigs.value = [] }
  try {
    const ds = await getDatasetList()
    datasets.value = ds.data?.items || []
  } catch { datasets.value = [] }
  await loadDetectionTasks()
  await loadDesensitizationTasks()
  
  // 检查是否有任务ID参数，如果有则显示详情
  const taskId = route.query.taskId || route.params.taskId
  if (taskId) {
    await loadDetailFromRoute()
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoRefresh()
  stopListAutoRefresh()
})
</script>

<style scoped>
.ai-detection {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.config-warning {
  margin-top: 12px;
}

.desensitize-mode-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.desensitize-mode-group .el-radio {
  display: flex;
  width: 100%;
  margin-right: 0;
  height: auto;
  padding: 10px 14px;
  align-items: flex-start;
  white-space: normal;
  line-height: 1.5;
}

.desensitize-mode-group .el-radio .el-radio__label {
  display: block;
  width: 100%;
  padding-left: 4px;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .ai-detection {
    padding: 8px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start !important;
  }
  
  .el-form {
    label-width: 90px !important;
  }
  
  .el-table {
    font-size: 12px;
  }
  
  .inline-preview {
    overflow-x: auto;
  }
}

@media (max-width: 576px) {
  .ai-detection {
    padding: 4px;
  }
  
  .el-button--large {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .desensitize-mode-group .el-radio {
    padding: 8px 10px;
  }
}
</style>
