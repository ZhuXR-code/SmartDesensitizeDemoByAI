<template>
  <span :class="['glass-badge', badgeClass]">
    <slot></slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 标签类型: success, info, warning, danger
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'info', 'warning', 'danger'].includes(value)
  },
  // 自定义类名
  customClass: {
    type: String,
    default: ''
  }
})

const badgeClass = computed(() => {
  const classes = [props.customClass]
  
  switch (props.type) {
    case 'success':
      classes.push('glass-badge--success')
      break
    case 'info':
      classes.push('glass-badge--info')
      break
    case 'warning':
      classes.push('glass-badge--warning')
      break
    case 'danger':
      classes.push('glass-badge--danger')
      break
  }
  
  return classes
})
</script>

<style scoped lang="scss">
@import '@/themes/dark-purple/styles/wisteria-glass-theme.scss';

.glass-badge {
  @extend .glass-badge;
}
</style>
