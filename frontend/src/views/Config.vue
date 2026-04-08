<template>
  <div class="config-page">
    <var-form ref="form">
      <var-paper class="config-section" :elevation="1">
        <div class="section-header">
          <var-icon name="cog" size="24" color="var(--color-primary)" />
          <span class="section-title">{{ fastSettingMode ? '快速设置' : '基础设置' }}</span>
        </div>
        
          <!-- 网络名称 + 网络密码 一行 -->
          <div class="input-row">
            <var-input
              v-model="config.network_identity.network_name"
              placeholder="网络名称"
              :rules="[(v) => !!v || '网络名称不能为空']"
              blur-color="var(--color-primary)"
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
              blur-color="var(--color-primary)"
            >
              <template #prepend-icon>
                <var-icon name="lock-outline" />
              </template>
              <template #label>网络密码</template>
            </var-input>
          </div>
          
          <span v-if="fastSettingMode" style="font-size: 12px; color: var(--color-warning); margin-top: 8px;"> 将使用动态社区节点用于发现组网节点。如不想用，请刷新页面重新选择正常模式设置，并输入初始节点 </span>
          <var-select
            v-if="!fastSettingMode"
            v-model="config.peer"
            multiple
            placeholder="初始节点"
            :chip="true"
            blur-color="var(--color-primary)"
          >
            <var-cell icon="tag-outline" title="peer">
              <template #>
                <var-input placeholder="输入初始节点" size="small" v-model="customPeer" blur-color="var(--color-primary)" />
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

          <!-- 主机名 + 虚拟IPv4 一行 -->
          <div class="input-row">
            <!-- 主机名 -->
            <div class="input-section">
              <div class="section-subtitle">主机名</div>
              <var-input
                v-model="config.hostname"
                placeholder="留空默认为主机名"
                variant="outlined"
                size="small"
              />
            </div>

            <!-- 虚拟IPv4 -->
            <div class="input-section">
              <div class="section-subtitle">虚拟IPv4</div>
              <var-input
                v-model="config.ipv4"
                placeholder="固定虚拟IPv4"
                variant="outlined"
                size="small"
              />
            </div>
          </div>

          <!-- TUN接口名称 + 监听地址 一行 -->
          <div class="input-row">
            <!-- TUN接口名称 -->
            <div class="input-section">
              <div class="section-subtitle">TUN接口名称
                <var-tooltip content="当多个网络同时使用相同的TUN接口名称时，将会在设置TUN的IP时产生冲突" :offset-x="160">
                  <var-icon 
                    name="help-circle-outline" 
                    size="16" 
                    class="help-icon"
                  />
                </var-tooltip>
              </div>
              <var-input
                v-model="config.flags.dev_name"
                placeholder="留空自动生成随机名称"
                variant="outlined"
                size="small"
              />
            </div>
            <div class="input-section">
              <div class="section-subtitle">MTU
                <var-tooltip content="TUN设备的MTU，默认加密: 1360，不加密: 1380。取值范围 400 ~ 1380" :offset-x="160">
                  <var-icon 
                    name="help-circle-outline" 
                    size="16" 
                    class="help-icon"
                  />
                </var-tooltip>
              </div>
              <var-input
                v-model="mtuStr"
                type="number"
                :rules="(v) => (v === '' || v >= 400 && v <= 1380) || 'MTU值超出范围[400, 1380]'"
                placeholder="留空默认加密:1360, 不加密:1380"
                variant="outlined"
                size="small"
              />
            </div>
          </div>

          <div class="input-row">
            <div class="input-section">
              <div class="section-subtitle">线程数
                <var-tooltip content="仅当开启多线程时生效，取值必须大于2" :offset-x="60">
                  <var-icon 
                    name="help-circle-outline" 
                    size="16" 
                    class="help-icon"
                  />
                </var-tooltip>
              </div>
              <var-input
                v-model="multiThreadCountStr"
                placeholder="留空默认为2"
                variant="outlined"
                type="number"
                :rules="(v) => (v === '' || v >= 2) || '线程数必须大于等于2'"
                size="small"
              />
            </div>
            <div class="input-section">
              <div class="section-subtitle">加密算法</div>
              <var-select
              v-model="config.flags.encryption_algorithm"
              placeholder="留空默认aes-gcm"
              variant="outlined"
              :chip="true"
              size="small"
            >
              <var-option 
                v-for="(e, index) in encryptionAlgorithmList"
                :key="index"
                :label="e"
                :value="e"
              />
            </var-select>
            </div>
          </div>

          <div class="input-row">
            <!-- 仅转发白名单网络 -->
            <div class="input-section">
              <div class="section-subtitle">转发白名单网络                
                <var-tooltip content="仅转发白名单网络的流量，支持通配*符字符串。多个网络名称间可以使用英文空格间隔" :offset-x="60">
                  <var-icon 
                    name="help-circle-outline" 
                    size="16" 
                    class="help-icon"
                  />
                </var-tooltip>
              </div>
              <var-input
                v-model="config.flags.relay_network_whitelist"
                multiple
                placeholder="网络名称，支持通配*符字符串"
                variant="outlined"
                :chip="true"
                size="small"
              >
              </var-input>
            </div>
            <!-- 子网代理CIDR -->
            <div class="input-section">
              <div class="section-subtitle">子网代理CIDR</div>
              <var-select
                v-model="config.proxy_network"
                multiple
                placeholder="子网网段"
                variant="outlined"
                :chip="true"
                size="small"
              >
                <var-cell icon="tag-outline">
                  <template #>
                    <var-input placeholder="格式: 192.168.1.1/24 或 192.168.1.1/32 等" size="small" v-model="customProxyNetwork" blur-color="var(--color-primary)" />
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
            </div>            
          </div>

          <div class="input-row">
            <div class="input-section">
              <div class="section-subtitle">默认协议</div>
              <var-select
                v-model="config.flags.default_protocol"
                placeholder="默认协议"
                variant="outlined"
                :chip="true"
                size="small"
              >
                <var-option 
                  v-for="(e, index) in defaultProtocolList"
                  :key="index"
                  :label="e.label"
                  :value="e.value"
                />
              </var-select>
            </div>            
          </div>
          
          <!-- 监听地址 -->
          <div class="input-section">
            <div class="section-subtitle">监听地址
              <var-tooltip content="部分协议需要较高版本支持，具体可加ET群咨询" :offset-x="50">
                <var-icon 
                  name="help-circle-outline" 
                  size="16" 
                  class="help-icon"
                />
              </var-tooltip>
            </div>
            <var-select
              v-model="config.listeners"
              multiple
              placeholder="监听地址"
              variant="outlined"
              :chip="true"
              size="small"
            >
              <var-cell icon="tag-outline">
                <template #>
                  <var-input placeholder="自定义监听" size="small" v-model="customListener" blur-color="var(--color-primary)" />
                </template>
                <template #extra>
                  <var-button type="primary" size="small" @click="addListener">添加</var-button>
                </template>
              </var-cell>
              <var-option 
                v-for="(e, index) in listenerOptions"
                :key="index"
              :label="e"
              :value="e"
            />
          </var-select>
        </div>
      </div>
    </var-collapse-item>
  </var-collapse>
      </var-form>


    <!-- 操作按钮 -->
    <div class="actions">
       <var-space :size="[20, 8]" justify="space-around">
         <!-- <var-button type="primary" size="normal" block @click="uploaddConfig" v-if="!fastSettingMode">
            <var-icon name="upload"/>
            导入配置
         </var-button> -->
        <var-button style="min-width: 180px;" type="primary" size="normal" block auto-loading @click="saveConfig">
            <var-icon name="checkbox-marked-circle"/>
            保存重启 
        </var-button>
        <var-button style="min-width: 180px;" type="primary" size="normal" block @click="openCodePage" auto-loading v-if="!fastSettingMode">
          <var-icon name="tag"/>
          编辑文件
        </var-button>
        <var-button style="min-width: 180px;" type="primary" size="normal" block @click="downloadConfig" v-if="!fastSettingMode">
          <var-icon name="download"/>
          导出配置
        </var-button>
       </var-space>
    </div>

    <!-- 编辑配置弹窗 -->
     <var-popup
       v-model:show="showCodePage"
       class="code-editor-popup"
       :close-on-click-overlay="false"
     >
      <div class="code-editor-container">
        <div class="code-editor-header">
          <span class="editor-title">编辑配置</span>
          <var-space>
            <var-button type="primary" size="mini" round @click="saveToml" auto-loading>
              <var-icon name="check"/>                
            </var-button>
            <var-button type="default" size="mini" round @click="showCodePage = false">
              <var-icon name="window-close"/>               
            </var-button>
          </var-space>
        </div>
        <div class="code-editor-content">
          <CodeEditor v-model="configToml" language="toml" style="height: calc(96vh - 60px);" />
        </div>
      </div>
     </var-popup>
  </div>
