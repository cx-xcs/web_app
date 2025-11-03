# LoRaWAN 物联网数据监控平台

这是一个基于 FastAPI + Vue.js + InfluxDB 的 LoRaWAN 设备数据监控平台。

## 系统架构

```
传感器 → LoRa网关 → EMQX → FastAPI后端 → InfluxDB
                                   ↓
                              Vue.js前端
```

## 功能特性

### 后端功能
- 连接 EMQX MQTT 代理，订阅传感器数据
- 解码 Base64 编码的传感器数据
- 将数据存储到 InfluxDB 时序数据库
- 提供 RESTful API 接口
- 支持 WebSocket 实时数据推送

### 前端功能
- 设备列表展示
- 显示每个设备最后一次上传的数据及时间
- 选择时间段查询历史数据
- 数据曲线图表展示
- 自动刷新设备数据（每30秒）

## 数据格式

EMQX 接收到的数据格式：
```json
{
  "applicationID": "1",
  "applicationName": "temp_hum",
  "devEUI": "cacbb80100002362",
  "deviceName": "node1",
  "timestamp": 1759816588,
  "fCnt": 0,
  "fPort": 1,
  "data": "AAAAAEBFa4A=",  // Base64编码的数据
  "data_encode": "base64",
  "adr": true,
  "rxInfo": [...],
  "txInfo": {...}
}
```

## 环境要求

### 后端
- Python 3.8+
- InfluxDB 2.x
- EMQX (或其他 MQTT 代理)

### 前端
- Node.js 20.x+
- npm 或 yarn

## 安装和配置

### 1. 后端配置

1. 进入后端目录并安装依赖：
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. 配置环境变量（创建 `.env` 文件或设置环境变量）：
```
# MQTT配置
MQTT_HOSTNAME=localhost
MQTT_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
MQTT_TOPIC=application/+/device/+/rx

# InfluxDB配置
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_influxdb_token
INFLUXDB_ORG=your_org
INFLUXDB_BUCKET=iot_data
```

3. 配置设备（编辑 `backend/app/devices.json`）：
```json
{
  "cacbb80100002362": {
    "dev_eui": "cacbb80100002362",
    "device_name": "node1",
    "application_name": "temp_hum",
    "data_format": ">ff",
    "data_fields": ["temperature", "humidity"]
  }
}
```

数据格式说明：
- `data_format`: Python struct 格式字符串
  - `>`: 大端字节序
  - `f`: float (4字节)
  - 例如 `">ff"` 表示两个大端浮点数
- `data_fields`: 字段名称列表，与解码后的数据一一对应

4. 启动后端服务：
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端配置

1. 进入前端目录并安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

3. 访问 `http://localhost:5173`

### 3. 生产环境部署

#### 后端
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

或使用 Docker：
```bash
cd backend
docker build -t lorawan-backend .
docker run -d -p 8000:8000 --env-file .env lorawan-backend
```

#### 前端
```bash
cd frontend
npm run build
# 将 dist 目录部署到 Nginx 或其他 Web 服务器
```

## API 接口

### 设备管理
- `GET /api/devices` - 获取所有设备列表
- `GET /api/devices/{dev_eui}` - 获取单个设备信息
- `POST /api/devices` - 创建新设备
- `DELETE /api/devices/{dev_eui}` - 删除设备

### 数据查询
- `GET /api/devices/{dev_eui}/latest` - 获取设备最新数据
- `GET /api/devices/{dev_eui}/history?field=temperature&start=2024-01-01T00:00:00Z&stop=now()` - 获取历史数据

### WebSocket
- `ws://localhost:8000/ws` - 实时数据推送

## 使用说明

1. **查看设备列表**
   - 打开网页，在首页可以看到所有已配置的设备
   - 每个设备显示最后一次上传的数据和时间

2. **查看历史数据**
   - 点击设备行的"查看历史"按钮
   - 选择要查看的数据字段（如温度、湿度）
   - 选择时间范围（默认最近3天）
   - 点击"查询"按钮查看数据曲线

3. **添加新设备**
   - 编辑 `backend/app/devices.json` 文件
   - 添加设备配置信息
   - 重启后端服务

## 故障排查

1. **后端无法连接 EMQX**
   - 检查 MQTT 配置是否正确
   - 确认 EMQX 服务是否运行
   - 检查网络连接和防火墙设置

2. **数据未写入 InfluxDB**
   - 检查 InfluxDB 配置和 token
   - 确认 bucket 是否存在
   - 查看后端日志

3. **前端无法获取数据**
   - 检查后端服务是否运行
   - 确认 API 地址配置正确
   - 查看浏览器控制台错误信息

## 开发说明

### 添加新的数据字段

1. 修改设备配置中的 `data_format` 和 `data_fields`
2. 确保传感器发送的数据格式与配置匹配
3. 重启后端服务

### 自定义图表样式

编辑 `frontend/src/views/Dashboard.vue` 中的 `updateChart` 函数，修改 ECharts 配置。

## 许可证

MIT License
