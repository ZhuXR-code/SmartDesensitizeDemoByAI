<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar" :class="{ 'sidebar-collapsed': isCollapse }">
      <div class="logo">
        <div class="logo-icon">
          <el-icon size="22"><Lock /></el-icon>
        </div>
        <span v-if="!isCollapse" class="logo-text">敏感信息脱敏平台</span>
      </div>

      <!-- 装饰线 -->
      <div class="sidebar-divider" v-if="themeStore.isDarkTheme"></div>

      <!-- 折叠按钮 -->
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
        :background-color="themeStore.isDarkTheme ? 'transparent' : '#001529'"
        :text-color="themeStore.isDarkTheme ? 'rgba(239,221,141,0.85)' : '#bfcbd9'"
        :active-text-color="themeStore.isDarkTheme ? '#F4FDAF' : '#409EFF'"
      >
        <el-menu-item index="/dashboard">
          <el-tooltip
            :disabled="!isCollapse"
            content="首页"
            placement="right"
            :show-arrow="false"
            :offset="12"
            popper-class="sidebar-tooltip-glass"
          >
            <div class="menu-icon-wrap">
              <el-icon><HomeFilled /></el-icon>
            </div>
          </el-tooltip>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu index="/datasets">
          <template #title>
            <el-icon><Document /></el-icon>
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
            <el-icon><Lock /></el-icon>
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
            <el-icon><TrendCharts /></el-icon>
            <span>运营报表</span>
          </template>
          <el-menu-item index="/report/platform">平台运营成效</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/help">
          <template #title>
            <el-icon><QuestionFilled /></el-icon>
            <span>帮助中心</span>
          </template>
          <el-menu-item index="/help/manual">用户操作手册</el-menu-item>
        </el-sub-menu>
      </el-menu>

      <!-- 底部装饰 -->
      <div v-if="!isCollapse && themeStore.isDarkTheme" class="sidebar-footer">
        <div class="footer-glass"></div>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="breadcrumb">
          <el-breadcrumb>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-actions">
          <!-- 主题切换 -->
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

          <!-- 用户信息 -->
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
  HomeFilled, Document, Search, Lock, ArrowDown, QuestionFilled,
  Fold, Expand, TrendCharts, UserFilled, Setting, SwitchButton,
  Sunny, Moon, Star, Cpu
} from '@element-plus/icons-vue'

const route = useRoute()
const themeStore = useThemeStore()

// 侧边栏折叠状态
const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

const currentTitle = computed(() => {
  return route.meta?.title || '敏感信息脱敏平台'
})

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 获取当前主题图标
const getThemeIcon = () => {
  const iconMap = {
    'classic': 'Sunny',
    'dark-purple': 'Moon',
    'black-gold': 'Star'
  }
  return iconMap[themeStore.currentTheme] || 'Sunny'
}

// 处理主题切换
const handleThemeChange = (themeKey) => {
  themeStore.setTheme(themeKey)
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #001529;
  color: #fff;
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  border-bottom: 1px solid rgba(255,255,255,0.1);
  white-space: nowrap;
  overflow: hidden;
  gap: 10px;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-text {
  margin-left: 0;
  font-size: 16px;
  font-weight: 600;
  transition: opacity 0.3s ease;
}

/* 装饰线 */
.sidebar-divider {
  height: 1px;
  margin: 0 20px;
  background: linear-gradient(90deg, transparent, rgba(244, 253, 175, 0.15), transparent);
}

/* 折叠按钮 */
.collapse-btn {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #bfcbd9;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  color: #409EFF;
  background-color: rgba(64, 158, 255, 0.1);
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

/* 菜单图标包装器（用于tooltip定位） */
.menu-icon-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* 菜单折叠时的样式 */
.sidebar-menu.el-menu--collapse {
  width: 64px;
}

.header {
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 主题切换器 */
.theme-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(64, 158, 255, 0.08);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.25s ease;
  color: #409EFF;
  font-size: 13px;
}

.theme-switcher:hover {
  background: rgba(64, 158, 255, 0.15);
  border-color: rgba(64, 158, 255, 0.35);
}

.theme-label {
  font-weight: 500;
}

/* 用户信息 */
.user-info {
  .user-profile {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 9999px;
    cursor: pointer;
    transition: all 0.25s ease;
  }

  .user-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }

  .user-name {
    font-size: 13px;
    font-weight: 500;
    color: #606266;
  }

  .dropdown-arrow {
    color: #909399;
    font-size: 12px;
  }
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 底部装饰 */
.sidebar-footer {
  padding: 16px;
  position: relative;
}

.footer-glass {
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(244, 253, 175, 0.08) 0%, rgba(239, 221, 141, 0.04) 100%);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(244, 253, 175, 0.08);
  position: relative;
  overflow: hidden;
}

/* 滚动条样式 */
.sidebar-menu::-webkit-scrollbar {
  width: 6px;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.3);
}
</style>
