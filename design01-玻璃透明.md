我来为你分析这种"液态玻璃"(Liquid Glass)设计风格，并输出完整的设计文档。

一、风格特点分析

维度 特征描述

核心材质 透明玻璃质感 + 微磨砂效果 + 高光反射

色彩 浅灰/纯白背景 + 低饱和蓝色点缀 + 柔光阴影

形状 大圆角(Round Corners)、胶囊型(Pills)、全圆角矩形

光影 顶部/左上高光、底部柔和投影、边缘渐变过渡

层次 多层玻璃叠加、半透明蒙版、微妙模糊背景

字体 无衬线字体(Sans-serif)、中等字重、清晰易读

交互 柔和反馈、状态切换有颜色流动感

二、设计文档 (Design System)

2.1 命名规范


风格名称：Liquid Glass / 液态玻璃
版本：v1.0
适用平台：PC Web端
技术栈：Vue 3 + CSS/SCSS + 可选：Tailwind CSS


2.2 色彩系统

// 主色调
$primary-blue: #B8D4E3;      // 主蓝，用于激活/主要按钮
$primary-blue-light: #E3F0F7; // 浅蓝，用于背景/悬停

// 中性色
$white: #FFFFFF;
$glass-white: rgba(255, 255, 255, 0.85); // 玻璃白，带透明度
$gray-50: #F9FAFB;
$gray-100: #F3F4F6;
$gray-200: #E5E7EB;
$gray-300: #D1D5DB;

// 深色文本
$text-primary: #1F2937;      // 主文本
$text-secondary: #6B7280;    // 次要文本

// 阴影系统
$shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
$shadow-soft: 0 4px 16px 0 rgba(0, 0, 0, 0.08);
$shadow-subtle: 0 2px 8px 0 rgba(0, 0, 0, 0.04);

// 边框/分割
$border-glass: 1px solid rgba(255, 255, 255, 0.6);
$border-subtle: 1px solid rgba(0, 0, 0, 0.05);


2.3 字体规范

$font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
              'Helvetica Neue', Arial, sans-serif;

// 字重
$font-weight-regular: 400;
$font-weight-medium: 500;
$font-weight-semibold: 600;

// 字号
$font-size-xs: 0.75rem;   // 12px
$font-size-sm: 0.875rem;  // 14px
$font-size-base: 1rem;    // 16px
$font-size-lg: 1.125rem;  // 18px
$font-size-xl: 1.25rem;   // 20px
$font-size-2xl: 1.5rem;   // 24px


2.4 圆角系统

$radius-none: 0;
$radius-sm: 0.375rem;     // 6px
$radius-md: 0.5rem;       // 8px
$radius-lg: 0.75rem;      // 12px
$radius-xl: 1rem;         // 16px
$radius-2xl: 1.5rem;      // 24px
$radius-full: 9999px;     // 全圆角/胶囊型


2.5 核心组件样式

2.5.1 玻璃卡片 (Glass Card)

<template>
  <div class="glass-card">
    <slot />
  </div>
</template>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 1rem;
  box-shadow: 
    0 8px 32px 0 rgba(31, 38, 135, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  padding: 1.5rem;
}
</style>


2.5.2 玻璃按钮 (Glass Button)

<template>
  <button 
    :class="[
      'glass-button',
      `glass-button--${variant}`,
      { 'glass-button--disabled': disabled }
    ]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'primary' }, // primary, secondary, text
  disabled: { type: Boolean, default: false }
})
</script>

<style scoped>
.glass-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 9999px; // 胶囊型
  border: 1px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #1F2937;
  cursor: pointer;
  transition: all 0.2s ease-out;
  box-shadow: 
    0 4px 16px 0 rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  
  &:hover {
    background: rgba(255, 255, 255, 0.95);
    transform: translateY(-1px);
    box-shadow: 
      0 6px 20px 0 rgba(0, 0, 0, 0.12),
      inset 0 1px 0 rgba(255, 255, 255, 0.9);
  }
  
  &:active {
    transform: translateY(0);
    box-shadow: 
      0 2px 8px 0 rgba(0, 0, 0, 0.06),
      inset 0 1px 0 rgba(255, 255, 255, 0.7);
  }
}

