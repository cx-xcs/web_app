<template>
  <div class="dashboard">
    <n-grid :x-gap="12" :y-gap="12" cols="1 s:2 m:3">
      <!-- 实时数据卡片 -->
      <n-grid-item v-for="device in devices" :key="device.dev_eui">
        <n-card :title="device.device_name">
          <template #header-extra>
            Last update: {{ formatTime(device.timestamp) }}
          </template>
          <n-space vertical>
            <n-statistic v-for="(value, key) in device.data" :key="key" :label="key">
              {{ formatValue(value, key) }}
            </n-statistic>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { NGrid, NGridItem, NCard, NSpace, NStatistic } from 'naive-ui'
import { createWebSocket } from '../api'

const devices = ref({})
let ws = null

// 格式化时间戳
function formatTime(timestamp) {
  if (!timestamp) return '-'
  return new Date(timestamp * 1000).toLocaleTimeString()
}

// 格式化数值
function formatValue(value, key) {
  if (typeof value !== 'number') return value
  
  // 根据字段名添加单位
  const units = {
    temperature: '°C',
    humidity: '%',
    pressure: 'hPa',
    rssi: 'dBm'
  }
  
  return `${value.toFixed(2)}${units[key] || ''}`
}

// WebSocket 处理函数
function handleWebSocketMessage(event) {
  const data = JSON.parse(event.data)
  devices.value[data.dev_eui] = {
    device_name: data.device_name,
    timestamp: data.timestamp,
    data: data.data
  }
}

onMounted(() => {
  // 创建 WebSocket 连接
  ws = createWebSocket()
  ws.onmessage = handleWebSocketMessage
})

onUnmounted(() => {
  // 关闭 WebSocket 连接
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.dashboard {
  padding: 12px;
}
</style>
