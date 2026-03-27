<template>
  <div class="side-menu" :class="{ collapsed: isCollapsed }">
    <div class="logo">
      <var-icon name="network-wired" :size="32" />
      <span v-if="!isCollapsed" class="logo-text">易组网 . EasyTier</span>
      <span v-if="isCollapsed" class="logo-text">ET</span>
      <var-button
        class="collapse-btn"
        text
        round
        :size="isCollapsed ? 'small' : 'mini'"
        @click="toggleCollapse"
      >
        <var-icon :name="isCollapsed ? 'menu-right' : 'menu-left'" />
      </var-button>
    </div>
    
    <div class="menu-list">
      <template v-for="menu in menuTree" :key="menu.key">
        <!-- 有子菜单的项 -->
        <div v-if="menu.children" class="menu-group">
          <div
            class="menu-item"
            :class="{ active: active?.startsWith(menu.key) }"
            @click="isCollapsed ? handleClick(menu.children[0].key) : toggleExpand(menu.key)"
          >
            <var-icon :name="menu.icon" class="menu-icon" />
            <span v-if="!isCollapsed" class="menu-title">{{ menu.label }}</span>
            <var-icon
              v-if="!isCollapsed"
              name="chevron-down"
              class="expand-icon"
              :class="{ expanded: expandedKeys.includes(menu.key) }"
            />
          </div>

          <div v-if="!isCollapsed && expandedKeys.includes(menu.key)" class="sub-menu-list">
            <div
              v-for="child in menu.children"
              :key="child.key"
              class="sub-menu-item"
              :class="{ active: active === child.key }"
              @click="handleClick(child.key)"
            >
              <var-icon :name="child.icon" size="18" />
              <span>{{ child.label }}</span>
            </div>
          </div>
        </div>

        <!-- 无子菜单的项 -->
        <div
          v-else
          class="menu-item"
          :class="{ active: active === menu.key }"
          @click="handleClick(menu.key)"
        >
          <var-icon :name="menu.icon" class="menu-icon" />
          <span v-if="!isCollapsed" class="menu-title">{{ menu.label }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { menuTree } from '../config/menu.js'
import { SIDEBAR_COLLAPSED_KEY } from '../config/storage-keys.js'

const props = defineProps({
  active: String,
  collapsed: Boolean
})

const emit = defineEmits(['update:active', 'update:collapsed'])

const expandedKeys = ref([])
const isCollapsed = ref(props.collapsed || false)

// 页面加载时从 localStorage 恢复折叠状态
onMounted(() => {
  const saved = localStorage.getItem(SIDEBAR_COLLAPSED_KEY)
  if (saved !== null) {
    isCollapsed.value = saved === 'true'
    emit('update:collapsed', isCollapsed.value)
  }
})

// 监听 props.collapsed 变化
watch(() => props.collapsed, (val) => {
  isCollapsed.value = val
})

// 监听 isCollapsed 变化，保存到 localStorage
watch(isCollapsed, (val) => {
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(val))
})

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  emit('update:collapsed', isCollapsed.value)
}

// 监听 active 变化，自动展开父菜单
watch(() => props.active, (val) => {
  if (val?.startsWith('software-') && !expandedKeys.value.includes('software')) {
    expandedKeys.value.push('software')
  }
}, { immediate: true })

const toggleExpand = (key) => {
  const index = expandedKeys.value.indexOf(key)
  if (index > -1) {
    expandedKeys.value.splice(index, 1)
  } else {
    expandedKeys.value.push(key)
  }
}

const handleClick = (key) => {
  emit('update:active', key)
}
</script>

<style scoped>
.side-menu {
  height: 100vh;
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--color-outline);
  width: 240px;
  transition: width 0.3s ease;
}

.side-menu.collapsed {
  width: 72px;
}

.logo {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--color-outline);
  position: relative;
}

.side-menu.collapsed .logo {
  padding: 20px 12px;
  justify-content: center;
}

.collapse-btn {
  margin-left: auto;
  color: var(--color-primary);
}

.side-menu.collapsed .collapse-btn {
  margin-left: 0;
  position: absolute;
  right: -12px;
  background: var(--color-surface);
  border: 1px solid var(--color-outline);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-primary);
}

.menu-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--color-on-surface);
}

.side-menu.collapsed .menu-item {
  padding: 12px;
  justify-content: center;
}

.side-menu.collapsed .menu-icon {
  margin-right: 0;
}

.menu-item:hover {
  background: var(--color-surface-container-highest);
}

.menu-item.active {
  background: var(--color-primary-container);
  color: var(--color-on-primary-container);
}

.menu-icon {
  margin-right: 12px;
  color: var(--color-on-surface-variant);
}

.menu-item.active .menu-icon {
  color: var(--color-on-primary-container);
}

.menu-title {
  flex: 1;
  font-size: 14px;
}

.expand-icon {
  transition: transform 0.2s;
  color: var(--color-on-surface-variant);
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.menu-group {
  margin-bottom: 4px;
}

.sub-menu-list {
  padding-left: 8px;
}

.sub-menu-item {
  display: flex;
  align-items: center;
  padding: 10px 16px 10px 40px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--color-on-surface-variant);
  font-size: 13px;
  gap: 8px;
}

.sub-menu-item:hover {
  background: var(--color-surface-container-highest);
}

.sub-menu-item.active {
  background: var(--color-primary-container);
  color: var(--color-on-primary-container);
}
</style>
