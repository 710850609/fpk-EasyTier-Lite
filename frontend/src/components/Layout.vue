<template>
  <div class="layout" :class="{ 'dark': isDark, 'menu-collapsed': isMenuCollapsed }">
      <side-menu
        v-if="!isMobile"
        :active="activeMenu"
        v-model:collapsed="isMenuCollapsed"
        @update:active="handleMenuChange"
        class="side-menu"
      />

      <main class="main-content" :class="{ 'has-bottom-nav': isMobile }">
        <div class="content-wrapper">
          <component :is="currentComponent" />
        </div>
      </main>

      <bottom-nav
        v-if="isMobile"
        :active="activeMenu"
        @update:active="handleMenuChange"
      />
    </div>
</template>

<script setup>
import SideMenu from './SideMenu.vue'
import BottomNav from './BottomNav.vue'
import { componentMap } from '../config/menu.js'
import { isDark } from '../config/theme.js'
import { VCONSOLE_ENABLED_KEY } from '../config/storage-keys.js'
import toast from './toast.js'

// 动态导入 Empty 组件，避免与 menu.js 中的动态导入冲突
const Empty = defineAsyncComponent(() => import('../views/Empty.vue'))

const isMobile = ref(window.innerWidth < 768)
const activeMenu = ref('nodes')
const isMenuCollapsed = ref(false)
const fastSettingMode = ref(false)

const handleMenuChange = (key) => {
  activeMenu.value = key
}

// 提供主题状态给子组件
provide('isDark', isDark)
// 提供当前菜单状态给子组件
provide('activeMenu', readonly(activeMenu))
provide('setActiveMenu', handleMenuChange)
provide('fastSettingMode', fastSettingMode)

const currentComponent = computed(() => {
  const component = componentMap[activeMenu.value]
  // 如果没有对应组件，返回空组件（显示提示或保持当前页面）
  if (!component) {
    return Empty
  }
  // 组件已同步加载，直接使用
  return component
})

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

// 从 localStorage 加载 VConsole（动态导入）
const loadVConsole = async () => {
  const vconsoleEnabled = localStorage.getItem(VCONSOLE_ENABLED_KEY)
  if (vconsoleEnabled !== 'true') return

  try {
    const VConsole = await import('vconsole')
    new VConsole.default()
  } catch (error) {
    console.error('加载 VConsole 失败:', error)
    localStorage.setItem(VCONSOLE_ENABLED_KEY, 'false')
    toast.error('加载 VConsole 失败\n' + error.message)
  }
}
// ✅ 节流 + 只处理必要逻辑
let resizeTimer;
const handleResizeThrottled = () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    // 仅调整输入框位置，不动整体布局
    handleResize();
  }, 10);
}

onMounted(() => {
  window.addEventListener('resize', handleResizeThrottled)
  // 加载 VConsole（如果之前开启过）
  loadVConsole()

})

onUnmounted(() => {
  window.removeEventListener('resize', handleResizeThrottled)
  clearTimeout(resizeTimer)
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-body);
}

.side-menu {
  flex-shrink: 0;
  border-right: 1px solid var(--color-outline);
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 100;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
}

.menu-collapsed .main-content {
  margin-left: 72px;
}

.main-content.has-bottom-nav {
  padding-bottom: 64px;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

@media (max-width: 767px) {
  .layout {
    flex-direction: column;
  }
  
  .side-menu {
    position: relative;
    width: 100%;
    height: auto;
  }
  
  .main-content {
    width: 100%;
    margin-left: 0;
  }
  
  .content-wrapper {
    overflow-y: visible;
    padding: 0;
  }
}
</style>
