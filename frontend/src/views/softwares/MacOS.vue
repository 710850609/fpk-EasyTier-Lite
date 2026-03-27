<script setup>
import { ref } from 'vue'
import { Snackbar } from '@varlet/ui'

const architecture = ref('x86_64')
const version = ref('v1.0.0')

const architectures = [
  { label: 'Intel (x86_64)', value: 'x86_64' },
  { label: 'Apple Silicon (arm64)', value: 'arm64' }
]

const versions = ['v1.0.0', 'v0.9.5', 'v0.9.0']

const downloadMacOS = () => {
  Snackbar.success(`开始下载 MacOS ${architecture.value} 架构 ${version.value} 版本 EasyTier`)
}
</script>

<template>
  <var-paper :elevation="2" class="software-page">
    <h2 class="page-title">MacOS 客户端</h2>

    <var-paper :elevation="0" class="download-section">
      <var-cell>下载</var-cell>
      <var-divider />
      <var-space direction="column" :size="[16, 0]">
        <var-row :gutter="16">
          <var-col :span="12" :xs="24">
            <var-select
              v-model="architecture"
              label="架构"
              variant="outlined"
            >
              <var-option
                v-for="arch in architectures"
                :key="arch.value"
                :label="arch.label"
                :value="arch.value"
              />
            </var-select>
          </var-col>
          <var-col :span="12" :xs="24">
            <var-select
              v-model="version"
              label="版本"
              variant="outlined"
            >
              <var-option
                v-for="v in versions"
                :key="v"
                :label="v"
                :value="v"
              />
            </var-select>
          </var-col>
        </var-row>
        <var-button type="primary" size="large" @click="downloadMacOS" block>
          <var-icon name="download" />
          <span>下载 MacOS 版本</span>
        </var-button>
      </var-space>
    </var-paper>

    <var-paper :elevation="0" class="instructions-section">
      <var-cell>使用说明</var-cell>
      <var-divider />
      <var-space direction="column" :size="[16, 0]">
        <h4>安装步骤</h4>
        <var-list>
          <var-list-item>下载对应架构的安装包</var-list-item>
          <var-list-item>打开下载的 .dmg 文件</var-list-item>
          <var-list-item>将 EasyTier 拖拽到 Applications 文件夹</var-list-item>
          <var-list-item>启动 EasyTier 客户端</var-list-item>
          <var-list-item>输入网络名称和密码连接</var-list-item>
        </var-list>

        <h4>截图说明</h4>
        <var-row :gutter="16">
          <var-col :span="12" :xs="24">
            <var-image
              src="https://via.placeholder.com/400x300?text=登录界面"
              fit="cover"
              :radius="8"
            />
            <var-cell>登录界面</var-cell>
          </var-col>
          <var-col :span="12" :xs="24">
            <var-image
              src="https://via.placeholder.com/400x300?text=主界面"
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