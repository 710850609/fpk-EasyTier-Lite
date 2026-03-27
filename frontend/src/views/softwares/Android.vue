<script setup>
import { Snackbar } from '@varlet/ui'

const downloadAndroid = () => {
  Snackbar.success('开始下载 Android 版本 EasyTier')
}
</script>

<template>
  <var-paper :elevation="2" class="software-page">
    <h2 class="page-title">安卓客户端</h2>

    <var-paper :elevation="0" class="download-section">
      <var-cell>下载</var-cell>
      <var-divider />
      <var-space direction="column" :size="[16, 0]">
        <var-button type="primary" size="large" @click="downloadAndroid" block>
          <var-icon name="download" />
          <span>下载 Android 版本</span>
        </var-button>
        <var-chip size="small" type="primary">最新版本: v1.0.0</var-chip>
      </var-space>
    </var-paper>

    <var-paper :elevation="0" class="instructions-section">
      <var-cell>使用说明</var-cell>
      <var-divider />
      <var-space direction="column" :size="[16, 0]">
        <h4>安装步骤</h4>
        <var-list>
          <var-list-item>下载 APK 安装包</var-list-item>
          <var-list-item>允许安装来自未知来源的应用</var-list-item>
          <var-list-item>安装 EasyTier 客户端</var-list-item>
          <var-list-item>启动 EasyTier 客户端</var-list-item>
          <var-list-item>输入网络名称和密码连接</var-list-item>
        </var-list>

        <h4>截图说明</h4>
        <var-row :gutter="16">
          <var-col :span="12" :xs="24">
            <var-image
              src="https://via.placeholder.com/300x500?text=登录界面"
              fit="cover"
              :radius="8"
            />
            <var-cell>登录界面</var-cell>
          </var-col>
          <var-col :span="12" :xs="24">
            <var-image
              src="https://via.placeholder.com/300x500?text=主界面"
              fit="cover"
              :radius="8"
            />
            <var-cell>主界面</var-cell>
          </var-col>
        </var-row>
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