<template>
  <button
    :class="['glass-button', buttonClass]"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot></slot>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 按钮类型: primary, secondary, ghost, danger
  type: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'ghost', 'danger'].includes(value)
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 自定义类名
  customClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['click'])

const buttonClass = computed(() => {
  const classes = [props.customClass]
  
  switch (props.type) {
    case 'primary':
      classes.push('glass-button--primary')
      break
    case 'secondary':
      classes.push('glass-button--secondary')
      break
    case 'ghost':
      classes.push('glass-button--ghost')
      break
    case 'danger':
      classes.push('glass-button--danger')
      break
  }
  
  return classes
})

const handleClick = (event) => {
  if (!props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
@import '@/themes/dark-purple/styles/wisteria-glass-theme.scss';

.glass-button {
  @extend .glass-button;
}
</style>
