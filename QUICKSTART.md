# LoRaWAN 物联网监控平台 - 快速启动指南

## 系统已完成重构！

### 主要改进：

1. **后端 API**
   - ✅ 新增 `/api/devices/{dev_eui}/latest` - 获取设备最新数据
   - ✅ 新增 `/api/devices/{dev_eui}/history` - 获取设备历史数据
   - ✅ 支持按时间范围查询历史数据
   - ✅ InfluxDB 查询最新数据功能

2. **前端界面**
   - ✅ 全新的 Dashboard 页面
   - ✅ 设备列表展示（显示设备名称、DevEUI、应用名称）
   - ✅ 实时显示每个设备最后一次上传的数据
   - ✅ 显示数据上传时间
   - ✅ 可选择时间段查询历史数据
   - ✅ ECharts 图表展示数据变化曲线
   - ✅ 自动刷新（每30秒更新一次设备数据）

### 启动步骤：

#### 1. 启动 InfluxDB
确保 InfluxDB 正在运行：
```powershell
# 如果使用 Docker
docker start influxdb
# 或
docker run -d --name influxdb -p 8086:8086 influxdb:latest
```

#### 2. 启动后端服务
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将运行在: http://localhost:8000
API 文档: http://localhost:8000/docs

#### 3. 启动前端服务
打开新的终端窗口：
```powershell
cd frontend
npm run dev
```

前端将运行在: http://localhost:5173

### 页面功能说明：

#### 设备列表表格
- **设备名称**: 显示设备的友好名称
- **DevEUI**: 设备的唯一标识符
- **应用名称**: 设备所属的应用
- **最新数据**: 实时显示设备上传的最新数据（如温度、湿度等）
- **更新时间**: 数据最后更新的时间
- **操作**: 点击"查看历史"按钮查看历史数据曲线

#### 历史数据查询
1. 点击任一设备的"查看历史"按钮
2. 从下拉菜单选择要查看的数据字段（如 temperature、humidity）
3. 选择时间范围（默认最近3天）
4. 点击"查询"按钮
5. 查看数据随时间变化的曲线图

### 设备配置示例：

编辑 `backend/app/devices.json`：

```json
{
  "cacbb80100002362": {
    "dev_eui": "cacbb80100002362",
    "device_name": "温湿度传感器1号",
    "application_name": "temp_hum",
    "data_format": ">ff",
    "data_fields": ["temperature", "humidity"]
  },
  "cacbb80100002363": {
    "dev_eui": "cacbb80100002363",
    "device_name": "土壤传感器1号",
    "application_name": "soil_monitor",
    "data_format": ">fff",
    "data_fields": ["temperature", "humidity", "moisture"]
  }
}
```

### 数据格式说明：

`data_format` 使用 Python struct 格式：
- `>`: 大端字节序（Big-endian）
- `<`: 小端字节序（Little-endian）
- `f`: 32位浮点数（4字节）
- `d`: 64位浮点数（8字节）
- `i`: 32位整数（4字节）
- `h`: 16位整数（2字节）
- `b`: 8位整数（1字节）

例如：
- `">ff"`: 两个大端浮点数（温度 + 湿度）
- `">fff"`: 三个大端浮点数（温度 + 湿度 + 土壤湿度）
- `">hh"`: 两个大端短整数

### 测试数据：

如果需要测试，可以使用 MQTT 客户端发送测试数据到 EMQX：

```json
{
  "applicationID": "1",
  "applicationName": "temp_hum",
  "devEUI": "cacbb80100002362",
  "deviceName": "node1",
  "timestamp": 1759816588,
  "fCnt": 0,
  "fPort": 1,
  "data": "QkzMzUHMzM0=",
  "data_encode": "base64"
}
```

这个 Base64 数据解码后是两个浮点数：
- temperature: 25.6°C
- humidity: 51.2%

### 下一步：

1. 确保 EMQX、InfluxDB、后端、前端都正常运行
2. 配置你的设备信息
3. 让传感器开始发送数据
4. 在网页上查看实时数据和历史曲线！

### 故障排查：

- 如果设备列表为空：检查 `devices.json` 文件
- 如果没有最新数据：确认 MQTT 数据正在接收，检查后端日志
- 如果图表不显示：检查浏览器控制台是否有错误
- 如果时间格式错误：确认 InfluxDB 中有数据

祝使用愉快！🎉