.glass-button--primary {
  background: linear-gradient(135deg, #B8D4E3 0%, #D4E4ED 100%);
  color: #1F2937;
  border: 1px solid rgba(184, 212, 227, 0.8);
  
  &:hover {
    background: linear-gradient(135deg, #C2DAE8 0%, #DEEAF0 100%);
  }
}

.glass-button--secondary {
  background: rgba(255, 255, 255, 0.6);
  color: #4B5563;
  
  &:hover {
    background: rgba(255, 255, 255, 0.8);
    color: #1F2937;
  }
}
</style>


2.5.3 玻璃输入框 (Glass Input)

<template>
  <div class="glass-input-wrapper">
    <input
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      :type="type"
      class="glass-input"
    />
    <!-- 图标插槽 -->
    <span v-if="$slots.icon" class="glass-input__icon">
      <slot name="icon" />
    </span>
  </div>
</template>

<script setup>
defineProps({
  modelValue: String,
  placeholder: String,
  type: { type: String, default: 'text' }
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.glass-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.glass-input {
  width: 100%;
  padding: 0.75rem 1rem;
  padding-right: 2.5rem; // 为图标预留空间
  font-family: inherit;
  font-size: 0.875rem;
  color: #1F2937;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 0.75rem;
  box-shadow: 
    inset 0 1px 2px 0 rgba(0, 0, 0, 0.03),
    0 2px 8px 0 rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease-out;
  
  &::placeholder {
    color: #9CA3AF;
  }
  
  &:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.9);
    border-color: rgba(184, 212, 227, 0.8);
    box-shadow: 
      inset 0 1px 2px 0 rgba(0, 0, 0, 0.05),
      0 4px 12px 0 rgba(184, 212, 227, 0.2);
  }
}

.glass-input__icon {
  position: absolute;
  right: 0.75rem;
  color: #9CA3AF;
  pointer-events: none;
}
</style>


2.5.4 玻璃开关 (Glass Switch)

<template>
  <label class="glass-switch">
    <input 
      type="checkbox" 
      :checked="modelValue"
      @change="$emit('update:modelValue', $event.target.checked)"
      class="glass-switch__input"
    />
    <span class="glass-switch__slider"></span>
  </label>
</template>

<script setup>
defineProps({ modelValue: Boolean })
defineEmits(['update:modelValue'])
</script>

<style scoped>
.glass-switch {
  position: relative;
  display: inline-block;
  width: 3.5rem;
  height: 2rem;
  cursor: pointer;
}

.glass-switch__input {
  opacity: 0;
  width: 0;
  height: 0;
  
  &:checked + .glass-switch__slider {
    background: linear-gradient(135deg, #B8D4E3 0%, #D4E4ED 100%);
    border-color: rgba(184, 212, 227, 0.8);
    
    &:before {
      transform: translateX(1.5rem);
      background: white;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
  }
}

.glass-switch__slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 9999px;
  transition: all 0.3s ease-out;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
  
  &:before {
    position: absolute;
    content: "";
    height: 1.5rem;
    width: 1.5rem;
    left: 0.25rem;
    bottom: 0.25rem;
    background: white;
    border-radius: 50%;
    transition: all 0.3s ease-out;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
}
</style>


2.5.5 玻璃下拉选择 (Glass Select)

<template>
  <div class="glass-select-wrapper">
    <select 
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="glass-select"
    >
      <option 
        v-for="option in options" 
        :key="option.value" 
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    <span class="glass-select__arrow">▼</span>
  </div>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  options: { type: Array, required: true }
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.glass-select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.glass-select {
  width: 100%;
  padding: 0.75rem 1rem;
  padding-right: 2.5rem;
  font-family: inherit;
  font-size: 0.875rem;
  color: #1F2937;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 0.75rem;
  box-shadow: 
    inset 0 1px 2px 0 rgba(0, 0, 0, 0.03),
    0 2px 8px 0 rgba(0, 0, 0, 0.04);
  appearance: none;
  cursor: pointer;
  transition: all 0.2s ease-out;
  
  &:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.9);
    border-color: rgba(184, 212, 227, 0.8);
    box-shadow: 
      inset 0 1px 2px 0 rgba(0, 0, 0, 0.05),
      0 4px 12px 0 rgba(184, 212, 227, 0.2);
  }
}

.glass-select__arrow {
  position: absolute;
  right: 1rem;
  color: #6B7280;
  pointer-events: none;
  font-size: 0.75rem;
}
</style>


2.5.6 玻璃标签栏 (Glass Tabs)

<template>
  <div class="glass-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      :class="['glass-tab', { active: modelValue === tab.value }]"
      @click="$emit('update:modelValue', tab.value)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  tabs: { type: Array, required: true }
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.glass-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 0.75rem;
  padding: 0.375rem;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.04);
}

