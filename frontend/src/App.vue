<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <div class="content-wrapper">
      <component :is="currentComponent" />
    </div>

    <!-- 标签页 - 固定在底部 -->
    <div class="tabs-wrapper">
       <var-bottom-navigation v-model:active="activeTab" active-color="var(--color-primary)">
        <var-bottom-navigation-item name="nodes" label="节点" icon="format-list-checkbox" />
        <var-bottom-navigation-item name="config" label="配置" icon="bookmark" />
        <var-bottom-navigation-item name="download" label="下载" icon="download" />
        <var-bottom-navigation-item name="setting" label="设置" icon="cog" />
      </var-bottom-navigation>
    </div>
    
  </div>
</template>

<script setup>
import { shallowRef, onMounted, onUnmounted, watch } from 'vue'
import { Snackbar, StyleProvider, Themes } from '@varlet/ui'

// 允许同时显示多个消息条
Snackbar.allowMultiple(true)
const activeTab = shallowRef('nodes')
const currentComponent = shallowRef(null)

// 动态导入组件
const loadComponent = async (tab) => {
  switch (tab) {
    case 'nodes':
      const { default: NodesTab } = await import('./components/NodesTab.vue')
      currentComponent.value = NodesTab
      break
    case 'config':
      const { default: ConfigTab } = await import('./components/ConfigTab.vue')
      currentComponent.value = ConfigTab
      break
    case 'download':
      const { default: DownloadTab } = await import('./components/DownloadTab.vue')
      currentComponent.value = DownloadTab
      break
    case 'setting':
      const { default: SettingTab } = await import('./components/SettingTab.vue')
      currentComponent.value = SettingTab
      break
    default:
      currentComponent.value = null
  }
}

// 监听标签页变化
watch(activeTab, (newTab) => {
  loadComponent(newTab)
})

const changeTheme = (theme) => {
  if (theme === 'dark') {
    console.log('md3Dark')
    StyleProvider(Themes.md3Dark)
    document.body.classList.remove('light-mode')
    document.body.classList.add('dark-mode')
  } else {
    StyleProvider(Themes.md3Light)
    // StyleProvider(null)
    document.body.classList.remove('dark-mode')
    document.body.classList.add('light-mode')
  }
}

onMounted(async () => {
  new FnThemeListener((themeMode) => changeTheme(themeMode));
  // 初始加载第一个组件
  loadComponent(activeTab.value)
})

onUnmounted(() => {
})
</script>

<style scoped>
  .app-container {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    height: 96vh;
  }

  .content-wrapper {
    flex: 1;
    overflow: auto;
    padding: 0 0px;
  }

  .tabs-wrapper {
    flex-shrink: 0;
    padding: 12px;
    border-top: 1px solid var(--color-outline);
    background: var(--color-body);
  }

  @media (max-width: 767px) {
    .app-container {
      height: 100vh;
    }

    .tabs-wrapper {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      width: 100%;
      background: var(--color-body);
      border-top: 1px solid var(--color-outline);
    }

    .content-wrapper {
      padding-bottom: 80px;
    }
  }
</style>