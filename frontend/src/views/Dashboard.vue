<template>
  <div class="dashboard">
    <n-space vertical :size="20">
      <n-card title="设备列表">
        <template #header-extra>
          <n-button type="primary" size="small" @click="openAddModal">添加设备</n-button>
        </template>
        <n-data-table
          :columns="deviceColumns"
          :data="devicesWithData"
          :loading="loading"
          :pagination="pagination"
        />
      </n-card>

      <!-- 新增/编辑设备弹窗 -->
      <n-modal v-model:show="showAdd" :auto-focus="false">
        <n-card :title="isEditing ? '编辑设备' : '新增设备'" size="small" style="max-width: 560px;">
          <n-form :model="addForm" label-width="100">
            <n-form-item label="DevEUI">
              <n-input v-model:value="addForm.dev_eui" placeholder="16位十六进制，如 cacbb80100002362" :disabled="isEditing" />
            </n-form-item>
            <n-form-item label="设备名称">
              <n-input v-model:value="addForm.device_name" placeholder="如 room1" />
            </n-form-item>
            <n-form-item label="应用名称">
              <n-input v-model:value="addForm.application_name" placeholder="如 temp_hum" />
            </n-form-item>
            <n-form-item label="数据格式">
              <n-input v-model:value="addForm.data_format" placeholder=">ff 表示2个float" />
            </n-form-item>
            <n-form-item label="数据字段">
              <n-input v-model:value="addForm.data_fields_csv" placeholder="逗号分隔，如 temperature,humidity" />
            </n-form-item>
          </n-form>
          <template #footer>
            <n-space justify="end">
              <n-button @click="showAdd=false">取消</n-button>
              <n-button type="primary" @click="submitAdd" :loading="adding">保存</n-button>
            </n-space>
          </template>
        </n-card>
      </n-modal>

      <n-card v-if="selectedDevice" :title="`历史数据 - ${selectedDevice.device_name} (${selectedDevice.dev_eui})`">
        <template #header-extra>
          <n-button size="small" @click="closeHistory">关闭</n-button>
        </template>
        <n-space vertical>
          <n-space align="center">
            <span style="font-weight: 500;">环境数据:</span>
            <n-select
              v-model:value="selectedField"
              :options="fieldOptions"
              placeholder="选择数据字段"
              style="width: 200px"
            />
            <span style="font-weight: 500;">时间段:</span>
            <!-- 单日历：同一时刻仅弹出一个 -->
            <n-date-picker
              v-model:value="startDate"
              v-model:show="startOpen"
              type="date"
              clearable
              format="yyyy-MM-dd"
              :is-date-disabled="disableStart"
              placeholder="开始日期"
              style="width: 160px"
              @update:value="onStartPicked"
            />
            <span>至</span>
            <n-date-picker
              v-model:value="endDate"
              v-model:show="endOpen"
              type="date"
              clearable
              format="yyyy-MM-dd"
              :is-date-disabled="disableEnd"
              placeholder="结束日期"
              style="width: 160px"
              @update:value="onEndPicked"
            />
            <n-button type="primary" @click="loadHistoryData">
              查询
            </n-button>
            <n-button @click="loadAllData">
              查询所有数据
            </n-button>
          </n-space>
          
          <div ref="chartRef" style="width: 100%; height: 400px;"></div>
        </n-space>
      </n-card>
    </n-space>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, h, nextTick } from 'vue'
import { NButton, NTag, useMessage } from 'naive-ui'
import { api } from '../api'
import * as echarts from 'echarts'

const message = useMessage()
const loading = ref(false)
const devices = ref([])
const devicesData = ref({})
const selectedDevice = ref(null)
const selectedField = ref(null)

// 新增/编辑设备弹窗
const showAdd = ref(false)
const adding = ref(false)
const isEditing = ref(false)
const editingDevEui = ref('')
const addForm = ref({
  dev_eui: '',
  device_name: '',
  application_name: 'temp_hum',
  data_format: '>ff',
  data_fields_csv: 'temperature,humidity'
})

// 开始/结束日期（时间戳，毫秒）
const startDate = ref(Date.now() - 30 * 24 * 60 * 60 * 1000)
const endDate = ref(Date.now())
// 仅弹一个日历：受控显示
const startOpen = ref(false)
const endOpen = ref(false)

const chartRef = ref(null)
let chart = null

const pagination = {
  pageSize: 10
}

