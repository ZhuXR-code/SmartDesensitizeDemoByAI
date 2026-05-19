<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar" :class="{ 'sidebar-collapsed': isCollapse }">
      <div class="logo">
        <div class="logo-icon">
          <el-icon size="22"><Lock /></el-icon>
        </div>
        <span v-if="!isCollapse" class="logo-text">敏感信息脱敏平台</span>
      </div>

      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon>
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
      </div>

      <el-menu
        :default-active="activeMenu"
        router
        :collapse="isCollapse"
        :collapse-transition="true"
        class="sidebar-menu"
        background-color="transparent"
        text-color="#1d1d1f"
        active-text-color="#0071e3"
      >
        <el-menu-item index="/dashboard">
          <el-tooltip
            :disabled="!isCollapse"
            content="首页"
            placement="right"
            :show-arrow="false"
            :offset="12"
          >
            <div class="menu-icon-wrap">
              <el-icon><House /></el-icon>
            </div>
          </el-tooltip>
          <span>首页</span>
        </el-menu-item>

        <el-menu-item index="/workflow/express">
          <el-tooltip
            :disabled="!isCollapse"
            content="快速脱敏"
            placement="right"
            :show-arrow="false"
            :offset="12"
          >
            <div class="menu-icon-wrap">
              <el-icon><Lightning /></el-icon>
            </div>
          </el-tooltip>
          <span>快速脱敏</span>
        </el-menu-item>

        <el-sub-menu index="/datasets">
          <template #title>
            <el-icon><FolderOpened /></el-icon>
            <span>数据集管理</span>
          </template>
          <el-menu-item index="/datasets/list">数据集列表</el-menu-item>
          <el-menu-item index="/datasets/upload">导入数据</el-menu-item>
          <el-menu-item index="/datasets/sources">数据源配置</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/detection">
          <template #title>
            <el-icon><Search /></el-icon>
            <span>敏感数据识别</span>
          </template>
          <el-menu-item index="/detection/rules">识别规则管理</el-menu-item>
          <el-menu-item index="/detection/rule-sets">规则集管理</el-menu-item>
          <el-menu-item index="/detection/tasks">识别任务</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/desensitization">
          <template #title>
            <el-icon><Key /></el-icon>
            <span>数据脱敏</span>
          </template>
          <el-menu-item index="/desensitization/rules">脱敏规则管理</el-menu-item>
          <el-menu-item index="/desensitization/tasks">脱敏任务</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/ai">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>AI智能</span>
          </template>
          <el-menu-item index="/ai/detection">AI识别与脱敏</el-menu-item>
          <el-menu-item index="/ai/config">AI配置管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/report">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>运营报表</span>
          </template>
          <el-menu-item index="/report/platform">平台运营成效</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/help">
          <template #title>
            <el-icon><Help /></el-icon>
            <span>帮助中心</span>
          </template>
          <el-menu-item index="/help/manual">用户操作手册</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="breadcrumb">
          <el-breadcrumb>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-actions">
          <el-dropdown trigger="click" @command="handleThemeChange">
            <div class="theme-switcher">
              <el-icon size="16"><component :is="getThemeIcon()" /></el-icon>
              <span class="theme-label">{{ themeStore.currentThemeLabel }}</span>
              <el-icon size="12"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="theme in themeStore.themes"
                  :key="theme.key"
                  :command="theme.key"
                  :class="{ 'is-active': themeStore.currentTheme === theme.key }"
                >
                  <el-icon><component :is="theme.icon" /></el-icon>
                  <span>{{ theme.label }}</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <div class="user-info">
            <el-dropdown>
              <div class="user-profile">
                <div class="user-avatar">
                  <el-icon size="18"><UserFilled /></el-icon>
                </div>
                <span class="user-name">管理员</span>
                <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>
                    <el-icon><Setting /></el-icon> 个人设置
                  </el-dropdown-item>
                  <el-dropdown-item divided>
                    <el-icon><SwitchButton /></el-icon> 退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import {
  House, FolderOpened, Search, Key, DataAnalysis, Help,
  ArrowDown, Fold, Expand, UserFilled, Setting, SwitchButton,
  Sunny, Moon, Star, Connection, Lock, Cpu, Lightning
} from '@element-plus/icons-vue'

const route = useRoute()
const themeStore = useThemeStore()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

const currentTitle = computed(() => {
  return route.meta?.title || '敏感信息脱敏平台'
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const getThemeIcon = () => {
  const iconMap = {
    'classic': 'Sunny',
    'vue-classic': 'Connection',
    'dark-purple': 'Moon',
    'black-gold': 'Star'
  }
  return iconMap[themeStore.currentTheme] || 'Sunny'
}

const handleThemeChange = (themeKey) => {
  themeStore.setTheme(themeKey)
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #ffffff;
  color: #1d1d1f;
  transition: width 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e5e5ea;
}

.sidebar-collapsed {
  width: 64px !important;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  border-bottom: 1px solid #e5e5ea;
  white-space: nowrap;
  overflow: hidden;
  gap: 10px;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #0071e3;
}

.logo-text {
  margin-left: 0;
  font-size: 15px;
  font-weight: 600;
  transition: opacity 0.3s ease;
  color: #1d1d1f;
  letter-spacing: 0.3px;
}

.collapse-btn {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #86868b;
  border-bottom: 1px solid #d2d2d7;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  color: #0071e3;
  background-color: rgba(0, 113, 227, 0.06);
}

.collapse-btn .el-icon {
  font-size: 18px;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.menu-icon-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.sidebar-menu.el-menu--collapse {
  width: 64px;
}

:deep(.sidebar-menu) {
  .el-menu-item,
  .el-sub-menu .el-sub-menu__title {
    color: #1d1d1f !important;
    background-color: transparent !important;
    height: 44px;
    line-height: 44px;
    font-size: 14px;
    font-weight: 450;
    margin: 2px 8px;
    border-radius: 6px;
    width: auto;
    padding: 0 12px !important;
  }

  .el-menu-item:hover,
  .el-sub-menu .el-sub-menu__title:hover {
    background-color: rgba(0, 0, 0, 0.05) !important;
    color: #1d1d1f !important;
  }

  .el-menu-item.is-active {
    background-color: rgba(0, 113, 227, 0.1) !important;
    color: #0071e3 !important;
    font-weight: 500;
    border-right: none;
  }

  .el-sub-menu.is-active .el-sub-menu__title {
    color: #0071e3 !important;
    font-weight: 500;
  }

  .el-menu-item .el-icon,
  .el-sub-menu .el-sub-menu__title .el-icon {
    font-size: 18px;
    margin-right: 8px;
    color: inherit;
  }
}

.el-sub-menu .el-menu {
  background-color: transparent !important;
}

:deep(.el-sub-menu .el-menu) {
  .el-menu-item {
    padding-left: 44px !important;
    font-size: 13px;
    margin: 1px 8px;
  }
}

.header {
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #d2d2d7;
  box-shadow: none;
  height: 56px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #f5f5f7;
  border: 1px solid #d2d2d7;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #1d1d1f;
  font-size: 13px;
}

.theme-switcher:hover {
  background: #eaeaea;
  border-color: #bfbfc3;
}

.theme-label {
  font-weight: 500;
}

.user-info .user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-info .user-profile:hover {
  background: #f5f5f7;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0071e3, #34c759);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.dropdown-arrow {
  color: #86868b;
  font-size: 12px;
}

.main-content {
  background-color: #f5f5f7;
  padding: 24px;
  overflow-y: auto;
}

.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background-color: #c7c7cc;
  border-radius: 2px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background-color: #aeaeb2;
}
</style>
