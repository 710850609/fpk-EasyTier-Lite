<template>
  <div class="config-page">
    <var-paper class="config-section" :elevation="1">
      <div class="section-header">
        <var-icon name="cog" size="24" color="var(--color-primary)" />
        <span class="section-title">基础设置</span>
      </div>
      
      <var-form ref="form" :disabled="false">
        <var-input
          v-model="config.network_name"
          placeholder="网络名称"
          :rules="[(v) => !!v || '网络名称不能为空']"
        >
          <!-- <template #prepend-icon>
            <var-icon name="network-wired" />
          </template> -->
          <template #label>网络名称</template>
        </var-input>

        <var-input
          v-model="config.network_secret"
          placeholder="网络密码"
          type="password"
          autocomplete="new-password"
        >
          <!-- <template #prepend-icon>
            <var-icon name="lock" />
          </template> -->
          <template #label>网络密码</template>
        </var-input>

        <var-input
          v-model="config.ipv4"
          placeholder="IPv4"
        >
          <!-- <template #prepend-icon>
            <var-icon name="globe" />
          </template> -->
          <template #label>IPv4 网段</template>
        </var-input>

        <var-select
          v-model="config.peers"
          multiple
          placeholder="选择公共节点"
        >
          <template #label>公共节点列表</template>
          <var-option 
            v-for="peer in publicPeerOptions" 
            :key="peer"
            :label="peer"
            :value="peer"
          />
        </var-select>
      </var-form>
    </var-paper>

    <!-- 高级设置 -->
    <var-collapse v-model="advancedOpen" class="advanced-section">
      <var-collapse-item name="advanced">
        <template #title>
          <div class="collapse-title">
            <var-icon name="cog" size="24" color="var(--color-primary)" />
            <span class="section-title">高级设置</span>
          </div>
        </template>        
        <div class="advanced-content">
          <!-- 功能开关 -->
          <div class="feature-section">
            <div class="section-subtitle">功能开关</div>
            <div class="feature-grid">
              <div 
                v-for="feature in featureSwitches" 
                :key="feature.key"
                class="feature-item"
              >
                <var-checkbox v-model="config.advanced[feature.key]">
                  {{ feature.label }}
                </var-checkbox>
                <var-tooltip :content="feature.tooltip" v-if="feature.tooltip">
                  <var-icon 
                    name="help-circle-outline" 
                    size="16" 
                    class="help-icon"
                  />
                </var-tooltip>
              </div>
            </div>
          </div>

          <!-- 主机名 -->
          <div class="input-section">
            <div class="section-subtitle">主机名</div>
            <var-input
              v-model="config.advanced.hostname"
              placeholder="留空默认为主机名"
              variant="outlined"
            />
          </div>

          <!-- 子网代理CIDR -->
          <div class="input-section">
            <div class="section-subtitle">子网代理CIDR</div>
            <var-input
              v-model="config.advanced.subnet_cidr"
              placeholder="例如：10.0.0.0/24, 输入后在下拉框中选择生效"
              variant="outlined"
            />
          </div>

          <!-- 监听端口 -->
          <div class="input-section">
            <div class="section-subtitle">监听端口</div>
            <var-input
              v-model="listenPortStr"
              type="number"
              placeholder="15888"
              variant="outlined"
            />
          </div>

          <!-- MTU 大小 -->
          <div class="input-section">
            <div class="section-subtitle">MTU 大小</div>
            <var-input
              v-model="mtuStr"
              type="number"
              placeholder="1380"
              variant="outlined"
            />
          </div>
        </div>
      </var-collapse-item>
    </var-collapse>

    <div class="actions">
       <var-space justify="center" :size="[40, 40]">
         <var-button type="primary" size="large" block @click="saveConfig">
           保存并重启服务
         </var-button> 
         <var-button type="primary" size="large" block @click="downloadConfig">
           导出配置文件
         </var-button>
       </var-space>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import toast from '../components/toast.js'

const newRandomStr = (length = 8) => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

const advancedOpen = ref([])
const form = ref(null)

const config = ref({
  network_name: `fnOS-${newRandomStr()}`,
  network_secret: '',
  ipv4: '10.0.0.0',
  peers: [],
  advanced: {
    // 功能开关
    latency_first: false,
    kcp_proxy: true,
    disable_quic: false,
    physical_only: false,
    relay_rpc: false,
    disable_encryption: false,
    disable_symmetric_nat: false,
    user_stack: false,
    disable_kcp_input: false,
    disable_p2p: false,
    no_tun: false,
    multi_thread: true,
    disable_tcp_hole: false,
    magic_dns: false,
    disable_ipv6: false,
    quic_proxy: false,
    p2p_only: false,
    exit_node: false,
    system_forward: false,
    disable_udp_hole: false,
    private_mode: true,
    // 输入项
    hostname: '',
    subnet_cidr: '',
    listen_port: 15888,
    mtu: 1380
  }
})

