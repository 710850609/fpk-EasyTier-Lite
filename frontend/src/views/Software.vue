<template>
  <div class="software-page">
    <component :is="currentPlatform" />
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import Windows from './software/Windows.vue'
import MacOS from './software/MacOS.vue'
import IOS from './software/IOS.vue'
import Linux from './software/Linux.vue'
import Android from './software/Android.vue'
import HarmonyOS from './software/HarmonyOS.vue'

// 注入当前菜单状态
const activeMenu = inject('activeMenu', { value: 'software-windows' })

// 从当前菜单获取平台
const currentPlatform = computed(() => {
  const menuValue = activeMenu?.value || 'software-windows'
  const map = {
    'software-windows': Windows,
    'software-macos': MacOS,
    'software-ios': IOS,
    'software-linux': Linux,
    'software-android': Android,
    'software-harmonyos': HarmonyOS
  }
  return map[menuValue] || Windows
})
</script>

<style scoped>
.software-page {
  height: 100%;
}
</style>
