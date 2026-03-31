<template>
  <div class="config-page">
    <var-paper class="config-section" :elevation="1">
      <div class="section-header">
        <var-icon name="cog" size="24" color="var(--color-primary)" />
        <span class="section-title">{{ fastSettingMode ? '快速设置' : '基础设置' }}</span>
      </div>
      
      <var-form ref="form" :disabled="false">
        <var-input
          v-model="config.network_identity.network_name"
          placeholder="网络名称"
          :rules="[(v) => !!v || '网络名称不能为空']"
        >
          <template #prepend-icon>
            <var-icon name="wifi" />
          </template>
          <template #label>网络名称</template>
        </var-input>

        <var-input
          v-model="config.network_identity.network_secret"
          placeholder="网络密码"
          type="password"
        >
          <template #prepend-icon>
            <var-icon name="lock-outline" />
          </template>
          <template #label>网络密码</template>
        </var-input>

        <var-input
          v-if="!fastSettingMode"
          v-model="config.ipv4"
          placeholder="IPv4"
        >
          <template #prepend-icon>
            <var-icon name="pin-outline" />
          </template>
          <template #label>IPv4 网段</template>
        </var-input>

        
        <span v-if="fastSettingMode" style="font-size: 12px; color: var(--color-warning); margin-top: 8px;"> 将使用动态社区节点用于发现组网节点。如不想用，请刷新页面重新选择正常模式设置，并输入公共节点 </span>
        <var-select
          v-if="!fastSettingMode"
          v-model="config.peer"
          multiple
          placeholder="公共节点"
          :chip="true"
        >
          <var-cell v-for="peer in ['1']"  icon="tag" title="peer">
            <template #>
              <var-input placeholder="输入公共节点" size="small" v-model="customPeer" />
            </template>
            <template #extra>
              <var-button type="primary" size="small" @click="addPeer">添加</var-button>
            </template>
          </var-cell>
          <var-option 
            v-for="peer in publicPeerOptions"
            :key="peer.uri"
            :label="peer.label || peer.uri"
            :value="peer.uri"
          />
        </var-select>
      </var-form>
    </var-paper>

    <!-- 高级设置 -->
    <var-collapse v-if="!fastSettingMode" v-model="flagsOpen" class="flags-section" :class="`var-elevation--2`">
      <var-collapse-item name="flags">
        <template #title>
          <div class="collapse-title">
            <var-icon name="cog" size="24" color="var(--color-primary)" />
            <span class="section-title">高级设置</span>
          </div>
        </template>        
        <div class="flags-content">
          <!-- 功能开关 -->
          <div class="feature-section">
            <div class="section-subtitle">功能开关</div>
            <div class="feature-grid">
              <div 
                v-for="feature in featureSwitches" 
                :key="feature.key"
                class="feature-item"
              >
                <var-checkbox v-model="config.flags[feature.key]">
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
              v-model="config.hostname"
              placeholder="留空默认为主机名"
              variant="outlined"
            />
          </div>

          <!-- 子网代理CIDR -->
          <div class="input-section">
            <div class="section-subtitle">子网代理CIDR</div>
            <var-select
              v-if="!fastSettingMode"
              v-model="config.proxy_network"
              multiple
              placeholder="子网网段"
              variant="outlined"
              :chip="true"
            >
              <var-cell icon="tag">
                <template #>
                  <var-input placeholder="格式: 192.168.1.1/24 或 192.168.1.1/32 等" size="small" v-model="customProxyNetwork" />
                </template>
                <template #extra>
                  <var-button type="primary" size="small" @click="addProxyNetwork">添加</var-button>
                </template>
              </var-cell>
              <var-option 
                v-for="(e, index) in config.proxy_network"
                :key="index"
                :label="e"
                :value="e"
              />
            </var-select>
            <!-- <var-input
              v-model="config.proxy_network"
              placeholder="例如：10.0.0.0/24, 输入后在下拉框中选择生效"
              variant="outlined"
            /> -->
          </div>

          <!-- 监听端口 -->
          <!-- <div class="input-section">
            <div class="section-subtitle">监听端口</div>
            <var-input
              v-model="listenPortStr"
              type="number"
              placeholder="15888"
              variant="outlined"
            />
          </div> -->

          <!-- MTU 大小 -->
          <!-- <div class="input-section">
            <div class="section-subtitle">MTU 大小</div>
            <var-input
              v-model="mtuStr"
              type="number"
              placeholder="1380"
              variant="outlined"
            />
          </div> -->
        </div>
      </var-collapse-item>
    </var-collapse>

    <div class="actions">
       <var-space justify="center" :size="[40, 40]">
         <var-button type="primary" size="normal" block auto-loading @click="saveConfig">
            <var-icon name="checkbox-marked-circle" style="margin-right: 8px;" />
           保存并重启 
         </var-button>
         <var-button type="primary" size="normal" block @click="downloadConfig" v-if="!fastSettingMode">
            <var-icon name="download" style="margin-right: 8px;" />
           导出配置
         </var-button>
       </var-space>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, inject } from 'vue'
