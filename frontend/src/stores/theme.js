import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', () => {
  const themes = [
    { key: 'classic', label: '经典', icon: 'Sunny' },
    { key: 'vue-classic', label: 'Vue经典', icon: 'Connection' },
    { key: 'dark-purple', label: '暗紫', icon: 'Moon' },
    { key: 'black-gold', label: '黑金', icon: 'Star' }
  ]

  const savedTheme = localStorage.getItem('app-theme')
  const validThemes = ['classic', 'vue-classic', 'dark-purple', 'black-gold']
  const currentTheme = ref(validThemes.includes(savedTheme) ? savedTheme : 'classic')

  const currentThemeLabel = computed(() => {
    const theme = themes.find(t => t.key === currentTheme.value)
    return theme ? theme.label : '经典'
  })

  const isDarkTheme = computed(() => {
    return currentTheme.value === 'dark-purple' || currentTheme.value === 'black-gold'
  })

  function setTheme(themeKey) {
    if (themes.some(t => t.key === themeKey)) {
      currentTheme.value = themeKey
      localStorage.setItem('app-theme', themeKey)
      applyTheme(themeKey)

      window.location.reload()
    }
  }

  function applyTheme(themeKey) {
    const html = document.documentElement
    html.classList.remove('theme-classic', 'theme-vue-classic', 'theme-dark-purple', 'theme-black-gold')
    html.classList.add(`theme-${themeKey}`)

    if (themeKey === 'classic' || themeKey === 'vue-classic') {
      html.style.backgroundColor = '#f0f2f5'
    } else {
      html.style.backgroundColor = ''
    }
  }

  function initTheme() {
    applyTheme(currentTheme.value)
  }

  return {
    themes,
    currentTheme,
    currentThemeLabel,
    isDarkTheme,
    setTheme,
    initTheme
  }
})
