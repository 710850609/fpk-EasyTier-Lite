<template>
  <var-card title="页面调试">
      <var-cell border>这是单元格</var-cell>

    <var-divider />
    <var-switch v-model="switchVconsole" />    
  </var-card>
  
  <!-- <div class="main-content">
    <div class="tab-content">        
      <h2>配置页面</h2>
      <p>功能开发中...</p>
    </div>
  </div> -->
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { Snackbar, Dialog } from '@varlet/ui'
  

  let vconsoleInstance = null;
  const switchVconsole = ref(false)
  const toggleVconsole = () => {
  if (switchVconsole.value && vconsoleInstance) {
    vconsoleInstance.destroy()
    switchVconsole.value = false
    vconsoleInstance = null
    return
  }
  import('vconsole').then(({ default: VConsole }) => {
    vconsoleInstance = new VConsole()
    switchVconsole.value = true
  })
}

  
</script>

<style scoped>
/* .main-content {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  overflow: hidden;
}

.tab-content {
  padding: 24px;
}

.tab-content h2 {
  color: var(--text-primary);
  margin-bottom: 16px;
}

.tab-content p {
  color: var(--text-secondary);
} */
</style>
