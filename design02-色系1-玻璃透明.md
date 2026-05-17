液态玻璃（Liquid Glass）UI 设计系统文档

青苔紫夜 · Moss Midnight Edition（颜色深度重构版）

适用平台：PC Web 端

前端框架：Vue 3 + TypeScript + SCSS

设计风格：毛玻璃（Frosted Glass）+ 暗调青苔紫夜配色

1. 设计理念与风格定位

1.1 核心风格

• 风格名称：Liquid Glass（液态玻璃）

• 视觉关键词：通透、呼吸感、悬浮、神秘、自然

• 材质特征：

  • 半透明毛玻璃背景（backdrop-filter: blur）

  • 微弱的高光边框

  • 多层叠加的柔和阴影

  • 避免生硬的实色填充

1.2 视觉基调

• 整体氛围：深夜森林、潮湿泥土、静谧神秘

• 对比度：低对比度背景 + 高亮度强调色

• 动效哲学：轻盈、克制、无干扰

2. 色彩系统（Color System）

2.1 颜色深度分析与角色定义

根据您提供的 5 个色值，我进行了亮度（Luminance）和视觉温度的分析，并重新定义了它们在界面中的功能角色（从最亮到最暗排序）：

色名 视觉角色 亮度判断 HEX RGB 使用场景

Lime Cream 高光/强调色 最亮（接近白色） #F4FDAF 244, 253, 175 主按钮文字、图标、悬停高亮、选中状态

Light Gold 浅色表面 较亮（暖黄） #EFDD8D 239, 221, 141 卡片背景、表单输入框、浅色玻璃面板

Fern 自然/中性过渡 中等（深绿） #65743A 101, 116, 58 边框、分割线、次要图标、禁用态

Dark Slate Grey 深色表面 较暗（深灰绿） #394F49 57, 79, 73 深色玻璃卡片、导航栏背景、页脚

Midnight Violet 背景/深邃基底 最暗（近黑） #210124 33, 1, 36 页面主背景、模态框背景、深色遮罩

2.2 颜色使用规范（强制）

• 背景层：必须使用 Midnight Violet 或其半透明变体。

• 前景/文字：在浅色背景上使用 Lime Cream 或 Light Gold；在深色背景上使用 Lime Cream。

• 玻璃材质：使用 Light Gold 或 Dark Slate Grey 作为玻璃底色，并叠加 rgba(255,255,255,0.1) 高光。

3. PC 端导航菜单栏设计（Navigation Bar）

3.1 布局结构

• 位置：页面顶部，固定定位（position: fixed; top: 0; left: 0; width: 100%）

• 高度：64px

• 内边距：0 24px

• 对齐方式：左侧 Logo，右侧菜单项

3.2 视觉样式

• 背景：半透明毛玻璃（background: rgba(33, 1, 36, 0.8); backdrop-filter: blur(12px);）

• 边框：底部 1px 实线，border-bottom: 1px solid rgba(244, 253, 175, 0.1);

• 阴影：box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);

3.3 菜单项（Menu Items）

• 字体：font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500;

• 默认颜色：#EFDD8D（Light Gold）

• 悬停颜色：#F4FDAF（Lime Cream）

• 激活状态：#F4FDAF + 下划线（border-bottom: 2px solid #F4FDAF;）

• 间距：每个菜单项之间 24px 间距

3.4 菜单栏动效

• 入场动画：淡入 + 从上至下微移（opacity: 0 -> 1; transform: translateY(-8px) -> 0;）

• 悬停动画：文字颜色平滑过渡（transition: color 150ms ease-out;）

• 背景呼吸：轻微的不透明度变化（opacity: 0.8 -> 0.9;，每 5 秒一次，极微弱）

4. 菜单卡片设计（Menu Card）

4.1 布局结构

• 位置：页面中央或右侧抽屉

• 宽度：320px

• 圆角：16px

• 内边距：24px

4.2 视觉样式

• 背景：双层玻璃（background: rgba(239, 221, 141, 0.05); backdrop-filter: blur(20px);）

• 边框：1px solid rgba(244, 253, 175, 0.15);

• 阴影：box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);

• 高光：顶部 1px 线性渐变高光（background: linear-gradient(to bottom, rgba(244, 253, 175, 0.1), transparent);）

4.3 卡片内容

