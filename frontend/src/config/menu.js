/**
 * 菜单配置
 * 统一维护应用的所有菜单项
 */

// 使用 import.meta.glob 预加载所有视图组件（包括子目录）
const viewModules = import.meta.glob('../views/**/*.vue')

// 菜单树结构（每个节点单行）
export const menuTree = [
  { key: 'nodes', label: '节点', icon: 'format-list-checkbox', title: '节点管理', component: 'Nodes' },
  { key: 'config', label: '配置', icon: 'bookmark-outline', title: '配置管理', component: 'Config' },
  { key: 'software', label: '应用', icon: 'shopping-outline', title: '软件下载',
    children: [
      { key: 'softwares-windows', label: 'Windows', icon: './asserts/windows.svg', component: 'softwares/Windows' },
      { key: 'softwares-android', label: 'Android', icon: './asserts/android.svg', component: 'softwares/Android' },
      { key: 'softwares-macos', label: 'MacOS', icon: './asserts/mac.svg', component: 'softwares/MacOS' },
      { key: 'softwares-ios', label: 'IOS', icon: './asserts/ios.svg', component: 'softwares/IOS' },
      { key: 'softwares-harmonyos', label: '鸿蒙', icon: './asserts/harmony.svg', component: 'softwares/HarmonyOS' },
      { key: 'softwares-linux', label: 'Linux', icon: './asserts/linux.svg', component: 'softwares/Linux' },
    ]
  },
  { key: 'settings', label: '设置', icon: 'cog-outline', title: '系统设置', component: 'Settings' }
]

// 扁平化菜单树
const flattenMenuTree = (items) => {
  const result = []
  items.forEach(item => {
    result.push(item)
    if (item.children) {
      result.push(...flattenMenuTree(item.children))
    }
  })
  return result
}

// 组件映射表（从菜单树构建）
// 只处理叶子节点（没有 children 的菜单项）
const buildComponentMap = () => {
  const map = {}
  const flatMenus = flattenMenuTree(menuTree)
  flatMenus.forEach(item => {
    // 只有叶子节点（没有子菜单）且配置了 component 才加入映射
    if (!item.children && item.component) {
      const modulePath = `../views/${item.component}.vue`
      if (viewModules[modulePath]) {
        map[item.key] = viewModules[modulePath]
      }
    }
  })
  return map
}

export const componentMap = buildComponentMap()

export default menuTree
