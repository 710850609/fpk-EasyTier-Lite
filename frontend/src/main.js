
import VConsole from 'vconsole';
new VConsole();

import { createApp } from 'vue'
import Varlet from '@varlet/ui'
import './assets/style.css'
import './assets/fnapp.js'
import '@varlet/ui/es/style'
import App from './App.vue'

const app = createApp(App)
app.use(Varlet)
app.mount('#app')
// import('vconsole').then(({ default: VConsole }) => {
//   new VConsole()
// })
// 在应用挂载后初始化 VConsole
// if (import.meta.env.DEV) {
//   import('vconsole').then(({ default: VConsole }) => {
//     new VConsole()
//   })
// }