.glass-tab {
  flex: 1;
  padding: 0.5rem 1rem;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6B7280;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease-out;
  
  &:hover {
    color: #1F2937;
    background: rgba(255, 255, 255, 0.5);
  }
  
  &.active {
    color: #1F2937;
    background: rgba(255, 255, 255, 0.9);
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  }
}
</style>


2.5.7 玻璃头像/用户信息 (Glass Profile)

<template>
  <div class="glass-profile">
    <div class="glass-profile__avatar">
      <img :src="avatar" :alt="name" />
    </div>
    <div class="glass-profile__info">
      <h3 class="glass-profile__name">{{ name }}</h3>
      <p class="glass-profile__title">{{ title }}
      <p class="glass-profile__bio">{{ bio }}
    </div>
    <div v-if="status" class="glass-profile__status">
      <span class="status-dot"></span>
      {{ status }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  avatar: { type: String, required: true },
  name: { type: String, required: true },
  title: { type: String, required: true },
  bio: { type: String, required: true },
  status: String
})
</script>

<style scoped>
.glass-profile {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 
    0 8px 32px 0 rgba(31, 38, 135, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.glass-profile__avatar {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.glass-profile__info {
  flex: 1;
}

.glass-profile__name {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1F2937;
}

.glass-profile__title {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #6B7280;
  font-weight: 500;
}

.glass-profile__bio {
  margin: 0;
  font-size: 0.875rem;
  color: #4B5563;
  line-height: 1.5;
}

.glass-profile__status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: rgba(184, 212, 227, 0.2);
  border: 1px solid rgba(184, 212, 227, 0.4);
  border-radius: 9999px;
  font-size: 0.75rem;
  color: #1F2937;
  font-weight: 500;
  
  .status-dot {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
  }
}
</style>


2.6 布局系统

// 容器
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

// 网格系统
.grid {
  display: grid;
  gap: 1.5rem;
  
  &.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  &.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  &.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}

// 间距
.gap-1 { gap: 0.5rem; }
.gap-2 { gap: 1rem; }
.gap-3 { gap: 1.5rem; }
.gap-4 { gap: 2rem; }

// 弹性布局
.flex {
  display: flex;
  
  &.flex-col { flex-direction: column; }
  &.items-center { align-items: center; }
  &.justify-between { justify-content: space-between; }
  &.gap-1 { gap: 0.5rem; }
  &.gap-2 { gap: 1rem; }
  &.gap-3 { gap: 1.5rem; }
}


2.7 响应式断点

$breakpoint-sm: 640px;
$breakpoint-md: 768px;
$breakpoint-lg: 1024px;
$breakpoint-xl: 1280px;

@media (max-width: $breakpoint-sm) {
  .container { padding: 1rem; }
  .grid-cols-3, .grid-cols-4 { grid-template-columns: 1fr; }
  .grid-cols-2 { grid-template-columns: 1fr; }
}

@media (min-width: $breakpoint-md) {
  .container { padding: 1.5rem; }
  .grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: $breakpoint-lg) {
  .grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
}

@media (min-width: $breakpoint-xl) {
  .container { padding: 2rem; }
  .grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}


2.8 全局样式

<!-- src/styles/global.scss -->
<template>
  <div id="app">
    <slot />
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  background: 
    radial-gradient(circle at 20% 20%, rgba(184, 212, 227, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(216, 226, 233, 0.1) 0%, transparent 50%),
    linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>


三、优化后的提示词

原始提示词

我要生成一个pc端的页面，类似于这种风格的，请分析风格特点 并且输出设计文档。这样我在生成我的平台前后端代码的时候，ai能依据这个文档生成类似这种特色风格的前端。我前端用的vue

优化后提示词


你是一位资深UI/UX设计师兼前端架构师，精通现代Web设计和Vue3生态系统。请帮我创建一个遵循"液态玻璃"(Liquid Glass)设计风格的PC端平台。

## 设计风格参考
请参考我提供的四张图片风格：
1. 个人资料卡片界面
2. 玻璃质感表单界面  
3. 各种玻璃按钮和控件
4. 完整的玻璃组件集合

## 核心风格特征分析
请从以下维度分析并提取设计系统：
- 色彩：主色调、辅助色、中性色、透明度运用
- 材质：玻璃质感、磨砂效果、高光、阴影层次
- 形状：圆角系统、胶囊型、全圆角矩形
- 光影：顶部高光、底部投影、渐变过渡
- 字体：字重、字号、行高、字间距
- 间距：网格系统、组件间距、页面留白

## 输出要求

### 1. 设计系统文档 (Design System)
用结构化方式输出：
- 色彩变量表 (CSS/SCSS变量，提供HEX和RGBA值)
- 字体规范 (font-family, font-size, font-weight)
- 圆角系统 (radius-sm, radius-md, radius-lg等)
- 阴影系统 (glass shadow, soft shadow, subtle shadow)
- 间距系统 (4px基准或8px基准)

### 2. 核心组件库
为每个基础组件提供：
- Vue3单文件组件代码 (SFC)
- 支持v-model双向绑定
- Props类型定义
- 基础样式 (使用<style scoped>，可配合SCSS)
- 悬停/激活/禁用等状态样式
- 响应式处理

必需组件列表：
- GlassCard (玻璃卡片)
- GlassButton (玻璃按钮 - 主按钮、次要按钮、文本按钮)
- GlassInput (玻璃输入框 - 支持前缀/后缀图标)
- GlassSelect (玻璃下拉选择)
- GlassSwitch (玻璃开关)
- GlassTabs (玻璃标签栏)
- GlassProfile (玻璃用户信息卡片)
- GlassModal (玻璃模态框 - 可选)

### 3. 布局系统
- 容器规范 (container)
- 网格系统 (grid, flex)
- 响应式断点 (mobile, tablet, desktop)
- 间距工具类 (gap utilities)

### 4. 全局样式
- 根元素背景样式 (radial-gradient或linear-gradient)
- 全局字体设置
- 基础重置样式

### 5. 使用示例
提供一个完整的页面示例，展示：
- 导航栏 (玻璃质感)
- 主内容区 (使用Grid布局，展示多个玻璃卡片)
- 交互状态演示 (按钮悬停、输入框聚焦、开关切换)

## 技术要求
- 使用Vue 3 Composition API + <script setup>
- 样式使用原生CSS或SCSS (推荐SCSS，方便主题化)
- 不依赖第三方UI库 (纯手写组件)
- 响应式设计 (移动端适配)
- 良好的代码注释和类型提示

## 输出格式
请用清晰的Markdown格式输出，包含：
- 标题层级分明
- 代码块使用正确的语言标记
- 组件代码完整可复制
- 提供可直接运行的main.vue入口文件示例


---
好，这里我会在不破坏你已有的「液态玻璃」风格的前提下，补充「动效系统」+「PC 端菜单栏」+「菜单卡片样式与动效」，并给你一份可直接给 AI 用的增强版提示词。  
你可以直接把它接在前面的设计文档后面用。

四、动效系统设计（Motion System）

目标：轻盈、通透、有呼吸感，不做夸张动画，保持“玻璃感”。

4.1 动效原则

原则 说明

轻量 位移 ≤ 8px，缩放 ≤ 1.05

快 入场 / 悬停：150–250ms

柔 使用 ease-out / spring 感

层次 背景不动，前景微动

不抢 不遮挡内容，不频繁闪烁

4.2 标准动效曲线（Easing）

$ease-out: cubic-bezier(0.22, 1, 0.36, 1);
$ease-in-out: cubic-bezier(0.42, 0, 0.58, 1);
$spring: cubic-bezier(0.34, 1.56, 0.64, 1);


4.3 通用动效 Token

// 时长
$duration-fast: 150ms;
$duration-base: 220ms;
$duration-slow: 350ms;

// 组合 token
@mixin glass-transition($props...) {
  transition: join($props, (), comma) $duration-base $ease-out;
}


4.4 推荐动效清单

场景 动效

按钮 hover 上浮 2px + 阴影增强

按钮 click 轻微缩放 0.97

卡片 hover 上浮 + 高光增强

菜单展开 淡入 + 向下微移

菜单项 hover 背景渐显 + 左高光线

开关切换 滑块弹簧位移

页面切换 fade + slide-up

加载 玻璃呼吸（opacity 变化）

五、PC 端菜单栏设计（Top Navigation Bar）

5.1 风格定位

• 玻璃条悬浮导航

• 不贴死顶部（悬浮感）

• Logo 左 / 菜单中 / 操作右

• 永远保持“像浮在桌面上的玻璃片”

5.2 玻璃菜单栏组件（Glass Navbar）

<template>
  <header class="glass-navbar">
    <div class="glass-navbar__inner container">
      <!-- Logo -->
      <div class="glass-navbar__logo">
        <span class="logo-text">Platform</span>
      </div>

      <!-- Menu -->
      <nav class="glass-navbar__menu">
        <ul class="menu-list">
          <li
            v-for="item in menu"
            :key="item.key"
            :class="['menu-item', { active: activeKey === item.key }]"
            @click="activeKey = item.key"
          >
            {{ item.label }}
          </li>
        </ul>
      </nav>

      <!-- Actions -->
      <div class="glass-navbar__actions">
        <GlassButton size="small">登录</GlassButton>
        <GlassButton size="small" variant="primary">注册</GlassButton>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import GlassButton from './GlassButton.vue'

const activeKey = ref('home')

const menu = [
  { key: 'home', label: '首页' },
  { key: 'explore', label: '探索' },
  { key: 'workspace', label: '工作台' },
  { key: 'settings', label: '设置' }
]
</script>

<style scoped lang="scss">
.glass-navbar {
  position: sticky;
  top: 1rem;
  z-index: 100;
  padding: 0 2rem;
}

.glass-navbar__inner {
  display: flex;
  align-items: center;
  height: 64px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: 1rem;
  box-shadow:
    0 8px 32px rgba(31, 38, 135, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  padding: 0 1.5rem;
  gap: 2rem;
}

/* Logo */
.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1F2937;
  letter-spacing: -0.02em;
}

/* Menu */
.menu-list {
  display: flex;
  gap: 0.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu-item {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6B7280;
  border-radius: 9999px;
  cursor: pointer;
  @include glass-transition(background, color, box-shadow);

  &:hover {
    background: rgba(255, 255, 255, 0.6);
    color: #1F2937;
  }

  &.active {
    background: rgba(184, 212, 227, 0.35);
    color: #1F2937;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  }
}

/* Actions */
.glass-navbar__actions {
  margin-left: auto;
  display: flex;
  gap: 0.75rem;
}
</style>


5.3 菜单栏动效说明

元素 动效

导航栏 页面滚动时 top 微调

菜单项 hover 背景淡入 + 文字加深

激活态 柔和蓝色背景 + 内高光

首次进入 淡入 + 向下 6px

六、菜单卡片（Menu Card / Dropdown Card）

用于：用户菜单 / 设置面板 / 二级菜单

6.1 玻璃菜单卡片组件

<template>
  <transition name="menu-dropdown">
    <div v-if="visible" class="glass-menu-card">
      <ul class="menu-card__list">
        <li
          v-for="item in items"
          :key="item.key"
          class="menu-card__item"
          @click="handleClick(item)"
        >
          <span class="menu-icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </li>
      </ul>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  visible: Boolean,
  items: Array
})

const emit = defineEmits(['select'])

const handleClick = (item) => {
  emit('select', item)
}
</script>

<style scoped lang="scss">
.glass-menu-card {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 200px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 1rem;
  box-shadow:
    0 12px 40px rgba(31, 38, 135, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  padding: 0.5rem;
  overflow: hidden;
}

.menu-card__list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu-card__item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  border-radius: 0.75rem;
  cursor: pointer;
  @include glass-transition(background, color);

  &:hover {
    background: rgba(184, 212, 227, 0.3);
    color: #1F2937;
  }

  .menu-icon {
    font-size: 1rem;
  }
}
</style>


6.2 菜单卡片动效（Vue Transition）

/* 下拉菜单动画 */
.menu-dropdown-enter-active {
  transition: all 220ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
.menu-dropdown-leave-active {
  transition: all 180ms ease-in;
}
.menu-dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}
.menu-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}


七、增强后的「AI 可用提示词」（✅ 强烈推荐）

你可以直接复制下面这段给 AI，让它按你这套系统生成页面

✅ 优化后的完整提示词（含动效 + 菜单）


你是一位资深 UI/UX 设计师 + Vue3 前端架构师，请基于「液态玻璃（Liquid Glass）」风格，为我构建一个 PC 端管理平台前端设计系统。

## 一、风格约束
- 材质：毛玻璃、半透明、柔和高光、轻阴影
- 色彩：浅灰 + 白色 + 低饱和蓝（#B8D4E3）
- 形状：大圆角、胶囊型、全圆角卡片
- 视觉层级：悬浮感、不贴边、不沉重

## 二、动效系统（必须实现）
请遵循以下动效规范：
- 动效时长：150–250ms
- 缓动曲线：cubic-bezier(0.22, 1, 0.36, 1)
- 禁止：剧烈位移、高频闪烁、夸张缩放
- 动效类型：
  - hover：上浮 2px + 阴影增强
  - click：scale(0.97)
  - 菜单展开：淡入 + 向下微移
  - 卡片 hover：背景高光增强
  - 开关：spring 弹簧位移

## 三、PC 端菜单栏设计
请实现：
1. 顶部玻璃导航栏（sticky，悬浮）
2. Logo 左 / 菜单居中 / 操作右
3. 菜单项支持激活态、hover 态
4. 导航栏使用 backdrop-filter + 玻璃阴影

## 四、菜单卡片（Dropdown / Popover）
- 玻璃质感下拉卡片
- 圆角 ≥ 1rem
- hover 有柔和蓝色背景
- 使用 Vue Transition 实现入场动画

## 五、技术栈
- Vue 3 + <script setup>
- SCSS（变量化、可主题化）
- 不使用第三方 UI 库
- 所有组件支持 v-model

## 六、输出要求
- 设计系统（颜色、圆角、阴影、动效 token）
- 玻璃按钮 / 输入框 / 开关 / 卡片
- 玻璃导航栏（含动效）
- 玻璃菜单卡片（含下拉动画）
- 一个完整 Dashboard 页面示例
- 代码可直接复制使用

请确保：  
✅ 风格高度统一  
✅ 动效细腻、克制  
✅ 代码干净、可维护  
✅ 适合作为平台级设计系统