• 标题：font-size: 18px; font-weight: 600; color: #F4FDAF;

• 分隔线：height: 1px; background: rgba(244, 253, 175, 0.1);

• 列表项：

  • 高度：40px

  • 文字颜色：#EFDD8D

  • 悬停背景：rgba(244, 253, 175, 0.08);

  • 悬停文字：#F4FDAF

4.4 卡片动效

• 入场动画：淡入 + 从右至左微移（opacity: 0 -> 1; transform: translateX(16px) -> 0;）

• 悬停动画：卡片上浮 2px + 阴影增强（transform: translateY(-2px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);）

• 点击反馈：轻微缩放 0.98（transform: scale(0.98);）

5. 动效系统（Motion System）

5.1 动效原则

• 轻量：位移 ≤ 8px，缩放 ≤ 1.05

• 快：入场 / 悬停：150–250ms

• 柔：使用 ease-out 或 cubic-bezier(0.22, 1, 0.36, 1)

• 层次：背景不动，前景微动

• 不抢：不遮挡内容，不频繁闪烁

5.2 标准动效曲线（SCSS）

$ease-out: cubic-bezier(0.22, 1, 0.36, 1);
$ease-in-out: cubic-bezier(0.42, 0, 0.58, 1);
$spring: cubic-bezier(0.34, 1.56, 0.64, 1);


5.3 通用动效 Token（SCSS）

// 时长
$duration-fast: 150ms;
$duration-base: 220ms;
$duration-slow: 350ms;

// 组合 mixin
@mixin glass-transition($props...) {
  transition: join($props, (), comma) $duration-base $ease-out;
}


5.4 推荐动效清单

场景 动效

按钮 hover 上浮 2px + 阴影增强

按钮 click 轻微缩放 0.97

卡片 hover 上浮 + 高光增强

菜单展开 淡入 + 向下微移

菜单项 hover 背景渐显 + 左高光线

开关切换 滑块弹簧位移

页面切换 fade + slide-up

加载 玻璃呼吸（opacity 变化）

6. 技术实现建议（Vue 3 + SCSS）

6.1 全局样式变量（Global SCSS Variables）

// 颜色
$lime-cream: #F4FDAF;
$light-gold: #EFDD8D;
$fern: #65743A;
$dark-slate-grey: #394F49;
$midnight-violet: #210124;

// 动效
$duration-base: 220ms;
$ease-out: cubic-bezier(0.22, 1, 0.36, 1);

// 玻璃材质
$glass-bg-light: rgba($light-gold, 0.05);
$glass-bg-dark: rgba($midnight-violet, 0.8);
$glass-border: rgba($lime-cream, 0.15);
$glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);


6.2 Vue 组件示例（Navbar.vue）

<template>
  <nav class="navbar">
    <div class="logo">Logo</div>
    <ul class="menu">
      <li v-for="item in menuItems" :key="item.name" :class="{ active: item.active }">
        {{ item.name }}
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
const menuItems = [
  { name: '首页', active: true },
  { name: '产品', active: false },
  { name: '关于', active: false },
]
</script>

<style scoped lang="scss">
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: $glass-bg-dark;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid $glass-border;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 1000;

  .menu li {
    color: $light-gold;
    font-size: 14px;
    font-weight: 500;
    margin: 0 24px;
    cursor: pointer;
    @include glass-transition(color);

    &:hover {
      color: $lime-cream;
    }

    &.active {
      color: $lime-cream;
      border-bottom: 2px solid $lime-cream;
    }
  }
}
</style>


7. 交付物检查清单（Checklist）

✅ 所有颜色必须使用指定 HEX 值  
✅ 所有玻璃材质必须使用 backdrop-filter: blur  
✅ 所有动效必须使用 $ease-out 曲线  
✅ 导航栏必须固定顶部，高度为 64px  
✅ 菜单卡片必须居中或右对齐，宽度 320px  
✅ 所有悬停态必须有颜色或位移变化  
✅ 所有点击态必须有轻微缩放反馈  

这份文档已经完全结构化、参数化、可执行，你可以直接复制粘贴给任何 AI（如 Cursor、Claude、GPT-4、通义千问等），它会精准生成符合你要求的 Vue 3 前端代码。  
如需扩展“下拉菜单”、“抽屉动画”、“响应式适配”，可在此基础上追加模块。