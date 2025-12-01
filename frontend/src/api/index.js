const API_BASE_URL = 'http://localhost:8000'
const WS_URL = 'ws://localhost:8000/ws'

export const api = {
  // Device Management
  async getDevices() {
    const response = await fetch(`${API_BASE_URL}/api/devices`)
    return response.json()
  },

  async getDevice(devEui) {
    const response = await fetch(`${API_BASE_URL}/api/devices/${devEui}`)
    return response.json()
  },

  async createDevice(device) {
    const response = await fetch(`${API_BASE_URL}/api/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(device)
    })
    return response.json()
  },

  async updateDevice(devEui, device) {
    const response = await fetch(`${API_BASE_URL}/api/devices/${devEui}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(device)
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(`更新失败: ${error}`)
    }
    return response.json()
  },

  async deleteDevice(devEui) {
    await fetch(`${API_BASE_URL}/api/devices/${devEui}`, {
      method: 'DELETE'
    })
  },

  // Get device latest data (获取设备最新数据)
  async getDeviceLatestData(devEui) {
    const response = await fetch(`${API_BASE_URL}/api/devices/${devEui}/latest`)
    return response.json()
  },

  // Get device history (获取设备历史数据)
  async getDeviceHistory(devEui, field, start, stop) {
    const params = new URLSearchParams({
      field,
      start,
      stop
    })
    const response = await fetch(`${API_BASE_URL}/api/devices/${devEui}/history?${params}`)
    return response.json()
  }
}

export function createWebSocket() {
  const ws = new WebSocket(WS_URL)
  
  ws.onopen = () => {
    console.log('WebSocket connected')
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket disconnected')
    // 可以在这里添加重连逻辑
  }
  
  return ws
}
