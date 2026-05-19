<template>
  <el-container class="layout-container">
    <!-- 玻璃质感侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar" :class="{ 'sidebar-collapsed': isCollapse }">
      <div class="logo">
        <div class="logo-icon">
          <el-icon size="22"><Lock /></el-icon>
        </div>
        <span v-if="!isCollapse" class="logo-text">敏感信息脱敏平台</span>
      </div>

      <!-- 装饰线 -->
      <div class="sidebar-divider"></div>

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
        background-color="transparent"
        text-color="rgba(239,221,141,0.85)"
        active-text-color="#F4FDAF"
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

        <el-menu-item index="/workflow/express">
          <el-tooltip
            :disabled="!isCollapse"
            content="快速脱敏"
            placement="right"
            :show-arrow="false"
            :offset="12"
            popper-class="sidebar-tooltip-glass"
          >
            <div class="menu-icon-wrap">
              <el-icon><Lightning /></el-icon>
            </div>
          </el-tooltip>
          <span>快速脱敏</span>
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
      <div v-if="!isCollapse" class="sidebar-footer">
        <div class="footer-glass"></div>
      </div>
    </el-aside>

    <el-container>
      <!-- 玻璃质感顶部导航 -->
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

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="slide-up" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { HomeFilled, Document, Lock, ArrowDown, QuestionFilled, Fold, Expand, TrendCharts, UserFilled, Setting, SwitchButton, Sunny, Moon, Star, Connection, Cpu, Lightning } from '@element-plus/icons-vue'

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
    'vue-classic': 'Connection',
    'dark-purple': 'Moon',
    'black-gold': 'Star'
  }
  return iconMap[themeStore.currentTheme] || 'Sunny'
}

// 切换主题
const handleThemeChange = (themeKey) => {
  themeStore.setTheme(themeKey)
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

// 玻璃质感侧边栏 - 青苔紫夜色系
.sidebar {
  background:
    linear-gradient(180deg, rgba(33, 1, 36, 0.95) 0%, rgba(57, 79, 73, 0.92) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  color: #EFDD8D;
  transition: width 0.35s cubic-bezier(0.22, 1, 0.36, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);

  // 顶部高光
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(244, 253, 175, 0.3), transparent);
    z-index: 10;
  }
}

.sidebar-collapsed {
  width: 64px !important;
}

// Logo区域
.logo {
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  white-space: nowrap;
  overflow: hidden;
  gap: 10px;
}

.logo-icon {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(244, 253, 175, 0.3) 0%, rgba(239, 221, 141, 0.15) 100%);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #F4FDAF;
  border: 1px solid rgba(244, 253, 175, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  flex-shrink: 0;
}

.logo-text {
  font-size: 15px;
  font-weight: 600;
  color: rgba(244, 253, 175, 0.95);
  letter-spacing: 0.5px;
  transition: opacity 0.3s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

// 装饰线
.sidebar-divider {
  height: 1px;
  margin: 0 20px;
  background: linear-gradient(90deg, transparent, rgba(244, 253, 175, 0.15), transparent);
}

// 折叠按钮
.collapse-btn {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(239, 221, 141, 0.6);
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  margin: 8px 16px;
  border-radius: 10px;

  &:hover {
    color: rgba(244, 253, 175, 0.95);
    background: rgba(244, 253, 175, 0.1);
    backdrop-filter: blur(8px);
  }

  .el-icon {
    font-size: 18px;
  }
}

// 菜单样式
.sidebar-menu {
  border-right: none;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;

  :deep(.el-menu-item) {
    height: 46px;
    line-height: 46px;
    margin: 4px 10px !important;
    padding-left: 12px !important;
    border-radius: 10px !important;
    transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);

    &:hover {
      background: rgba(244, 253, 175, 0.08) !important;
      transform: translateX(2px);
    }

    &.is-active {
      background: linear-gradient(135deg, rgba(244, 253, 175, 0.2) 0%, rgba(239, 221, 141, 0.12) 100%) !important;
      backdrop-filter: blur(12px);
      box-shadow: inset 0 1px 0 rgba(244, 253, 175, 0.1), 0 2px 8px rgba(0, 0, 0, 0.2);
      border: 1px solid rgba(244, 253, 175, 0.15);

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 20px;
        background: linear-gradient(180deg, #F4FDAF, #EFDD8D);
        border-radius: 0 3px 3px 0;
      }
    }

    .el-icon {
      font-size: 18px;
      margin-right: 10px;
      color: rgba(239, 221, 141, 0.85);
    }

    &.is-active .el-icon {
      color: #F4FDAF;
    }
  }

  :deep(.el-sub-menu__title) {
    height: 46px;
    line-height: 46px;
    margin: 4px 10px !important;
    padding-left: 12px !important;
    padding-right: 30px !important;
    border-radius: 10px !important;
    transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
    color: rgba(239, 221, 141, 0.85) !important;

    &:hover {
      background: rgba(244, 253, 175, 0.08) !important;
      transform: translateX(2px);
    }

    .el-icon {
      font-size: 18px;
      margin-right: 10px;
      color: rgba(239, 221, 141, 0.85);
    }

    // 调整箭头位置
    .el-sub-menu__icon-arrow {
      right: 10px !important;
      color: rgba(239, 221, 141, 0.6) !important;
    }
  }

  :deep(.el-sub-menu .el-menu-item) {
    height: 40px;
    line-height: 40px;
    font-size: 13px;
    padding-left: 48px !important;
    color: rgba(239, 221, 141, 0.7) !important;

    &:hover {
      color: rgba(244, 253, 175, 0.95) !important;
    }

    &.is-active {
      background: rgba(244, 253, 175, 0.12) !important;
      color: #F4FDAF !important;
    }
  }
}

