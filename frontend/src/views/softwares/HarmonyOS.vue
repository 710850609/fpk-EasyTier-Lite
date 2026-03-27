<script setup>
import { Snackbar } from '@varlet/ui'
import { copyToClipboard } from '../../utils/clipboard.js'

const harmonyStoreUrl = 'https://appgallery.huawei.com/app/detail?id=top.frankhan.easytier&channelId=SHARE&source=appshare'

const copyAndOpenLink = () => {
  window.open(harmonyStoreUrl, '_blank')
}
</script>

<template>
  <var-paper :elevation="2" class="software-page">
    <h2 class="page-title">鸿蒙客户端</h2>

    <var-paper :elevation="0" class="instructions-section">
      <var-cell><a href="https://easytier.cn/guide/gui/easytier-harmonyos.html" target="_blank">Easytier相关使用说明</a>
      </var-cell>
      <var-divider />
    </var-paper>

    <var-paper :elevation="0" class="download-section">
      <var-space direction="column" :size="[16, 0]">
        <var-button type="primary" size="large" @click="copyAndOpenLink" block>
          <var-icon name="open-in-new" />
          <span>前往鸿蒙应用商店</span>
        </var-button>
      </var-space>
    </var-paper>

  </var-paper>
</template>

<style scoped>
.software-page {
  padding: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.download-section,
.instructions-section {
  margin-bottom: 16px;
  padding: 16px;
}

h4 {
  margin: 16px 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .software-page {
    padding: 12px;
  }
  
  .page-title {
    font-size: 18px;
  }
}
</style>