<template>
  <div class="platform-page">
    <var-paper class="download-card" :elevation="2">
      <div class="platform-header">
        <div class="platform-info">
          <h2>EasyTier MacOS版本</h2>
        </div>
      </div>
      <div class="version-info">
        <var-cell>安装应用，并导出飞牛上配置toml文件后。把toml配置文件导入到easytier中，并启动网络即可。</var-cell>
        <var-cell>
          其他使用说明，请访问 
          <var-link type="primary" href="https://easytier.cn/" target="_blank" underline="none">
            EasyTier官网
          </var-link>
        </var-cell>
        <var-space :size="[20, 20]" justify="center">
          <var-cell>
            <var-link type="primary" underline="none" href="https://github.com/EasyTier/EasyTier/releases" target="_blank">
              <img src="https://img.shields.io/github/v/tag/EasyTier/EasyTier?color=blue&logo=github" />
            </var-link>
          </var-cell>
          <var-cell>
            <var-link type="primary" underline="none" href="https://github.com/EasyTier/EasyTier/releases" target="_blank">
              <img src="https://img.shields.io/github/v/release/EasyTier/EasyTier?color=blue&logo=github" />
            </var-link>
          </var-cell>
        </var-space>
      </div>
      <div>
        <var-divider />
        <var-space :size="[20, 20]" justify="center">
          <var-button type="primary" size="large" block @click="downloadLatestAarch64" auto-loading>
            <template #default>
              <var-icon name="download" style="margin-right: 8px;" />
              下载最新版(Apple芯片)
            </template>
          </var-button>
          <var-button type="primary" size="large" block @click="downloadReleaseAarch64" auto-loading>
            <template #default>
              <var-icon name="download" style="margin-right: 8px;" />
              下载稳定版(Apple芯片)
            </template>
          </var-button>
          </var-space>
        <var-space :size="[20, 20]" justify="center">
          <var-button type="primary" size="large" block @click="downloadLatestAmd64" auto-loading>
            <template #default>
              <var-icon name="download" style="margin-right: 8px;" />
              下载最新版(Intel芯片)
            </template>
          </var-button>
          <var-button type="primary" size="large" block @click="downloadReleaseAmd64" auto-loading>
            <template #default>
              <var-icon name="download" style="margin-right: 8px;" />
              下载稳定版(Intel芯片)
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

const githubProxy = ref('https://ghfast.top')

const downloadLatestAarch64 = () => {
  return download('aarch64', true)
}

const downloadReleaseAarch64 = () => {
  return download('aarch64', false)
}

const downloadLatestAmd64 = () => {
  return download('x64', true)
}

const downloadReleaseAmd64 = () => {
  return download('x64', false)
}

const download = (arch, prerelease) => {
  return new Promise(async (resolve, reject) => {
    try {
      const fetchUrl = 'https://api.github.com/repos/EasyTier/EasyTier/releases';
      const response = await fetch(fetchUrl);
      const releases = await response.json();
      const resources = releases.find(r => r.prerelease === prerelease);
      let url = null;
      if (resources) {
        const asset = resources.assets.find(e => e.name.startsWith('easytier-gui_') && e.name.includes(`_${arch}.dmg`));
        if (asset) {
              url = asset.browser_download_url;
          }
      }
      if (githubProxy.value) {
        url = `${githubProxy.value}/${url}`;
      }
      console.log(url)
      window.open(url, '_blank')
      resolve()
    } catch (error) {
      console.error('下载失败:', error)
      reject(error)
    }
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