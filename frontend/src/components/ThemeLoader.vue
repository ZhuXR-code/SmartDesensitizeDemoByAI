<template>
  <component :is="dynamicComponent" v-if="dynamicComponent" />
  <div v-else class="theme-loading">
    <el-skeleton :rows="10" animated />
  </div>
</template>

<script setup>
import { shallowRef, watch, defineProps } from 'vue'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  componentPath: {
    type: String,
    required: true
  }
})

const themeStore = useThemeStore()
const dynamicComponent = shallowRef(null)

const loadComponent = async () => {
  const theme = themeStore.currentTheme
  const path = props.componentPath

  try {
    let module
    if (theme === 'classic') {
      module = await import(`@/themes/vue-classic/views/${path}.vue`)
    } else if (theme === 'vue-classic') {
      module = await import(`@/themes/vue-classic/views/${path}.vue`)
    } else if (theme === 'dark-purple') {
      module = await import(`@/themes/dark-purple/views/${path}.vue`)
    } else if (theme === 'black-gold') {
      module = await import(`@/themes/black-gold/views/${path}.vue`)
    }
    dynamicComponent.value = module.default
  } catch (error) {
    console.error(`Failed to load component: ${path} for theme: ${theme}`, error)
    try {
      const fallback = await import(`@/themes/vue-classic/views/${path}.vue`)
      dynamicComponent.value = fallback.default
    } catch (fallbackError) {
      console.error('Fallback also failed:', fallbackError)
    }
  }
}

// Initial load
loadComponent()

// Reload when theme or route changes
watch(
  [() => themeStore.currentTheme, () => props.componentPath],
  () => {
    loadComponent()
  }
)
</script>

<style scoped>
.theme-loading {
  padding: 20px;
}
</style>
