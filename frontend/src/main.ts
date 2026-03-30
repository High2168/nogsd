/**
 * Vue应用入口文件
 * 初始化Vue应用、插件、全局配置
 *
 * 作者: 刘怀仁
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'

// 样式文件
import './assets/styles/main.css'

// 创建Vue应用实例
const app = createApp(App)

// 注册Pinia状态管理
app.use(createPinia())

// 注册路由
app.use(router)

// 注册Element Plus组件库
app.use(ElementPlus, {
  locale: zhCn,  // 中文语言包
})

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 挂载应用
app.mount('#app')
