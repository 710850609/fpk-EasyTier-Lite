<template>
  <div class="main-content">
    <var-app-bar title-position="center" :fixed="false" :safe-area-top="true">
      <template #default>
        节点: 普通 {{ peerCounts.client }} 个,服务器 {{ peerCounts.server }} 个
      </template>
      <template #right>
        <var-menu ref="menuRef">
          <var-button color="transparent" text-color="#fff" round text>
            <var-icon name="menu" :size="24" />
          </var-button>

          <template #menu>
            <!-- 1. 刷新菜单 -->
            <var-cell ripple @click="refreshNetwork">立即刷新</var-cell>
            
            <!-- 2. 显示列菜单 -->
            <var-cell ripple title="显示列" @click="showColumnMenu = !showColumnMenu">
              <template #extra>
                <var-icon name="arrow-right" :size="16" />
              </template>
            </var-cell>
            
            <!-- 3. vconsole菜单 -->
            <var-cell ripple title="vconsole" @click="showVconsoleMenu = !showVconsoleMenu">
              <template #extra>
                <var-icon name="arrow-right" :size="16" />
              </template>
            </var-cell>
          </template>

        </var-menu>
        
        <!-- 显示列二级菜单 -->
        <var-menu-select v-model="showColumns" multiple ref="columnMenuRef" v-model:show="showColumnMenu" position="bottom-left">
          <template #options>
            <var-menu-option v-for="(title, key) in keyTitleMap" :key="key" :label="title" :value="key" @click="handleColumnSelect(key)">
              {{ title }}
            </var-menu-option>
          </template>
        </var-menu-select>
        
        <!-- vconsole二级菜单 -->
        <var-menu-select v-model="vconsoleStatus" ref="vconsoleMenuRef" v-model:show="showVconsoleMenu" position="bottom-left">
          <template #options>
            <var-menu-option label="关闭" value="off" @click="handleVconsoleSelect('off')" />
            <var-menu-option label="开启" value="on" @click="handleVconsoleSelect('on')" />
          </template>
        </var-menu-select>      
      </template>
    </var-app-bar>

    <div class="table-container">
      <table class="network-table">
        <thead>
          <tr>
            <th v-if="showColumns.includes('cidr')">网段</th>
            <th v-if="showColumns.includes('ipv4')">IPv4</th>
            <th v-if="showColumns.includes('hostname')">主机名</th>
            <th v-if="showColumns.includes('cost')">穿透方式</th>
            <th v-if="showColumns.includes('lat_ms')">延迟</th>
            <th v-if="showColumns.includes('loss_rate')">丢包率</th>
            <th v-if="showColumns.includes('rx_bytes')">下载</th>
            <th v-if="showColumns.includes('tx_bytes')">上传</th>
            <th v-if="showColumns.includes('nat_type')">Nat类型</th>
            <th v-if="showColumns.includes('tunnel_proto')">协议</th>
            <th v-if="showColumns.includes('version')">内核版本</th>
            <th v-if="showColumns.includes('id')">id</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="peer in peers" :key="peer.id">
            <td v-if="showColumns.includes('cidr')" >{{ peer.cidr }}</td>
            <td v-if="showColumns.includes('ipv4')" >{{ formatIP(peer) }}</td>
            <td v-if="showColumns.includes('hostname')" >{{ formatHostname(peer) }}</td>
            <td v-if="showColumns.includes('cost')" ><var-chip :type="getCostClass(peer.cost)">{{ formatCost(peer.cost) }}</var-chip></td>
            <td v-if="showColumns.includes('lat_ms')" >{{ peer.lat_ms }}</td>
            <td v-if="showColumns.includes('loss_rate')" >{{ peer.loss_rate }}</td>
            <td v-if="showColumns.includes('rx_bytes')" >{{ formatBytes(peer.rx_bytes) }}</td>
            <td v-if="showColumns.includes('tx_bytes')" >{{ formatBytes(peer.tx_bytes) }}</td>
            <td v-if="showColumns.includes('nat_type')" >{{ formatNatType(peer.nat_type) }}</td>
            <td v-if="showColumns.includes('tunnel_proto')"  v-html="formatTunnelProto(peer.tunnel_proto)"></td>
            <td v-if="showColumns.includes('version')" >{{ peer.version }}</td>
            <td v-if="showColumns.includes('id')" >{{ peer.id }}</td>
          </tr>
        </tbody>
      </table>
      
      <!-- 拖拽刷新按钮 -->
      <!-- <var-fab 
        type="primary" 
        :loading="loading"
        style="position: fixed; bottom: 100px; right: 20px; z-index: 1000;"
        drag
        drag-trigger="click"
      >
       <var-chip type="success"><var-icon name="refresh" 
        @click="refreshNetwork" /></var-chip>
        
      </var-fab> -->
    </div>

    <div v-if="peers.length === 0" class="empty-state">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
        <circle cx="9" cy="7" r="4"></circle>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
      </svg>
      <p>暂无组网信息</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Snackbar, Dialog } from '@varlet/ui'

const peers = ref([])
const loading = ref(false)
const peerCounts = ref({server: 0, client: 0})
const showColumns = ref(['ipv4', 'hostname', 'cost', 'loss_rate', 'rx_bytes', 'tx_bytes', 'nat_type', 'tunnel_proto'])
const vconsoleStatus = ref('off')
const showColumnMenu = ref(false)
const showVconsoleMenu = ref(false)
const menuRef = ref(null)
const columnMenuRef = ref(null)
const vconsoleMenuRef = ref(null)