// 菜单图标包装器（用于tooltip定位）
.menu-icon-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

// 菜单折叠时的样式
.sidebar-menu.el-menu--collapse {
  width: 64px;

  :deep(.el-menu-item), :deep(.el-sub-menu__title) {
    justify-content: center;
    padding: 0 !important;
    margin: 4px 10px !important;

    .el-icon {
      margin: 0;
      color: rgba(239, 221, 141, 0.85);
    }
  }

  /* 折叠时子菜单tooltip玻璃效果 */
  :deep(.el-sub-menu.is-active) {
    .el-sub-menu__title {
      background: linear-gradient(135deg, rgba(244, 253, 175, 0.2) 0%, rgba(239, 221, 141, 0.12) 100%) !important;
      border: 1px solid rgba(244, 253, 175, 0.15);
    }
  }
}

// 侧边栏Tooltip玻璃效果
:deep(.sidebar-tooltip-glass) {
  background: #210124 !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(244, 253, 175, 0.2) !important;
  border-radius: 10px !important;
  padding: 8px 14px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
  color: #EFDD8D !important;
  font-size: 13px !important;
  font-weight: 500 !important;

  .el-popper__arrow::before {
    background: #210124 !important;
    border: 1px solid rgba(244, 253, 175, 0.2) !important;
  }
}

// 折叠时弹出的子菜单面板样式
:deep(.el-menu--popup),
:deep(.el-popper.is-pure),
:deep(.el-menu--popup-container) {
  background: #210124 !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  border: 1px solid rgba(244, 253, 175, 0.15) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
  padding: 8px !important;
  min-width: 180px !important;

  // 子菜单项样式
  .el-menu-item {
    background: transparent !important;
    color: rgba(239, 221, 141, 0.85) !important;
    height: 40px !important;
    line-height: 40px !important;
    border-radius: 8px !important;
    margin: 4px 0 !important;
    padding: 0 16px !important;
    font-size: 13px !important;
    transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1) !important;

    &:hover {
      background: rgba(244, 253, 175, 0.08) !important;
      color: #F4FDAF !important;
    }

    &.is-active {
      background: linear-gradient(135deg, rgba(244, 253, 175, 0.2) 0%, rgba(239, 221, 141, 0.12) 100%) !important;
      color: #F4FDAF !important;
      border: 1px solid rgba(244, 253, 175, 0.15) !important;
    }
  }

  // 确保popper内容区域也是深色背景
  .el-popper__content,
  .el-menu {
    background: #210124 !important;
  }
}

// 底部装饰
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

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(244, 253, 175, 0.06) 0%, transparent 60%);
    animation: shimmer 4s ease-in-out infinite;
  }
}

@keyframes shimmer {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(10%, 10%); }
}

// 玻璃质感顶部导航 - 青苔紫夜色系
.header {
  background: rgba(57, 79, 73, 0.72);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(244, 253, 175, 0.1);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.2);
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.breadcrumb {
  :deep(.el-breadcrumb__item) {
    .el-breadcrumb__inner {
      color: rgba(239, 221, 141, 0.7);
      font-weight: 500;
      font-size: 14px;
    }
  }
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
  background: rgba(244, 253, 175, 0.08);
  border: 1px solid rgba(244, 253, 175, 0.2);
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.25s ease;
  color: #F4FDAF;
  font-size: 13px;
}

