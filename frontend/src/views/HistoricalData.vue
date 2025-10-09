<template>
  <div class="historical-data">
    <n-space vertical>
      <!-- 查询表单 -->
      <n-card>
        <n-grid :cols="4" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Device">
              <n-select
                v-model:value="query.devEui"
                :options="deviceOptions"
                placeholder="Select Device"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Measurement">
              <n-select
                v-model:value="query.measurement"
                :options="measurementOptions"
                placeholder="Select Measurement"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Time Range">
              <n-select
                v-model:value="query.timeRange"
                :options="timeRangeOptions"
                placeholder="Select Time Range"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-space justify="end" align="end" style="height: 100%">
              <n-button type="primary" @click="fetchData">
                Query
              </n-button>
            </n-space>
          </n-grid-item>
        </n-grid>
      </n-card>

      <!-- 图表展示 -->
      <n-card>
        <div ref="chartRef" style="width: 100%; height: 400px"></div>
      </n-card>
    </n-space>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { NSpace, NCard, NGrid, NGridItem, NFormItem, NSelect, NButton } from 'naive-ui'
import { api } from '../api'
import * as echarts from 'echarts'

const query = ref({
  devEui: null,
  measurement: null,
  timeRange: '-1h'
})

const devices = ref([])
const chartRef = ref(null)
let chart = null

// 设备选项
const deviceOptions = ref([])

// 测量项选项（根据选择的设备动态更新）
const measurementOptions = ref([])

// 时间范围选项
const timeRangeOptions = [
  { label: 'Last Hour', value: '-1h' },
  { label: 'Last 6 Hours', value: '-6h' },
  { label: 'Last Day', value: '-1d' },
  { label: 'Last Week', value: '-7d' },
  { label: 'Last Month', value: '-30d' }
]

// 初始化图表
function initChart() {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      type: 'line',
      smooth: true,
      data: []
    }]
  })
  
  // 响应窗口大小变化
  window.addEventListener('resize', () => chart?.resize())
}

// 更新图表数据
function updateChart(data) {
  if (!chart) return
  
  const chartData = data.map(item => ({
    value: [new Date(item.time), item.value]
  }))
  
  chart.setOption({
    series: [{
      data: chartData
    }]
  })
}

// 加载设备列表
async function loadDevices() {
  try {
    const devList = await api.getDevices()
    devices.value = devList
    deviceOptions.value = devList.map(dev => ({
      label: dev.device_name,
      value: dev.dev_eui
    }))
  } catch (error) {
    console.error('Failed to load devices:', error)
  }
}

// 更新测量项选项
function updateMeasurementOptions() {
  const device = devices.value.find(d => d.dev_eui === query.value.devEui)
  if (device) {
    measurementOptions.value = device.data_fields.map(field => ({
      label: field,
      value: field
    }))
  } else {
    measurementOptions.value = []
  }
}

// 获取历史数据
async function fetchData() {
  if (!query.value.devEui || !query.value.measurement) return
  
  try {
    const data = await api.getHistory(
      query.value.devEui,
      query.value.measurement,
      query.value.timeRange
    )
    updateChart(data)
  } catch (error) {
    console.error('Failed to fetch historical data:', error)
  }
}

// 监听设备选择变化
watch(() => query.value.devEui, () => {
  updateMeasurementOptions()
  query.value.measurement = null
})

onMounted(() => {
  loadDevices()
  initChart()
})
</script>

<style scoped>
.historical-data {
  padding: 12px;
}
</style>