import toast from '../components/toast.js'
import { api } from '../utils/api.js'

// 注入快速设置模式
const fastSettingMode = inject('fastSettingMode', ref(false))
const publicPeerOptions = ref([
  // 'tcp://easytier.public.com:11010',
  // 'udp://easytier.public.com:11011',
  // 'wss://easytier.public.com:11012'
])
const customPeer = ref('')
const customProxyNetwork = ref('')

const flagsOpen = ref([])
const form = ref(null)

const config = ref({
  "hostname": "",
  "dhcp": true,
  "ipv4": '10.0.0.0',
  "network_identity": {
    "network_name": '',
    "network_secret": '',
  },
  "rpc_portal": "",
  "listeners": [
    "tcp://0.0.0.0:11010",
    "udp://0.0.0.0:11010",
    "wg://0.0.0.0:11011",
    // "ws://0.0.0.0:11011",
  ],
  "peer": [],
  // 功能开关
  "flags": {
    "bind_device": true,
    "multi_thread": true,
    "enable_kcp_proxy": true,
    "private_mode": true,
  },
  // 子网代理
  "proxy_network": []
})

// 功能开关列表
const featureSwitches = [
  { key: 'latency_first', label: '开启延迟优先模式', tooltip: '优先选择延迟最低的连接路径' },
  { key: 'multi_thread', label: '启用多线程', tooltip: '启用多线程处理，提高性能' },
  { key: 'private_mode', label: '启用私有模式', tooltip: '启用私有模式，限制节点发现' },
  { key: 'enable_kcp_proxy', label: '启用 KCP 代理', tooltip: '使用 KCP 协议进行数据传输，提高弱网环境下的稳定性' },
  { key: 'enable_quic_proxy', label: '启用 QUIC 代理', tooltip: '使用 QUIC 协议进行代理传输' },
  { key: 'disable_kcp_input', label: '禁用 KCP 输入', tooltip: '关闭 KCP 协议的入站连接' },
  { key: 'disable_quic_input', label: '禁用 QUIC 输入', tooltip: '关闭 QUIC 协议的入站连接' },
  { key: 'disable_tcp_hole_punching', label: '禁用 TCP 打洞', tooltip: '关闭 TCP 协议的 NAT 打洞功能' },
  { key: 'disable_udp_hole_punching', label: '禁用 UDP 打洞', tooltip: '关闭 UDP 协议的 NAT 打洞功能' },
  { key: 'disable_sym_hole_punching', label: '禁用对称 NAT 打洞', tooltip: '关闭对称型 NAT 的打洞功能' },  
  { key: 'use_smoltcp', label: '使用用户态协议站', tooltip: '使用用户态TCP/IP协议栈，避免系统防火墙问题无法子网代理或KCP代理' },
  { key: 'proxy_forward_by_system', label: '系统转发', tooltip: '启用系统级 IP 转发' },
  { key: 'p2p_only', label: '仅 P2P', tooltip: '只允许 P2P 连接，不使用中继' },
  { key: 'disable_p2p', label: '禁用 P2P', tooltip: '关闭点对点直连功能，所有流量通过中继' },
  { key: 'enable_exit_node', label: '启用出口节点', tooltip: '允许此节点作为网络的出口' },
  { key: 'enable_encryption', label: '禁用加密', tooltip: '关闭数据传输加密，提高性能但降低安全性' },
  { key: 'enable_ipv6', label: '禁用 IPv6', tooltip: '关闭 IPv6 支持' },
  { key: 'no_tun', label: '无 TUN 模式', tooltip: '不使用 TUN 设备。' },
  { key: 'accept_dns', label: '启用魔法 DNS', tooltip: '启用特殊的 DNS 解析功能' },
  { key: 'relay_all_peer_rpc', label: '转发 RPC 包', tooltip: '允许转发 RPC 数据包' },
  { key: 'bind_device', label: '仅使用物理网卡', tooltip: '只使用物理网卡进行通信，排除虚拟网卡' },
  { key: 'user_stack', label: '使用用户态协议栈', tooltip: '使用用户态网络协议栈代替内核协议栈' },
]

