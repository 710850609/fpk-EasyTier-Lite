<template>
  <div class="platform-page">
    <var-paper class="download-card" :elevation="2">
      <div class="platform-header">
        <div class="platform-info">
          <h2>EasyTier 易组网</h2>
        </div>
      </div>
      <div class="version-info">
        <var-space :size="[20, 20]" justify="center">
          <var-cell>
            <var-link type="primary" underline="none" href="https://github.com/710850609/fpk-easytier-lite/releases" target="_blank">
              <img src="https://img.shields.io/github/v/release/710850609/fpk-easytier-lite?color=blue&logo=github" />
            </var-link>
          </var-cell>
        </var-space>
      </div>
      <var-divider />
      <div class="download-grid">
        <var-paper class="download-item" :elevation="1">
          <div class="item-header">
            <var-icon name="package" size="24" />
            <span class="item-title">x86_64</span>
          </div>
          <div class="item-actions">
            <var-button type="primary" size="normal" @click="download('x86', true)" auto-loading>
              <var-icon name="download"/>
              最新版
            </var-button>
          </div>
        </var-paper>
        <var-paper class="download-item" :elevation="1">
          <div class="item-header">
            <var-icon name="package" size="24" />
            <span class="item-title">Arm64</span>
          </div>
          <div class="item-actions">
            <var-button type="primary" size="normal" @click="download('aarch64', true)" auto-loading>
              <var-icon name="download"/>
              最新版
            </var-button>
          </div>
        </var-paper>
      </div>
    </var-paper>
  </div>
</template>

<script setup>
import toast from '../../components/toast.js'
const githubProxy = ref('https://ghfast.top')

const download = (arch, prerelease) => {
  const loadingToast = toast.loading('功能开发中...')
  setTimeout(() => loadingToast.clear(), 3000);
  return;
  return new Promise(async (resolve, reject) => {
    try {
      const fetchUrl = 'https://api.github.com/repos/EasyTier/EasyTier/releases';
      const response = await fetch(fetchUrl);
      const releases = await response.json();
      const resources = releases.find(r => r.prerelease === prerelease);
      let url = null;
      if (resources) {
        const asset = resources.assets.find(e => e.name.startsWith('easytier-gui_') && e.name.endsWith(`_${arch}`));
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

/* 下载卡片网格 */
.download-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.download-item {
  padding: 20px;
  border-radius: 12px;
  background: var(--color-surface-container) !important;
  display: flex;
  flex-direction: column;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  color: var(--color-on-surface);
}

.item-title {
  font-weight: 600;
  font-size: 15px;
}

.item-actions {
  display: flex;
  gap: 12px;
  margin-top: auto;
}

.item-actions .var-button {
  flex: 1;
  min-width: 90px;
}
</style>