// 功能开关列表
const featureSwitches = [
  { key: 'latency_first', label: '开启延迟优先模式', tooltip: '优先选择延迟最低的连接路径' },
  { key: 'kcp_proxy', label: '启用 KCP 代理', tooltip: '使用 KCP 协议进行数据传输，提高弱网环境下的稳定性' },
  { key: 'disable_quic', label: '禁用 QUIC 输入', tooltip: '关闭 QUIC 协议的入站连接' },
  { key: 'physical_only', label: '仅使用物理网卡', tooltip: '只使用物理网卡进行通信，排除虚拟网卡' },
  { key: 'relay_rpc', label: '转发 RPC 包', tooltip: '允许转发 RPC 数据包' },
  { key: 'disable_encryption', label: '禁用加密', tooltip: '关闭数据传输加密，提高性能但降低安全性' },
  { key: 'disable_symmetric_nat', label: '禁用对称 NAT 打洞', tooltip: '关闭对称型 NAT 的打洞功能' },
  { key: 'user_stack', label: '使用用户态协议栈', tooltip: '使用用户态网络协议栈代替内核协议栈' },
  { key: 'disable_kcp_input', label: '禁用 KCP 输入', tooltip: '关闭 KCP 协议的入站连接' },
  { key: 'disable_p2p', label: '禁用 P2P', tooltip: '关闭点对点直连功能，所有流量通过中继' },
  { key: 'no_tun', label: '无 TUN 模式', tooltip: '不使用 TUN 设备，仅提供代理功能' },
  { key: 'multi_thread', label: '启用多线程', tooltip: '启用多线程处理，提高性能' },
  { key: 'disable_tcp_hole', label: '禁用 TCP 打洞', tooltip: '关闭 TCP 协议的 NAT 打洞功能' },
  { key: 'magic_dns', label: '启用魔法 DNS', tooltip: '启用特殊的 DNS 解析功能' },
  { key: 'disable_ipv6', label: '禁用 IPv6', tooltip: '关闭 IPv6 支持' },
  { key: 'quic_proxy', label: '启用 QUIC 代理', tooltip: '使用 QUIC 协议进行代理传输' },
  { key: 'p2p_only', label: '仅 P2P', tooltip: '只允许 P2P 连接，不使用中继' },
  { key: 'exit_node', label: '启用出口节点', tooltip: '允许此节点作为网络的出口' },
  { key: 'system_forward', label: '系统转发', tooltip: '启用系统级 IP 转发' },
  { key: 'disable_udp_hole', label: '禁用 UDP 打洞', tooltip: '关闭 UDP 协议的 NAT 打洞功能' },
  { key: 'private_mode', label: '启用私有模式', tooltip: '启用私有模式，限制节点发现' }
]

// 监听端口字符串（用于输入框）
const listenPortStr = computed({
  get: () => String(config.value.advanced.listen_port),
  set: (val) => {
    config.value.advanced.listen_port = val ? parseInt(val, 10) : 0
  }
})

// MTU 字符串（用于输入框）
const mtuStr = computed({
  get: () => String(config.value.advanced.mtu),
  set: (val) => {
    config.value.advanced.mtu = val ? parseInt(val, 10) : 0
  }
})

const publicPeerOptions = [
  'tcp://easytier.public.com:11010',
  'udp://easytier.public.com:11011',
  'wss://easytier.public.com:11012'
]

const saveConfig = async () => {
  const valid = await form.value.validate()
  if (!valid) return
  
  // 调用 API 保存配置
  // await fetch('/api/config', { method: 'POST', body: JSON.stringify(config.value) })
  console.log(JSON.parse(JSON.stringify(config.value)))
  toast.info(`功能开发中...`)
}

const downloadConfig = () => {
  toast.info(`功能开发中...`)
}

onMounted(async () => {
  // 加载现有配置
  // const response = await fetch('/api/config')
  // config.value = await response.json()
})
</script>

<style scoped>
.config-page {
  padding: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.config-section {
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 16px;
  background: var(--color-surface-container) !important;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.advanced-section {
  margin-bottom: 16px;
  border-radius: 16px;
  overflow: hidden;
  background: var(--color-surface-container) !important;
}

:deep(.advanced-section .var-collapse-item) {
  border-radius: 16px;
  overflow: hidden;
  background: var(--color-surface-container) !important;
}

::deep(.advanced-section .var-paper) {
  border-radius: 16px;
  background: var(--color-surface-container) !important;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.advanced-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 8px 0;
}

.section-subtitle {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 12px;
}

.feature-section {
  margin-bottom: 8px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.help-icon {
  color: var(--color-primary);
  cursor: pointer;
  transition: color 0.2s;
}

.help-icon:hover {
  color: var(--color-info);
}

.input-section {
  display: flex;
  flex-direction: column;
}

.actions {
  margin-top: 24px;
}

:deep(.var-form) {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

:deep(.var-collapse-item__content) {
  padding: 8px 16px 16px;
}

/* 输入框文字颜色 */
:deep(.var-input__input) {
  color: var(--color-text);
}

:deep(.var-input__placeholder) {
  color: var(--color-text-disabled);
}

:deep(.var-input__label) {
  color: var(--color-text);
}

/* 选择框文字颜色 */
:deep(.var-select__label) {
  color: var(--color-text);
}

:deep(.var-select__placeholder) {
  color: var(--color-text-disabled);
}

/* 复选框文字颜色 */
:deep(.var-checkbox__text) {
  color: var(--color-text);
}

/* 折叠面板标题 */
:deep(.var-collapse-item__header) {
  color: var(--color-text);
}

:deep(.var-collapse-item__title) {
  color: var(--color-text);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