</template>

<script setup>
import toast from '../components/toast.js'
import { api } from '../utils/api.js'
import CodeEditor from '../components/CodeEditor.vue'

// 注入快速设置模式
const fastSettingMode = inject('fastSettingMode', ref(false))
const publicPeerOptions = ref([])
const customPeer = ref('')
const customProxyNetwork = ref('')
const customListener = ref('')
const flagsOpen = ref([])
const form = ref(null)
const showCodePage = ref(false)
const configToml = ref('')
const encryptionAlgorithmList = ref(['aes-gcm','xor','chacha20','aes-gcm','aes-gcm-256','openssl-aes128-gcm','openssl-aes256-gcm','openssl-chacha20'])
const defaultProtocolList = ref([ {'label': '默认','value': ''}, {'label': 'tcp','value': 'tcp'}, {'label': 'udp','value': 'udp'}, {'label': 'quic','value': 'quic'}, {'label': 'wg','value': 'wg'}, {'label': 'ws','value': 'ws'}, {'label': 'wss','value': 'wss'}, {'label': 'faketcp','value': 'faketcp'}])

const config = ref({
  "hostname": undefined,
  "dhcp": true,
  "ipv4": '',
  "network_identity": {
    "network_name": '',
    "network_secret": '',
  },
  "rpc_portal": "",
  "listeners": [
    "tcp://0.0.0.0:11010",
    "udp://0.0.0.0:11010",
    "quic://0.0.0.0:11013",
  ],
  "peer": [],
  // 功能开关
  "flags": {
    "bind_device": true,
    "multi_thread": true,
    "enable_kcp_proxy": true,
    "private_mode": true,
    "enable_encryption": true,
    "enable_ipv6": true,
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
  { key: 'use_smoltcp', label: '使用用户态协议栈', tooltip: '使用用户态TCP/IP协议栈，避免系统防火墙问题无法子网代理或KCP代理' },
  { key: 'proxy_forward_by_system', label: '系统转发', tooltip: '启用系统级 IP 转发' },
  { key: 'p2p_only', label: '仅 P2P', tooltip: '只允许 P2P 连接，不使用中继' },
  { key: 'disable_p2p', label: '禁用 P2P', tooltip: '关闭点对点直连功能，所有流量通过中继' },
  { key: 'enable_exit_node', label: '启用出口节点', tooltip: '允许此节点作为网络的出口' },
  { key: 'enable_encryption', label: '启用加密', tooltip: '开启数据传输加密，提高安全性但性能降低' },
  { key: 'enable_ipv6', label: '启用 IPv6', tooltip: '开启 IPv6 支持' },
  { key: 'no_tun', label: '无 TUN 模式', tooltip: '不使用 TUN 设备。' },
  { key: 'accept_dns', label: '启用魔法 DNS', tooltip: '魔法 DNS 目前仅支持在 Windows 和 MacOS 上自动配置系统 DNS，Linux 上需要手动配置 DNS 服务器为 100.100.100.101 才可正常使用' },
  { key: 'relay_all_peer_rpc', label: '转发 RPC 包', tooltip: '允许转发 RPC 数据包' },
  { key: 'bind_device', label: '仅使用物理网卡', tooltip: '只使用物理网卡进行通信，排除虚拟网卡' },
  { key: 'user_stack', label: '使用用户态协议栈', tooltip: '使用用户态网络协议栈代替内核协议栈' },
]

const listenerOptions = ref([
    "tcp://0.0.0.0:11010",
    "udp://0.0.0.0:11010",
    "wg://0.0.0.0:11011",
    "ws://0.0.0.0:11011",
    "wss://0.0.0.0:11012",  
    "quic://0.0.0.0:11012",
    "faketcp://0.0.0.0:11013",
])

const addListener = () => {
  const listener = customProxyNetwork.value
  if (!listener) {
    return
  }
  config.value.listeners.unshift(listener)
  customProxyNetwork.value = ''
}

// MTU 字符串（用于输入框）
const mtuStr = computed({
  get: () => config.value.flags.mtu !== null && config.value.flags.mtu !== undefined ? String(config.value.flags.mtu) : '',
  set: (val) => {
    config.value.flags.mtu = val === '' ? null : parseInt(val, 10)
  }
})

// 线程数字符串（用于输入框）
const multiThreadCountStr = computed({
  get: () => config.value.flags.multi_thread_count !== null && config.value.flags.multi_thread_count !== undefined ? String(config.value.flags.multi_thread_count) : '',
  set: (val) => {
    config.value.flags.multi_thread_count = val === '' ? null : parseInt(val, 10)
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

const ensureInt = (str) => {
  if (str && typeof str === 'string') {
    return parseInt(str, 10)
  }
  return str
}

const saveConfig = async () => {
  const valid = await form.value.validate()
  if (!valid) return

  return new Promise((resolve, reject) => {
    let data = {...config.value};
    data.peer = data.peer.map(e => ({uri: e}))
    data.proxy_network = data.proxy_network.map(e => ({cidr: e}))
    data.dhcp = !data.ipv4 || !(data.ipv4.trim())
    if (data.flags.enable_ipv6 === undefined) {
      data.flags.enable_ipv6 = true
    }
    if (data.flags.enable_encryption === undefined) {
      data.flags.enable_encryption = true
    }
    api.configs.save(data).then(res => {
      const restartLoading = toast.loading('保存成功，服务重启中...')
      api.services.restart().then(() => {
        toast.success('服务重启成功')
      }).finally(e => {
        restartLoading.clear()
        resolve()
      })
    }).catch(e => reject(e))
  }).catch(e => reject(e))
}

const downloadConfig = () => {
  const url = api.configs.getDownloadUrl();
  window.open(url, '_blank')
}

const openCodePage = () => {
  return new Promise((resolve, reject) => {
     api.configs.getToml().then(res => {
      configToml.value = res.data
      showCodePage.value = true
      resolve()
    }).catch(e => reject(e))
  })
}

// 从代码编辑器保存配置并关闭
const saveToml = () => {
  return new Promise((resolve, reject) => {
    api.configs.saveToml(configToml.value).then(res => {
      const restartLoading = toast.loading('保存成功，服务重启中...')
      api.services.restart().then(() => {
        toast.success('服务重启成功')
      }).finally(e => {
        loadConfig()
        restartLoading.clear()
        resolve()
      })
    }).catch(e => reject(e))
  });
}

const loadConfig = () => {
  api.configs.get().then(data => {
    const json = data.data
    json.peer = (json.peer || []).map(e => e.uri)
    json.proxy_network = (json.proxy_network || []).map(e => e.cidr)
    if (json.listeners) {
      json.listeners.forEach(e => {
        if (!listenerOptions.value.includes(e)) {
          listenerOptions.value.unshift(e)
        }
      })
    }
    // 兼容处理
    if (json.flags.mtu) {
      json.flags.mtu = ensureInt(json.flags.mtu)
    }
    if (json.flags.multi_thread_count) {
      json.flags.multi_thread_count = ensureInt(json.flags.multi_thread_count)
    }
    // 处理空值时，展示placeholder提示
    config.value = {
      ...config.value,
      ...json,
      hostname: json.hostname || undefined,
      ipv4: json.ipv4 || undefined,
      flags: {
        ...config.value.flags,
        ...json.flags,
        mtu: json.flags?.mtu || undefined,
        multi_thread_count: json.flags?.multi_thread_count || undefined
      }
    }
    console.log(config.value)
  })
}

onMounted(async () => {
  // 加载公共节点
  api.configs.publicPeers().then(data => {
    publicPeerOptions.value = data.data
  })
  loadConfig()
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

/* 两列布局 */
.input-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 600px) {
  .input-row {
    grid-template-columns: 1fr;
  }
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

/* 代码编辑器弹窗样式 - 专用样式 */
.code-editor-popup {
  :deep(.var-popup__content) {
    width: 98vw !important;
    height: 96vh !important;
    max-width: 1600px !important;
    max-height: 1000px !important;
    background: #0d1117 !important;
    border-radius: 16px !important;
    border: 1px solid rgba(48, 54, 61, 0.4) !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6),
                0 0 0 1px rgba(255, 255, 255, 0.03) inset !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    border-radius: 16px 16px 16px 16px !important; 
  }
}

.code-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background: #0d1117;
}

.code-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  background: var(--color-surface-container) !important;
  border-bottom: 1px solid var(--color-outline);
  flex-shrink: 0;
}

.code-editor-header :deep(.var-button--mini) {
  min-width: 24px !important;
  height: 24px !important;
  padding: 0 4px !important;
}

.code-editor-header :deep(.var-button--mini .var-icon) {
  font-size: 16px !important;
}

.editor-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: 0.5px;
}

.code-editor-content {
  padding: 0;
  background: #0d1117;
}

.config-code-block {
  height: 100%;

  :deep(pre) {
    background: #0d1117 !important;
    border-radius: 0 !important;
    border: none !important;
    padding: 24px !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    height: 100% !important;
    margin: 0 !important;
    overflow: auto !important;
  }

  :deep(code) {
    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', 'Monaco', monospace !important;
    font-size: 14px !important;
  }
}

/* 滚动条样式 */
.code-editor-content::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.code-editor-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 5px;
}

.code-editor-content::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #6366f1 0%, #a855f7 100%);
  border-radius: 5px;
  border: 2px solid transparent;
  background-clip: padding-box;
}

.code-editor-content::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .code-editor-popup {
    :deep(.var-popup__content) {
      width: 100vw !important;
      height: 100vh !important;
      max-width: 100vw !important;
      max-height: 100vh !important;
      border-radius: 0 !important;
    }
  }

  .code-editor-header {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .editor-title {
    font-size: 14px;
  }
}
</style>
