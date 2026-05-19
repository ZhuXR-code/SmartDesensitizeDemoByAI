import { createRouter, createWebHistory } from 'vue-router'
import ThemeLoader from '@/components/ThemeLoader.vue'

// 动态加载对应主题的 Layout
const Layout = () => import('@/components/ThemeLayout.vue')

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: ThemeLoader,
        props: { componentPath: 'Dashboard' },
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: 'workflow',
        name: 'Workflow',
        redirect: '/workflow/express',
        meta: { title: '快速脱敏', icon: 'Lightning' },
        children: [
          {
            path: 'express',
            name: 'WorkflowExpress',
            component: ThemeLoader,
            props: { componentPath: 'workflow/WorkflowExpress' },
            meta: { title: '快速脱敏工作流' }
          }
        ]
      },
      {
        path: 'datasets',
        name: 'Datasets',
        redirect: '/datasets/list',
        meta: { title: '数据集管理', icon: 'Document' },
        children: [
          {
            path: 'list',
            name: 'DatasetList',
            component: ThemeLoader,
            props: { componentPath: 'dataset/DatasetList' },
            meta: { title: '数据集列表' }
          },
          {
            path: 'upload',
            name: 'DatasetUpload',
            component: ThemeLoader,
            props: { componentPath: 'dataset/DatasetUpload' },
            meta: { title: '导入数据' }
          },
          {
            path: 'sources',
            name: 'DataSourceList',
            component: ThemeLoader,
            props: { componentPath: 'datasource/DataSourceList' },
            meta: { title: '数据源配置' }
          },
          {
            path: 'sources/manage',
            name: 'DataSourceManage',
            component: ThemeLoader,
            props: { componentPath: 'datasource/DataSourceManage' },
            meta: { title: '数据源管理', hidden: true }
          },
          {
            path: ':id',
            name: 'DatasetDetail',
            component: ThemeLoader,
            props: { componentPath: 'dataset/DatasetDetail' },
            meta: { title: '数据集详情', hidden: true }
          }
        ]
      },
      {
        path: 'detection',
        name: 'Detection',
        redirect: '/detection/rules',
        meta: { title: '敏感数据识别', icon: 'Search' },
        children: [
          {
            path: 'rules',
            name: 'DetectionRules',
            component: ThemeLoader,
            props: { componentPath: 'detection/RuleManage' },
            meta: { title: '识别规则管理' }
          },
          {
            path: 'tasks',
            name: 'DetectionTasks',
            component: ThemeLoader,
            props: { componentPath: 'detection/TaskList' },
            meta: { title: '识别任务' }
          },
          {
            path: 'tasks/create',
            name: 'CreateDetectionTask',
            component: ThemeLoader,
            props: { componentPath: 'detection/CreateTask' },
            meta: { title: '创建识别任务', hidden: true }
          },
          {
            path: 'tasks/:id',
            name: 'DetectionTaskDetail',
            component: ThemeLoader,
            props: { componentPath: 'detection/TaskDetail' },
            meta: { title: '任务详情', hidden: true }
          },
          {
            path: 'results',
            name: 'DetectionResults',
            component: ThemeLoader,
            props: { componentPath: 'detection/ResultList' },
            meta: { title: '识别结果' }
          },
          {
            path: 'rule-sets',
            name: 'DetectionRuleSets',
            component: ThemeLoader,
            props: { componentPath: 'detection/RuleSetManage' },
            meta: { title: '规则集管理' }
          },
        ]
      },
      {
        path: 'desensitization',
        name: 'Desensitization',
        redirect: '/desensitization/rules',
        meta: { title: '数据脱敏', icon: 'Lock' },
        children: [
          {
            path: 'rules',
            name: 'DesensitizationRules',
            component: ThemeLoader,
            props: { componentPath: 'desensitization/RuleManage' },
            meta: { title: '脱敏规则管理' }
          },
          {
            path: 'tasks',
            name: 'DesensitizationTasks',
            component: ThemeLoader,
            props: { componentPath: 'desensitization/TaskList' },
            meta: { title: '脱敏任务' }
          },
          {
            path: 'tasks/create',
            name: 'CreateDesensitizationTask',
            component: ThemeLoader,
            props: { componentPath: 'desensitization/CreateTask' },
            meta: { title: '创建脱敏任务', hidden: true }
          },
          {
            path: 'tasks/:id',
            name: 'DesensitizationTaskDetail',
            component: ThemeLoader,
            props: { componentPath: 'desensitization/TaskDetail' },
            meta: { title: '脱敏任务详情', hidden: true }
          }
        ]
      },
      {
        path: 'ai',
        name: 'Ai',
        redirect: '/ai/detection/tasks',
        meta: { title: 'AI智能', icon: 'Cpu' },
        children: [
          {
            path: 'config',
            name: 'AiConfig',
            component: ThemeLoader,
            props: { componentPath: 'ai/AiConfig' },
            meta: { title: 'AI配置管理' }
          },
          {
            path: 'detection',
            name: 'AiDetection',
            redirect: '/ai/detection/tasks',
            meta: { title: 'AI识别', icon: 'Cpu' },
            children: [
              {
                path: 'tasks',
                name: 'AiDetectionTasks',
                component: ThemeLoader,
                props: { componentPath: 'ai/AiDetection' },
                meta: { title: 'AI识别任务' }
              },
              {
                path: 'tasks/:id',
                name: 'AiDetectionTaskDetail',
                component: ThemeLoader,
                props: { componentPath: 'ai/AiDetection' },
                meta: { title: 'AI识别详情', hidden: true }
              }
            ]
          },
          {
            path: 'desensitization',
            name: 'AiDesensitization',
            redirect: '/ai/desensitization/tasks',
            meta: { title: 'AI脱敏', icon: 'Cpu' },
            children: [
              {
                path: 'tasks',
                name: 'AiDesensitizationTasks',
                component: ThemeLoader,
                props: { componentPath: 'desensitization/TaskList' },
                meta: { title: 'AI脱敏任务' }
              },
              {
                path: 'tasks/:id',
                name: 'AiDesensitizationTaskDetail',
                component: ThemeLoader,
                props: { componentPath: 'desensitization/TaskDetail' },
                meta: { title: 'AI脱敏详情', hidden: true }
              }
            ]
          }
        ]
      },
      {
        path: 'report',
        name: 'Report',
        redirect: '/report/platform',
        meta: { title: '运营报表', icon: 'TrendCharts' },
        children: [
          {
            path: 'platform',
            name: 'PlatformReport',
            component: ThemeLoader,
            props: { componentPath: 'report/PlatformReport' },
            meta: { title: '平台运营成效' }
          },
          {
            path: 'dashboard',
            name: 'ReportDashboard',
            component: ThemeLoader,
            props: { componentPath: 'report/ReportDashboard' },
            meta: { title: '规则校验报告', hidden: true }
          }
        ]
      },
      {
        path: 'help',
        name: 'Help',
        redirect: '/help/manual',
        meta: { title: '帮助中心', icon: 'QuestionFilled' },
        children: [
          {
            path: 'manual',
            name: 'UserManual',
            component: ThemeLoader,
            props: { componentPath: 'help/UserManual' },
            meta: { title: '用户操作手册' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
