<template>
  <input
    :class="['glass-input', inputClass]"
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    @input="handleInput"
    @focus="handleFocus"
    @blur="handleBlur"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 输入框类型
  type: {
    type: String,
    default: 'text'
  },
  // 绑定值
  modelValue: {
    type: [String, Number],
    default: ''
  },
  // 占位符
  placeholder: {
    type: String,
    default: ''
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

const emit = defineEmits(['update:modelValue', 'focus', 'blur'])

const inputClass = computed(() => {
  return props.customClass
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleBlur = (event) => {
  emit('blur', event)
}
</script>

<style scoped lang="scss">
@import '@/themes/dark-purple/styles/wisteria-glass-theme.scss';

.glass-input {
  @extend .glass-input;
}
</style>
