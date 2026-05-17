<template>
  <div 
    :class="['glass-card', cardClass]"
    :style="cardStyle"
  >
    <slot></slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 卡片类型: default, soft, dark
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'soft', 'dark'].includes(value)
  },
  // 自定义类名
  customClass: {
    type: String,
    default: ''
  },
  // 是否启用悬停效果
  hoverable: {
    type: Boolean,
    default: true
  },
  // 自定义样式
  customStyle: {
    type: Object,
    default: () => ({})
  }
})

const cardClass = computed(() => {
  const classes = [props.customClass]
  
  if (props.type === 'soft') {
    classes.push('glass-card--soft')
  } else if (props.type === 'dark') {
    classes.push('glass-card--dark')
  }
  
  return classes
})

const cardStyle = computed(() => {
  return props.customStyle
})
</script>

<style scoped lang="scss">
@import '@/themes/dark-purple/styles/wisteria-glass-theme.scss';

.glass-card {
  @extend .glass-card;
}
</style>