const deviceColumns = [
  {
    title: '设备名称',
    key: 'device_name',
    width: 150
  },
  {
    title: 'DevEUI',
    key: 'dev_eui',
    width: 200
  },
  {
    title: '应用名称',
    key: 'application_name',
    width: 120
  },
  {
    title: '最新数据',
    key: 'latest_data',
    width: 300,
    render: (row) => {
      const data = devicesData.value[row.dev_eui]
      if (!data) {
        return h(NTag, { type: 'warning' }, { default: () => '暂无数据' })
      }
      
      // 提取数据字段（排除 dev_eui, device_name, timestamp）
      const excludeKeys = ['dev_eui', 'device_name', 'timestamp']
      const dataEntries = Object.entries(data).filter(([key]) => !excludeKeys.includes(key))
      
      if (dataEntries.length === 0) {
        return h(NTag, { type: 'warning' }, { default: () => '暂无数据' })
      }
      
      // 使用标签形式显示数据，更美观
      return h('div', { style: 'display: flex; gap: 8px; flex-wrap: wrap;' },
        dataEntries.map(([key, value]) => {
          return h(NTag, { 
            type: 'info',
            size: 'small'
          }, { 
            default: () => `${key}: ${typeof value === 'number' ? value.toFixed(2) : value}` 
          })
        })
      )
    }
  },
  {
    title: '更新时间',
    key: 'last_update',
    width: 180,
    render: (row) => {
      const data = devicesData.value[row.dev_eui]
      if (!data || !data.timestamp) {
        return '-'
      }
      return new Date(data.timestamp).toLocaleString('zh-CN')
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) => {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            onClick: () => selectDevice(row)
          },
          { default: () => '查看历史' }
        ),
        h(
          NButton,
          {
            size: 'small',
            onClick: () => openEditModal(row)
          },
          { default: () => '编辑' }
        )
      ])
    }
  }
]

const devicesWithData = computed(() => {
  return devices.value.map(device => ({
    ...device,
    latest_data: devicesData.value[device.dev_eui]
  }))
})

const fieldOptions = computed(() => {
  if (!selectedDevice.value) return []
  return selectedDevice.value.data_fields.map(field => ({
    label: field,
    value: field
  }))
})

const openAddModal = () => {
  isEditing.value = false
  editingDevEui.value = ''
  addForm.value = {
    dev_eui: '',
    device_name: '',
    application_name: 'temp_hum',
    data_format: '>ff',
    data_fields_csv: 'temperature,humidity'
  }
  showAdd.value = true 
}

const openEditModal = (device) => {
  isEditing.value = true
  editingDevEui.value = device.dev_eui
  addForm.value = {
    dev_eui: device.dev_eui,
    device_name: device.device_name,
    application_name: device.application_name,
    data_format: device.data_format,
    data_fields_csv: device.data_fields.join(',')
  }
  showAdd.value = true
}

const submitAdd = async () => {
  const f = addForm.value
  const dev = (f.dev_eui || '').trim().toLowerCase()
  if (!/^([0-9a-f]{16})$/.test(dev)) { 
    message.warning('DevEUI 必须是16位十六进制')
    return 
  }
  if (!f.device_name) { 
    message.warning('请输入设备名称')
    return 
  }
  const fields = (f.data_fields_csv || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)
  if (!fields.length) { 
    message.warning('请至少填写一个数据字段')
    return 
  }
  const payload = {
    dev_eui: dev,
    device_name: f.device_name,
    application_name: f.application_name || 'temp_hum',
    data_format: f.data_format || '>ff',
    data_fields: fields
  }
  try {
    adding.value = true
    if (isEditing.value) {
      // 更新设备
      console.log('更新设备:', editingDevEui.value, payload)
      await api.updateDevice(editingDevEui.value, payload)
      message.success('设备已更新')
    } else {
      // 创建设备
      console.log('创建设备:', payload)
      await api.createDevice(payload)
      message.success('设备已创建')
    }
    showAdd.value = false
    // 重置表单
    addForm.value = {
      dev_eui: '',
      device_name: '',
      application_name: 'temp_hum',
      data_format: '>ff',
      data_fields_csv: 'temperature,humidity'
    }
    await loadDevices()
  } catch (e) {
    console.error('保存失败详情:', e)
    message.error('保存设备失败：' + (e.message || '未知错误'))
  } finally {
    adding.value = false
  }
}

