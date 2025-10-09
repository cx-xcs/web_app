import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import DeviceManagement from '../views/DeviceManagement.vue'
import HistoricalData from '../views/HistoricalData.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/devices',
      name: 'devices',
      component: DeviceManagement
    },
    {
      path: '/history',
      name: 'history',
      component: HistoricalData
    }
  ]
})

export default router
