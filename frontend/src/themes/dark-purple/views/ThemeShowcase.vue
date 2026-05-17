<template>
  <div class="theme-showcase">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="title">色系2 - 暮色紫雾玻璃主题</h1>
      <p class="subtitle">Wisteria Twilight Glass Theme Showcase</p>
    </div>

    <!-- 色彩系统展示 -->
    <GlassCard type="default" class="section-card">
      <h2 class="section-title">🎨 色彩系统</h2>
      <div class="color-grid">
        <div class="color-item">
          <div class="color-swatch" style="background: #210124;"></div>
          <span class="color-label">Base #210124</span>
        </div>
        <div class="color-item">
          <div class="color-swatch" style="background: #420D4B;"></div>
          <span class="color-label">Surface Dark #420D4B</span>
        </div>
        <div class="color-item">
          <div class="color-swatch" style="background: #6667AB;"></div>
          <span class="color-label">Surface Soft #6667AB</span>
        </div>
        <div class="color-item">
          <div class="color-swatch" style="background: #F4FDAF; color: #210124;"></div>
          <span class="color-label">Primary Text #F4FDAF</span>
        </div>
        <div class="color-item">
          <div class="color-swatch" style="background: #EFDD8D; color: #210124;"></div>
          <span class="color-label">Secondary Text #EFDD8D</span>
        </div>
        <div class="color-item">
          <div class="color-swatch" style="background: #DED9E2; color: #210124;"></div>
          <span class="color-label">Tertiary Text #DED9E2</span>
        </div>
      </div>
    </GlassCard>

    <!-- 按钮组件展示 -->
    <GlassCard type="soft" class="section-card">
      <h2 class="section-title">🔘 按钮组件</h2>
      <div class="button-group">
        <GlassButton type="primary">主要按钮</GlassButton>
        <GlassButton type="secondary">次要按钮</GlassButton>
        <GlassButton type="ghost">幽灵按钮</GlassButton>
        <GlassButton type="danger">危险按钮</GlassButton>
        <GlassButton type="primary" disabled>禁用按钮</GlassButton>
      </div>
    </GlassCard>

    <!-- 输入框展示 -->
    <GlassCard type="dark" class="section-card">
      <h2 class="section-title">📝 输入框组件</h2>
      <div class="input-group">
        <GlassInput 
          v-model="inputValue" 
          placeholder="请输入内容..."
          class="demo-input"
        />
        <GlassInput 
          v-model="searchValue" 
          placeholder="搜索..."
          type="search"
          class="demo-input"
        />
      </div>
      <p class="input-value">输入值: {{ inputValue }}</p>
    </GlassCard>

    <!-- 标签/Badge 展示 -->
    <GlassCard type="default" class="section-card">
      <h2 class="section-title">🏷️ 标签组件</h2>
      <div class="badge-group">
        <GlassBadge type="success">成功</GlassBadge>
        <GlassBadge type="info">信息</GlassBadge>
        <GlassBadge type="warning">警告</GlassBadge>
        <GlassBadge type="danger">危险</GlassBadge>
      </div>
    </GlassCard>

    <!-- 卡片类型展示 -->
    <div class="card-types">
      <GlassCard type="default" class="type-card">
        <h3>默认卡片</h3>
        <p>Standard glass card with gradient background</p>
      </GlassCard>
      
      <GlassCard type="soft" class="type-card">
        <h3>柔和卡片</h3>
        <p>Soft glass card with lighter appearance</p>
      </GlassCard>
      
      <GlassCard type="dark" class="type-card">
        <h3>深色卡片</h3>
        <p>Dark glass card for contrast sections</p>
      </GlassCard>
    </div>

    <!-- 渐变效果展示 -->
    <GlassCard type="default" class="section-card">
      <h2 class="section-title">✨ 渐变效果</h2>
      <div class="gradient-demo">
        <div class="gradient-box gradient-primary">
          <span>主渐变</span>
        </div>
        <div class="gradient-box gradient-soft">
          <span>柔光渐变</span>
        </div>
        <div class="gradient-box gradient-dark">
          <span>深紫渐变</span>
        </div>
      </div>
    </GlassCard>

    <!-- 动画效果展示 -->
    <GlassCard type="soft" class="section-card">
      <h2 class="section-title">🎬 动画效果</h2>
      <div class="animation-demo">
        <div class="anim-box glass-shimmer">Shimmer</div>
        <div class="anim-box glass-glow">Glow</div>
        <div class="anim-box glass-float">Float</div>
      </div>
    </GlassCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import GlassCard from '@/themes/dark-purple/components/GlassCard.vue'
import GlassButton from '@/themes/dark-purple/components/GlassButton.vue'
import GlassInput from '@/themes/dark-purple/components/GlassInput.vue'
import GlassBadge from '@/themes/dark-purple/components/GlassBadge.vue'

const inputValue = ref('')
const searchValue = ref('')
</script>

<style scoped lang="scss">
@import '@/themes/dark-purple/styles/wisteria-glass-theme.scss';

.theme-showcase {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
  
  .title {
    font-size: 2.5rem;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
  
  .subtitle {
    font-size: 1.125rem;
    color: $text-tertiary;
    font-weight: 400;
  }
}

.section-card {
  margin-bottom: 2rem;
  
  .section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid $glass-border-light;
  }
}

// 色彩网格
.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.color-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.color-swatch {
  height: 80px;
  border-radius: $radius-lg;
  border: 1px solid $glass-border-medium;
  box-shadow: $glass-shadow-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.color-label {
  font-size: 0.875rem;
  color: $text-secondary;
  text-align: center;
}

// 按钮组
.button-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

// 输入框组
.input-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.demo-input {
  width: 100%;
}

.input-value {
  color: $text-accent-cool;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

// 标签组
.badge-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

// 卡片类型展示
.card-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.type-card {
  padding: 1.5rem;
  
  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 0.75rem;
  }
  
  p {
    color: $text-secondary;
    font-size: 0.875rem;
    line-height: 1.6;
  }
}

// 渐变展示
.gradient-demo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.gradient-box {
  height: 100px;
  border-radius: $radius-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid $glass-border-medium;
  box-shadow: $glass-shadow-md;
  
  span {
    color: $text-primary;
    font-weight: 600;
    font-size: 1rem;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  }
}

.gradient-primary {
  background: $gradient-primary;
  
  span {
    color: $bg-base;
  }
}

.gradient-soft {
  background: $gradient-soft;
}

.gradient-dark {
  background: $gradient-dark;
}

// 动画展示
.animation-demo {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.anim-box {
  width: 120px;
  height: 80px;
  background: $gradient-card;
  backdrop-filter: blur($glass-blur-md);
  border: 1px solid $glass-border-medium;
  border-radius: $radius-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $text-primary;
  font-weight: 600;
  box-shadow: $glass-shadow-md;
}

// 响应式
@media (max-width: 768px) {
  .theme-showcase {
    padding: 1rem;
  }
  
  .page-header .title {
    font-size: 2rem;
  }
  
  .button-group,
  .badge-group,
  .animation-demo {
    flex-direction: column;
  }
  
  .anim-box {
    width: 100%;
  }
}
</style>
