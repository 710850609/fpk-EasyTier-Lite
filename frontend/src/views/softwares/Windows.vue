<template>
  <div class="platform-page">
    <var-paper class="download-card" :elevation="2">
      <div class="platform-header">
        <var-icon name="windows" size="48" color="#0078D4" />
        <div class="platform-info">
          <h2>Windows 客户端</h2>
          <p>支持 Windows 10/11 64位系统</p>
        </div>
      </div>

      <var-button 
        type="primary" 
        size="large" 
        block 
        @click="download"
        :loading="downloading"
      >
        <template #default>
          <var-icon name="download" style="margin-right: 8px;" />
          下载最新版 (v1.2.0)
        </template>
      </var-button>

      <div class="version-info">
        <p>更新日期: 2024-01-15</p>
        <p>文件大小: 15.6 MB</p>
        <p>SHA256: a1b2c3d4...</p>
      </div>
    </var-paper>

    <var-paper class="guide-card" :elevation="1">
      <h3>使用说明</h3>
      <div class="screenshot-guide">
        <!-- <img src="/assets/windows-screenshot-1.png" alt="安装步骤1" class="guide-img" />
        <div class="step-desc">1. 下载后双击安装包，按提示完成安装</div>
        
        <img src="/assets/windows-screenshot-2.png" alt="安装步骤2" class="guide-img" />
        <div class="step-desc">2. 在系统托盘找到 EasyTier 图标，右键打开管理界面</div>
        
        <img src="/assets/windows-screenshot-3.png" alt="安装步骤3" class="guide-img" />
        <div class="step-desc">3. 输入网络名称和密码，点击连接即可加入组网</div> -->
      </div>
    </var-paper>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const downloading = ref(false)

const download = () => {
  downloading.value = true
  window.open('https://github.com/EasyTier/EasyTier/releases/download/v1.2.0/easytier-windows-x64.exe', '_blank')
  setTimeout(() => downloading.value = false, 2000)
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

.guide-card {
  padding: 24px;
  border-radius: 16px;
}

.guide-card h3 {
  margin: 0 0 16px 0;
  color: var(--color-on-surface);
}

.screenshot-guide {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.guide-img {
  width: 100%;
  max-width: 600px;
  border-radius: 8px;
  border: 1px solid var(--color-outline-variant);
}

.step-desc {
  font-size: 14px;
  color: var(--color-on-surface-variant);
  margin-bottom: 16px;
}
</style>
