import './assets/main.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import router from './router'
import naive from 'naive-ui'

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(router)
app.use(naive)

// Mount app
app.mount('#app')
