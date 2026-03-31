<template>
  <div class="platform-page">
    <var-paper class="download-card" :elevation="2">
      <div class="platform-header">
        <div class="platform-info">
          <h2>EasyTier 鸿蒙版本</h2>
        </div>
      </div>
      <div class="version-info">
        <var-cell>安装应用，并导出飞牛上配置toml文件后。把toml配置文件内容复制黏贴到easytier中，并启动网络即可。</var-cell>
        <var-cell>
          其他使用说明，请访问 
          <var-link type="primary" href="https://easytier.cn/guide/gui/easytier-harmonyos.html" target="_blank" underline="none">
            EasyTier官网
          </var-link>
        </var-cell>
      </div>
      <div>
        <var-divider />
        <var-space :size="[20, 20]" justify="center">
          <var-button type="primary" size="normal" block @click="copyAndOpenLink" auto-loading>
            <template #default>
              <var-icon name="share" style="margin-right: 8px;" />
              前往鸿蒙应用商店
            </template>
          </var-button>
        </var-space>
      </div>
    </var-paper>
  </div>
</template>

<script setup>
import { Snackbar } from '@varlet/ui'
import { copyToClipboard } from '../../utils/clipboard.js'

const harmonyStoreUrl = 'https://appgallery.huawei.com/app/detail?id=top.frankhan.easytier&channelId=SHARE&source=appshare'

const copyAndOpenLink = () => {
  window.open(harmonyStoreUrl, '_blank')
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