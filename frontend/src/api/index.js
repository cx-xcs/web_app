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

  async deleteDevice(devEui) {
    await fetch(`${API_BASE_URL}/api/devices/${devEui}`, {
      method: 'DELETE'
    })
  },

  // Historical Data
  async getHistory(devEui, measurement, start = '-1h', stop = 'now()') {
    const response = await fetch(
      `${API_BASE_URL}/api/history/${devEui}?measurement=${measurement}&start=${start}&stop=${stop}`
    )
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
