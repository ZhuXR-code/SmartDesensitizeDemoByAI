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