const loadDevices = async () => {
  loading.value = true
  try {
    devices.value = await api.getDevices()
    
    for (const device of devices.value) {
      await loadLatestData(device.dev_eui)
    }
  } catch (error) {
    message.error('加载设备列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadLatestData = async (devEui) => {
  try {
    const data = await api.getDeviceLatestData(devEui)
    devicesData.value[devEui] = data
  } catch (error) {
    console.error(`加载设备 ${devEui} 最新数据失败:`, error)
  }
}

const selectDevice = async (device) => {
  selectedDevice.value = device
  if (device.data_fields && device.data_fields.length > 0) {
    selectedField.value = device.data_fields[0]
  }
  await nextTick()
  loadAllData()
}

const closeHistory = () => {
  selectedDevice.value = null
  if (chart) { chart.dispose(); chart = null }
}

// 禁用规则：
const disableStart = (ts) => {
  if (!endDate.value) return false
  // 开始不能晚于结束
  const endFloor = new Date(new Date(endDate.value).setHours(0, 0, 0, 0)).getTime()
  return ts > endFloor
}
const disableEnd = (ts) => {
  if (!startDate.value) return false
  // 结束不能早于开始
  const startFloor = new Date(new Date(startDate.value).setHours(0, 0, 0, 0)).getTime()
  return ts < startFloor
}

// 选择开始后自动打开结束，确保同一时刻只有一个弹层
const onStartPicked = (val) => {
  // 若结束为空或早于开始，自动对齐
  if (!endDate.value || endDate.value < val) endDate.value = val
  startOpen.value = false
  endOpen.value = true
}
const onEndPicked = () => {
  endOpen.value = false
}

const loadAllData = async () => {
  if (!selectedDevice.value || !selectedField.value) {
    message.warning('请选择数据字段')
    return
  }
  try {
    loading.value = true
    const start = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString()
    const stop = new Date().toISOString()
    const result = await api.getDeviceHistory(
      selectedDevice.value.dev_eui,
      selectedField.value,
      start,
      stop
    )
    if (!result.data || result.data.length === 0) {
      message.warning('没有找到任何数据')
      if (chart) chart.clear()
      return
    }
    updateChart(result.data)
    message.success(`加载了 ${result.data.length} 条数据`)
  } catch (error) {
    message.error('加载历史数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadHistoryData = async () => {
  if (!selectedDevice.value || !selectedField.value) {
    message.warning('请选择数据字段')
    return
  }
  if (!startDate.value || !endDate.value) {
    message.warning('请选择时间范围')
    return
  }
  if (startDate.value > endDate.value) {
    message.warning('开始日期不能大于结束日期')
    return
  }
  try {
    loading.value = true
    // 归零到当天 00:00:00 与 23:59:59.999（UTC）
    const start = new Date(startDate.value); start.setHours(0, 0, 0, 0)
    const stop = new Date(endDate.value); stop.setHours(23, 59, 59, 999)
    const result = await api.getDeviceHistory(
      selectedDevice.value.dev_eui,
      selectedField.value,
      start.toISOString(),
      stop.toISOString()
    )
    if (!result.data || result.data.length === 0) {
      message.warning('该时间段内没有数据')
      if (chart) chart.clear()
      return
    }
    updateChart(result.data)
    message.success(`加载了 ${result.data.length} 条数据`)
  } catch (error) {
    message.error('加载历史数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const updateChart = (data) => {
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  
  // 处理数据，确保时间格式正确
  const chartData = data.map(item => {
    const time = item.time || item.timestamp || item._time
    return [new Date(time), parseFloat(item.value || item._value || 0)]
  }).sort((a, b) => a[0] - b[0]) // 按时间排序
  
  const option = {
    title: {
      text: `${selectedDevice.value.device_name} - ${selectedField.value}`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        if (!params || params.length === 0) return ''
        const date = new Date(params[0].data[0])
        const value = params[0].data[1]
        return `时间: ${date.toLocaleString('zh-CN')}<br/>${selectedField.value}: ${value.toFixed(2)}`
      }
    },
    grid: {
      left: '60px',
      right: '40px',
      bottom: '60px',
      top: '80px'
    },
    xAxis: {
      type: 'time',
      name: '时间',
      nameLocation: 'middle',
      nameGap: 30,
      axisLabel: {
        formatter: '{MM}-{dd}\n{HH}:{mm}',
        rotate: 0
      }
    },
    yAxis: {
      type: 'value',
      name: selectedField.value,
      nameLocation: 'middle',
      nameGap: 40
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        start: 0,
        end: 100
      },
      {
        type: 'inside',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: selectedField.value,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2
        },
        data: chartData
      }
    ]
  }
  
  chart.setOption(option, true) // true 表示不合并，完全替换
}

// 自动刷新：每30秒更新一次设备数据
let refreshTimer = null
const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    devices.value.forEach(device => {
      loadLatestData(device.dev_eui)
    })
  }, 30000) // 30秒
}

onMounted(() => {
  loadDevices()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (chart) {
    chart.dispose()
  }
})
</script>

<style scoped>
.dashboard { padding: 20px; }
</style>
