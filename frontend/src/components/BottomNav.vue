<template>
  <div class="bottom-nav" :class="{ 'dark': isDark }">
    <div 
      v-for="item in menuTree" 
      :key="item.key"
      class="nav-item"
      :class="{ active: currentActive === item.key }"
      @click="handleNavClick(item)"
    >
      <var-icon :name="item.icon" :size="24" />
      <span class="nav-label">{{ item.label }}</span>
    </div>
  </div>
  
  <!-- 子菜单弹窗 - 动态适配任何有子菜单的项 -->
  <var-popup 
    v-model:show="showSubMenu" 
    position="bottom"
  >
    <div class="submenu-popup">
      <div class="popup-title">{{ currentSubMenuTitle }}</div>
      <div 
        v-for="item in currentSubMenus" 
        :key="item.key"
        class="popup-item"
        @click="handleSubMenuClick(item.key)"
      >
        <var-icon :name="item.icon" size="20" />
        <span>{{ item.label }}</span>
      </div>
    </div>
  </var-popup>
</template>

<script setup>
import { ref, watch, inject } from 'vue'
import { menuTree } from '../config/menu.js'

const props = defineProps({
  active: String
})

const emit = defineEmits(['update:active'])

// 注入主题状态
const isDark = inject('isDark', ref(false))

// 获取父菜单key
const getParentMenuKey = (key) => {
  if (key?.startsWith('software-') && key !== 'software') {
    return 'software'
  }
  return key
}

const currentActive = ref('nodes')
const showSubMenu = ref(false)
const currentSubMenus = ref([])
const currentSubMenuTitle = ref('')
const currentParentKey = ref('')

// 同步外部 active
watch(() => props.active, (val) => {
  currentActive.value = getParentMenuKey(val) || 'nodes'
}, { immediate: true })

const handleNavClick = (menu) => {
  // 如果有子菜单，显示弹窗
  if (menu?.children && menu.children.length > 0) {
    currentSubMenus.value = menu.children
    currentSubMenuTitle.value = menu.label
    currentParentKey.value = menu.key
    showSubMenu.value = true
  } else {
    currentActive.value = menu.key
    emit('update:active', menu.key)
  }
}

const handleSubMenuClick = (key) => {
  showSubMenu.value = false
  currentActive.value = currentParentKey.value
  emit('update:active', key)
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(var(--color-surface-rgb, 255, 255, 255), 0.55);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--color-outline-variant);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
}

/* 深色主题适配 */
.bottom-nav.dark {
  background: rgba(var(--color-surface-rgb, 30, 30, 30), 0.55);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 16px;
  cursor: pointer;
  color: var(--color-on-surface-variant);
  transition: all 0.2s;
}

.nav-item.active {
  color: var(--color-primary);
}

.nav-label {
  font-size: 12px;
  font-weight: 500;
}

.submenu-popup {
  padding: 16px;
  background: transparent;
  border-radius: 16px 16px 0 0;
}

.popup-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--color-on-surface);
  text-align: center;
}

.popup-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--color-on-surface);
  transition: background 0.2s;
}

.popup-item:hover {
  background: var(--color-surface-container-highest);
}

.popup-item:active {
  background: var(--color-surface-container);
}
</style>
