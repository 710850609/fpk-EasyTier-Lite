<template>
  <div class="settings-page">
    <!-- 外观设置 -->
    <var-paper class="setting-block" :elevation="1">
      <div class="block-header">
        <var-icon name="palette" size="24" color="var(--color-primary)" />
        <span class="block-title">外观设置</span>
      </div>      
      <div class="theme-options">
        <div 
          v-for="option in themeOptions" 
          :key="option.value"
          class="theme-option"
          :class="{ active: currentThemeMode === option.value }"
          @click="setThemeMode(option.value)"
        >
          <var-icon :name="option.icon" size="20" />
          <span>{{ option.label }}</span>
        </div>
      </div>
    </var-paper>

    <!-- 开发者选项 -->
    <var-paper class="setting-block" :elevation="1">
      <div class="block-header">
        <var-icon name="wrench" size="24" color="var(--color-primary)" />
        <span class="block-title">开发者选项</span>
      </div>
      
      <var-cell>
        <template #description>移动端页面调试</template>
        <template #extra>
          <var-switch v-model="vConsoleEnabled" @change="toggleVConsole" />
        </template>
      </var-cell>
    </var-paper>

     <var-paper class="setting-block" :elevation="1">
      <div class="block-header">
        <var-icon name="lock" size="24" color="var(--color-primary)" />
        <span class="block-title">内核</span>
      </div>      
      <var-cell>
        <template #description>EasyTier 版本 2.5.0</template>
        <template #extra>
          <var-button type="danger" round icon-container>
            <var-icon name="window-close" />
          </var-button>
          <var-icon name="close-circle" />
          <var-icon name="play-circle" />
        </template>
      </var-cell>
    </var-paper>

    <!-- 网络设置 -->
    <!-- <var-paper class="setting-block" :elevation="1">
      <div class="block-header">
        <var-icon name="globe" size="24" color="var(--color-success)" />
        <span class="block-title">网络加速</span>
      </div>
      
      <var-select v-model="settings.github_mirror" label="GitHub 加速地址">
        <var-option 
          v-for="mirror in githubMirrors" 
          :key="mirror.value"
          :label="mirror.label"
          :value="mirror.value"
        />
      </var-select>
      
      <var-cell class="test-link">
        <template #description>
          <a :href="settings.github_mirror" target="_blank" class="mirror-link">
            测试连接速度 <var-icon name="open-in-new" size="14" />
          </a>
        </template>
      </var-cell>
    </var-paper> -->

    <!-- 关于 -->
    <var-paper class="setting-block" :elevation="1">
      <div class="block-header">
        <var-icon name="information" size="24" color="var(--color-info)" />
        <span class="block-title">关于</span>
      </div>
      
      <var-cell>
        <template #default></template>
        <template #description>
          <div>
            <span>EasyTier 在飞牛上简化使用的版本，更合适新手简单上手使用，简记：<strong>易组网</strong></span>
          </div>
          <var-divider />
          <div>
            <var-cell><h3>相关链接</h3></var-cell>
            <var-cell>
              <var-link type="primary" href="https://github.com/710850609/fpk-easytier-lite" target="_blank" underline="hover">
                易组网源码 
              </var-link>
              <img src="https://img.shields.io/github/v/release/710850609/fpk-easytier-lite?color=blue&logo=github" />
            </var-cell>
          </div>
        </template>
      </var-cell>
    </var-paper>
  </div>
</template>

<script setup>
import { themeOptions, setThemeMode, themeMode } from '../config/theme.js'
import { VCONSOLE_ENABLED_KEY } from '../config/storage-keys.js'
import toast from '../components/toast.js'

const vConsoleEnabled = ref(false)
const vConsoleInstance = ref(null)

// 计算当前主题模式（从 theme.js 获取）
const currentThemeMode = computed(() => themeMode.value)

// 加载 VConsole（动态导入）
const loadVConsole = async () => {
  try {
    const VConsole = await import('vconsole')
    vConsoleInstance.value = new VConsole.default()
    return true
  } catch (error) {
    console.error('加载 VConsole 失败:', error)
    return false
  }
}

// 切换 VConsole
const toggleVConsole = async (val) => {
  // 保存开关状态
  localStorage.setItem(VCONSOLE_ENABLED_KEY, val ? 'true' : 'false')

  if (val) {
    const loaded = await loadVConsole()
    if (loaded) {
      toast.success('VConsole 已开启')
    } else {
      toast.error('加载 VConsole 失败')
      vConsoleEnabled.value = false
      localStorage.setItem(VCONSOLE_ENABLED_KEY, 'false')
    }
  } else {
    if (vConsoleInstance.value) {
      vConsoleInstance.value.destroy()
      vConsoleInstance.value = null
    }
    toast.success('VConsole 已关闭')
  }
}

onMounted(() => {
  // 从 localStorage 加载 VConsole 开关状态
  const enabled = localStorage.getItem(VCONSOLE_ENABLED_KEY) === 'true'
  vConsoleEnabled.value = enabled

  // 如果之前开启过，自动加载
  if (enabled) {
    loadVConsole()
  }
})
</script>

<style scoped>
.settings-page {
  padding: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.setting-block {
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 16px;
  background: var(--color-surface-container) !important;
}

.block-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.block-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.mirror-link, .source-link {
  color: var(--color-primary);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.test-link {
  margin-top: 8px;
}

:deep(.var-cell__description) {
  margin-top: 4px;
}

/* 主题选项样式 */
.theme-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: 12px;
  border: 2px solid var(--color-outline);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.theme-option:hover {
  border-color: var(--color-primary);
  background: var(--color-surface-container);
}

.theme-option.active {
  border-color: var(--color-primary);
  background: var(--color-primary-container);
  color: var(--color-on-primary-container);
}

.theme-option span {
  font-size: 14px;
  font-weight: 500;
}
</style>