.theme-switcher:hover {
  background: rgba(244, 253, 175, 0.15);
  border-color: rgba(244, 253, 175, 0.35);
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
    background: rgba(33, 1, 36, 0.4);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(244, 253, 175, 0.1);
    border-radius: 9999px;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);

    &:hover {
      background: rgba(33, 1, 36, 0.6);
      border-color: rgba(244, 253, 175, 0.2);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
  }

  .user-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(244, 253, 175, 0.3) 0%, rgba(239, 221, 141, 0.2) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #F4FDAF;
  }

  .user-name {
    font-size: 13px;
    font-weight: 500;
    color: #EFDD8D;
  }

  .dropdown-arrow {
    color: rgba(239, 221, 141, 0.5);
    font-size: 12px;
  }
}

// 主内容区
.main-content {
  background: transparent;
  padding: 24px;
  overflow-y: auto;
}

// 滚动条样式
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background-color: rgba(244, 253, 175, 0.15);
  border-radius: 2px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background-color: rgba(244, 253, 175, 0.25);
}

// 页面切换动画
.slide-up-enter-active {
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.slide-up-leave-active {
  transition: all 0.2s ease;
}

.slide-up-leave-to {
  opacity: 0;
}
</style>

<!-- 全局样式 - 覆盖Element Plus弹出子菜单默认样式 -->
<style lang="scss">
.el-menu--popup,
.el-menu--popup-container,
.el-menu--popup .el-menu,
.el-menu--popup .el-popper__content {
  background: #210124 !important;
  border: none !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
  padding: 8px !important;

  .el-menu-item {
    background: transparent !important;
    color: rgba(239, 221, 141, 0.85) !important;
    height: 40px !important;
    line-height: 40px !important;
    border-radius: 8px !important;
    margin: 4px 0 !important;
    padding: 0 16px !important;
    font-size: 13px !important;

    &:hover {
      background: rgba(244, 253, 175, 0.08) !important;
      color: #F4FDAF !important;
    }

    &.is-active {
      background: linear-gradient(135deg, rgba(244, 253, 175, 0.2) 0%, rgba(239, 221, 141, 0.12) 100%) !important;
      color: #F4FDAF !important;
      border: 1px solid rgba(244, 253, 175, 0.15) !important;
    }
  }
}

// 去掉popper外层的白色边框和背景
.el-popper.is-pure,
.el-menu--popper {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

// 下拉框全局样式优化 - 解决透明度过高导致文字看不清的问题
.el-select-dropdown,
.el-popper.is-select {
  background: #210124 !important;
  border: 1px solid rgba(244, 253, 175, 0.2) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
  padding: 8px !important;

  .el-select-dropdown__item {
    background: transparent !important;
    color: rgba(239, 221, 141, 0.9) !important;
    font-size: 13px !important;
    padding: 0 16px !important;
    height: 36px !important;
    line-height: 36px !important;
    border-radius: 8px !important;
    margin: 2px 0 !important;

    &:hover {
      background: rgba(244, 253, 175, 0.08) !important;
      color: #F4FDAF !important;
    }

    &.selected {
      background: rgba(244, 253, 175, 0.12) !important;
      color: #F4FDAF !important;
      font-weight: 500 !important;
    }

    &.is-disabled {
      color: rgba(239, 221, 141, 0.3) !important;
      cursor: not-allowed !important;
    }
  }

  // 下拉框箭头
  .el-popper__arrow::before {
    background: #210124 !important;
    border: 1px solid rgba(244, 253, 175, 0.2) !important;
  }
}

// 下拉框输入框样式
.el-select .el-input__wrapper {
  background: rgba(33, 1, 36, 0.8) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(244, 253, 175, 0.15) !important;
  border-radius: 8px !important;
  box-shadow: none !important;

  &:hover {
    border-color: rgba(244, 253, 175, 0.3) !important;
  }

  &.is-focus {
    border-color: rgba(244, 253, 175, 0.4) !important;
    box-shadow: 0 0 0 1px rgba(244, 253, 175, 0.1) inset !important;
  }

  .el-input__inner {
    color: rgba(239, 221, 141, 0.9) !important;
    
    &::placeholder {
      color: rgba(239, 221, 141, 0.4) !important;
    }
  }
}

// 级联选择器、日期选择器等下拉面板
.el-cascader-menu,
.el-picker-panel,
.el-date-picker,
.el-time-picker {
  background: #210124 !important;
  border: 1px solid rgba(244, 253, 175, 0.2) !important;
  border-radius: 12px !important;

  .el-cascader-node,
  .el-date-table td,
  .el-time-panel__content {
    color: rgba(239, 221, 141, 0.9) !important;
    
    &:hover {
      background: rgba(244, 253, 175, 0.08) !important;
    }
  }
}
</style>