// 监听端口字符串（用于输入框）
const listenPortStr = computed({
  get: () => String(config.value.flags.listen_port),
  set: (val) => {
    config.value.flags.listen_port = val ? parseInt(val, 10) : 0
  }
})

// MTU 字符串（用于输入框）
const mtuStr = computed({
  get: () => String(config.value.flags.mtu),
  set: (val) => {
    config.value.flags.mtu = val ? parseInt(val, 10) : 0
  }
})

const addPeer = () => {
  const peer = customPeer.value
  if (!peer) {
    return
  }
  publicPeerOptions.value.unshift({ uri: peer , label: peer })
  config.value.peer.unshift(peer)
  customPeer.value = ''
}

const addProxyNetwork = () => {
  const proxy = customProxyNetwork.value
  if (!proxy) {
    return
  }
  config.value.proxy_network.unshift(proxy)
  customProxyNetwork.value = ''
}

const saveConfig = async () => {
  const valid = await form.value.validate()
  if (!valid) return

  return new Promise((resolve, reject) => {
    let data = {...config.value, isFastConfig: fastSettingMode.value};
    data.peer = data.peer.map(e => ({uri: e}))
    data.proxy_network = data.proxy_network.map(e => ({cidr: e}))
    api.configs.save(data).then(res => {
      toast.success('配置保存成功')
      resolve()
    }).catch(err => {
      toast.error('保存失败: ' + err.message)
      reject(err)
    })
  })
}

const downloadConfig = () => {
  const url = api.configs.getDownloadUrl();
  window.open(url, '_blank')
}

onMounted(async () => {
  // 加载公共节点
  api.configs.publicPeers().then(data => {
    publicPeerOptions.value = data.data
  })
  api.configs.get().then(data => {
    const json = data.data
    json.hostname = json.hostname || null
    json.peer = (json.peer || []).map(e => e.uri)
    json.proxy_network = (json.proxy_network || []).map(e => e.cidr)
    config.value = json
  })
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

.flags-section {
  margin-bottom: 16px;
  border-radius: 16px;
  overflow: hidden;
  background: var(--color-surface-container) !important;
}

:deep(.flags-section .var-collapse-item) {
  border-radius: 16px;
  overflow: hidden;
  background: var(--color-surface-container) !important;
}

::deep(.flags-section .var-paper) {
  border-radius: 16px;
  background: var(--color-surface-container) !important;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.flags-content {
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

/* Select Chip 样式统一 */
:deep(.var-chip) {
  background: var(--color-primary-container) !important;
  color: var(--color-on-primary-container) !important;
}

:deep(.var-chip__close) {
  color: var(--color-on-primary-container) !important;
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