const keyTitleMap = {
    "cidr": "网段",
    "ipv4": "IPv4",
    "hostname": "主机名",
    "cost": "穿透方式",
    "lat_ms": "延迟",
    "loss_rate": "丢包率",
    "rx_bytes": "下载", 
    "tx_bytes": "上传",
    "nat_type": "Nat类型",
    "tunnel_proto": "协议",
    "id": "id",
    "version": "内核版本"
};

const refreshNetwork = async () => {
  loading.value = true
  try {
    const response = await fetch('/cgi/ThirdParty/EasyTier-Lite/api.cgi/peers/list')
    const text = await response.text()
    const data = JSON.parse(text)
    let peersData = []
    if (Array.isArray(data)) {
      peersData = data
    } else if (data && Array.isArray(data.data)) {
      peersData = data.data
    } else {
      console.error('Unexpected response format:', data)
    }
    peersData.sort((a, b) => {
      const hasIpA = a.ipv4 && a.ipv4.trim() !== ''
      const hasIpB = b.ipv4 && b.ipv4.trim() !== ''
      if (!hasIpA && !hasIpB) return 0
      if (!hasIpA) return 1
      if (!hasIpB) return -1
      return a.ipv4 > b.ipv4
    })
    peers.value = peersData
    peerCounts.value = {
      server: peersData.filter(peer => peer.hostname.startsWith('PublicServer_')).length,
      client: peersData.filter(peer => !peer.hostname.startsWith('PublicServer_')).length,
    }
  } catch (error) {
    console.error('获取组网信息失败:', error)
  } finally {
    loading.value = false
  }
}

const handleColumnSelect = (key) => {
  console.log('选择的列:', key)
}

const handleVconsoleSelect = (status) => {
  console.log('vconsole状态:', status)
}

const formatIP = (peer) => {
  if ((!peer.ipv4 || peer.ipv4 === '') && peer.hostname.startsWith('PublicServer_')) {
    return '服务器';
  }
  return peer.ipv4;
}
const formatHostname = (peer) => {
  if (peer.hostname && peer.hostname.startsWith('PublicServer_')) {
    return peer.hostname.replace('PublicServer_', '');
  }
  return peer.hostname;
}

const getCostClass = (cost) => {
  if (!cost) return ''
  const valueMap = {
    p2p: 'success',
    relay: 'info',
    Local: 'primary',
  }    
  for (const key of Object.keys(valueMap)) {
    if (cost.startsWith(key)) {
      return valueMap[key]
    }
  }
  return cost
}
const formatCost = (cost) => {
  if (!cost) return ''
  const valueMap = {
    p2p: '直连',
    relay: '中继',
    Local: '本地',
  }
  for (const key of Object.keys(valueMap)) {
    if (cost.startsWith(key)) {
      return cost.replace(key, valueMap[key])
    }
  }
  return cost
}

const formatNatType = (natType) => {
  if (!natType) return ''
  const valueMap = {
    'NoPAT': '基础NAT(NoPAT)',
    'NoPat': '基础NAT(NoPat)',
    'FullCone': 'Nat1全锥',
    'Restricted': 'Nat2受限',
    'PortRestricted': 'Nat3端口受限',
    'Symmetric': 'Nat4对称',
    'OpenInternet': '开放互联网',
    'Unknown': '未知',
  }
  return valueMap[natType] || natType
}

const formatTunnelProto = (tunnelProto) => {
  if (!tunnelProto) return ''
  return tunnelProto.replaceAll(',', '<br>')
}

const formatBytes = (bytes) => {
  if (!bytes) return ''
  return bytes
}

onMounted(() => {
  refreshNetwork()
  setInterval(() => {
    refreshNetwork()
  }, 10000);
})
</script>

<style scoped>

.main-content {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-container {
  flex: 1;
  overflow: auto;
  position: relative;
}

.network-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.network-table th,
.network-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
}

.network-table th {
  background: var(--table-header-bg);
  color: var(--table-header-text);
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
}

.network-table td {
  color: var(--text-primary);
}

.network-table td:nth-child(8) {
  white-space: nowrap;
}

.network-table td:nth-child(9) {
  white-space: pre-wrap;
}

.network-table tr:hover td {
  background: var(--table-row-hover);
}

.network-table th:first-child,
.network-table td:first-child {
  position: sticky;
  left: 0;
  background: var(--table-header-bg);
  z-index: 30;
  border-right: 2px solid var(--border-color);
  font-weight: 700;
}

.network-table tr:hover td:first-child {
  background: var(--table-row-hover);
}

.network-table th:first-child {
  z-index: 40;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-online {
  background: rgba(16, 185, 129, 0.1);
  color: var(--status-online);
}

.status-offline {
  background: rgba(239, 68, 68, 0.1);
  color: var(--status-offline);
}

.action-btn {
  padding: 6px 12px;
  margin-right: 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.btn-view {
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-text);
}

.btn-view:hover {
  opacity: 0.8;
}

.btn-edit {
  background: #3b82f6;
  color: white;
}

.btn-edit:hover {
  opacity: 0.8;
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.btn-delete:hover {
  opacity: 0.8;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.empty-state p {
  margin-top: 12px;
  font-size: 1rem;
}

.peer-count {
  text-align: center;
  padding: 8px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
}
</style>
