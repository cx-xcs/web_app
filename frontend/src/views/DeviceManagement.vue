<template>
  <div class="device-management">
    <n-space vertical>
      <!-- 添加设备按钮 -->
      <n-button type="primary" @click="showModal = true">
        Add Device
      </n-button>

      <!-- 设备列表 -->
      <n-data-table
        :columns="columns"
        :data="devices"
        :pagination="{ pageSize: 10 }"
        :bordered="false"
      />

      <!-- 添加设备对话框 -->
      <n-modal v-model:show="showModal" preset="dialog" title="Add Device">
        <n-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-placement="left"
          label-width="120"
        >
          <n-form-item label="Device EUI" path="dev_eui">
            <n-input v-model:value="formData.dev_eui" placeholder="e.g., cacbb80100002362" />
          </n-form-item>
          <n-form-item label="Device Name" path="device_name">
            <n-input v-model:value="formData.device_name" placeholder="e.g., Temperature Sensor 1" />
          </n-form-item>
          <n-form-item label="Application Name" path="application_name">
            <n-input v-model:value="formData.application_name" placeholder="e.g., temp_hum" />
          </n-form-item>
          <n-form-item label="Data Format" path="data_format">
            <n-input v-model:value="formData.data_format" placeholder="e.g., >ff for two floats" />
          </n-form-item>
          <n-form-item label="Data Fields" path="data_fields">
            <n-dynamic-input
              v-model:value="formData.data_fields"
              placeholder="Enter field name"
              :min="1"
            />
          </n-form-item>
        </n-form>
        <template #action>
          <n-button type="primary" @click="handleAddDevice">
            Add Device
          </n-button>
        </template>
      </n-modal>
    </n-space>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  NSpace,
  NButton,
  NDataTable,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NDynamicInput,
  useMessage
} from 'naive-ui'
import { api } from '../api'

const message = useMessage()
const devices = ref([])
const showModal = ref(false)
const formRef = ref(null)

// 表单数据
const formData = ref({
  dev_eui: '',
  device_name: '',
  application_name: '',
  data_format: '',
  data_fields: []
})

// 表单验证规则
const rules = {
  dev_eui: {
    required: true,
    trigger: ['blur', 'input'],
    message: 'Please enter device EUI'
  },
  device_name: {
    required: true,
    trigger: ['blur', 'input'],
    message: 'Please enter device name'
  },
  application_name: {
    required: true,
    trigger: ['blur', 'input'],
    message: 'Please enter application name'
  },
  data_format: {
    required: true,
    trigger: ['blur', 'input'],
    message: 'Please enter data format'
  },
  data_fields: {
    required: true,
    trigger: ['blur', 'input'],
    message: 'Please add at least one data field'
  }
}

// 表格列定义
const columns = [
  { title: 'Device EUI', key: 'dev_eui' },
  { title: 'Device Name', key: 'device_name' },
  { title: 'Application', key: 'application_name' },
  { title: 'Data Format', key: 'data_format' },
  {
    title: 'Data Fields',
    key: 'data_fields',
    render(row) {
      return row.data_fields.join(', ')
    }
  },
  {
    title: 'Actions',
    key: 'actions',
    render(row) {
      return h(
        NButton,
        {
          type: 'error',
          size: 'small',
          onClick: () => handleDeleteDevice(row.dev_eui)
        },
        { default: () => 'Delete' }
      )
    }
  }
]

// 加载设备列表
async function loadDevices() {
  try {
    devices.value = await api.getDevices()
  } catch (error) {
    message.error('Failed to load devices')
  }
}

// 添加设备
async function handleAddDevice() {
  try {
    await formRef.value?.validate()
    await api.createDevice(formData.value)
    message.success('Device added successfully')
    showModal.value = false
    loadDevices()
    // 重置表单
    formData.value = {
      dev_eui: '',
      device_name: '',
      application_name: '',
      data_format: '',
      data_fields: []
    }
  } catch (error) {
    message.error('Failed to add device')
  }
}

// 删除设备
async function handleDeleteDevice(devEui) {
  try {
    await api.deleteDevice(devEui)
    message.success('Device deleted successfully')
    loadDevices()
  } catch (error) {
    message.error('Failed to delete device')
  }
}

onMounted(() => {
  loadDevices()
})
</script>

<style scoped>
.device-management {
  padding: 12px;
}
</style>
