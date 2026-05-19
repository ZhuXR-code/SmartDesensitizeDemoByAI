<template>
  <component :is="dynamicLayout" v-if="dynamicLayout" />
  <div v-else class="layout-loading">
    <el-skeleton :rows="5" animated />
  </div>
</template>

<script setup>
import { shallowRef, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const dynamicLayout = shallowRef(null)

const loadLayout = async () => {
  const theme = themeStore.currentTheme

  try {
    let module
    if (theme === 'classic') {
      module = await import('@/themes/classic/components/Layout.vue')
    } else if (theme === 'vue-classic') {
      module = await import('@/themes/vue-classic/components/Layout.vue')
    } else if (theme === 'dark-purple') {
      module = await import('@/themes/dark-purple/components/Layout.vue')
    } else if (theme === 'black-gold') {
      module = await import('@/themes/black-gold/components/Layout.vue')
    }
    dynamicLayout.value = module.default
  } catch (error) {
    console.error(`Failed to load layout for theme: ${theme}`, error)
    // Fallback to classic
    try {
      const fallback = await import('@/themes/classic/components/Layout.vue')
      dynamicLayout.value = fallback.default
    } catch (fallbackError) {
      console.error('Fallback also failed:', fallbackError)
    }
  }
}

// Initial load
loadLayout()

// Reload when theme changes
watch(() => themeStore.currentTheme, () => {
  loadLayout()
})
</script>

<style scoped>
.layout-loading {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
</style>
