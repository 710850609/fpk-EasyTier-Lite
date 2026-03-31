<template>
  <div class="platform-page">
    <var-paper class="download-card" :elevation="2">
      <div class="platform-header">
        <div class="platform-info">
          <h2>EasyTier 管理器</h2>
        </div>
      </div>
      <div class="version-info">
        <var-cell>推荐新手使用</var-cell>
        <var-cell>集成当前配置，解压启动后选择配置，即可组网</var-cell>
        <var-cell>其他使用说明，请访问 <var-link type="primary" href="https://easytier.cn/guide/gui/easytier-manager.html" target="_blank" underline="none">EasyTier 管理器使用</var-link></var-cell>
        <var-cell>
          <var-link type="primary" underline="none" href="https://github.com/EasyTier/easytier-manager/releases" target="_blank"><img src="https://img.shields.io/github/v/release/EasyTier/easytier-manager?color=blue&logo=github" /></var-link>
        </var-cell>
      </div>
      <div>
        <var-divider />
        <var-space :size="[20, 20]" justify="center">
          <var-button type="primary" size="normal" block @click="download" auto-loading>
            <template #default>
              <var-icon name="download" style="margin-right: 8px;" />
              稳定版
            </template>
          </var-button>
        </var-space>
      </div>
    </var-paper>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '../../utils/api.js'

const download = () => {
  return new Promise((resolve, reject) => {
    let url = api.windows.getDownloadUrl()
    window.open(url, '_blank')
    resolve()
  })
}
</script>

<style scoped>
.platform-page {
  padding: 16px;
  max-width: 900px;
  margin: 0 auto;
}

.download-card {
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 20px;
  text-align: center;
}

.platform-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.platform-info h2 {
  margin: 0;
  color: var(--color-on-surface);
}

.platform-info p {
  margin: 4px 0 0;
  color: var(--color-on-surface-variant);
}

.version-info {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-outline-variant);
  font-size: 14px;
  color: var(--color-on-surface-variant);
}
</style>