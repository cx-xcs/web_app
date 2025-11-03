# WisGate OS MQTT主题配置指南

## 当前问题
- 网关发布的主题：`application/temp_hum/device/${dev_eui}/rx`
- 实际收到的主题：`application/temp_hum/device/${dev_eui}/rx`（未替换）
- 期望的主题：`application/temp_hum/device/cacbb80100002364/rx`

## 解决方案

### 步骤1：登录网关Web界面
1. 访问：https://192.168.230.1
2. 登录账号密码

### 步骤2：定位MQTT配置（按优先级尝试）

#### 选项A：应用级别配置（最可能）
```
路径：LoRa → Application → temp_hum → Integration
或者：应用 → temp_hum → 集成配置
```

查找字段：
- **Uplink Topic Template** (上行主题模板)
- **MQTT Topic Pattern** (MQTT主题模式)
- **Publish Topic** (发布主题)

#### 选项B：全局MQTT设置
```
路径：LoRa → Network Server → MQTT Bridge
或者：系统 → MQTT配置
```

#### 选项C：集成设置
```
路径：LoRa → Integration → MQTT Integration
```

### 步骤3：修改主题模板

**原配置（错误）：**
```
application/temp_hum/device/${dev_eui}/rx
```

**尝试以下配置（按顺序）：**

1. **首选** - Chirpstack标准格式：
   ```
   application/temp_hum/device/{dev_eui}/rx
   ```

2. **备选** - 紧凑格式：
   ```
   application/temp_hum/device/{deveui}/rx
   ```

3. **备选** - 大写格式：
   ```
   application/temp_hum/device/{DevEUI}/rx
   ```

4. **如果网关是RAK7268/7258系列**：
   ```
   application/{application_id}/device/{dev_eui}/rx
   ```

### 步骤4：保存并验证

1. 点击 **Save & Apply** 保存配置
2. 可能需要重启 LoRa Network Server 或重启网关
3. 触发设备上行
4. 在测试脚本中检查主题是否正确：
   ```powershell
   python "d:\Raspberry pico2\web_app\test_mqtt.py"
   ```

**期望输出：**
```
📨 收到消息:
  主题: application/temp_hum/device/cacbb80100002364/rx  ← 注意这里
  DevEUI: cacbb80100002364
```

## 如果找不到配置选项

### 方案A：查看网关系统日志
```
路径：System → Logs → LoRa Network Server
```
查找关键字：`mqtt`, `publish`, `topic`

### 方案B：SSH登录网关（高级）
```bash
ssh root@192.168.230.1
# 查找配置文件
find /etc -name "*mqtt*" -o -name "*lora*"
```

### 方案C：保持现状，修改后端订阅

如果网关配置确实无法修改，后端已经配置为订阅 `application/temp_hum/device/#`，
这会匹配所有子主题，包括 `${dev_eui}`。

但需要修改后端代码，从payload中的 `devEUI` 字段提取设备ID，而不是从主题中解析。

## 常见网关MQTT主题格式参考

### Chirpstack格式（推荐）
```
上行：application/{application_id}/device/{dev_eui}/event/up
下行：application/{application_id}/device/{dev_eui}/command/down
```

### TheThingsNetwork格式
```
上行：v3/{application_id}/devices/{dev_eui}/up
下行：v3/{application_id}/devices/{dev_eui}/down/push
```

### 自定义简化格式
```
上行：app/{application_name}/device/{dev_eui}/rx
下行：app/{application_name}/device/{dev_eui}/tx
```

## 变量语法对照表

| 语法 | 说明 | 支持平台 | 状态 |
|------|------|----------|------|
| `${var}` | Shell风格 | Bash脚本 | ❌ 网关通常不支持 |
| `{var}` | 标准花括号 | Chirpstack, TTN | ✅ 推荐 |
| `%s` | printf风格 | 老版本固件 | ⚠️ 已过时 |
| `{{var}}` | 双花括号 | Jinja2模板 | ❌ 网关不支持 |
| `$var` | 直接引用 | - | ❌ 不推荐 |

## 验证配置是否成功

运行测试脚本后，正确的输出应该是：
```
✅ 成功连接到 MQTT Broker!
✅ 已订阅主题: application/temp_hum/device/+/rx

📨 收到消息:
  主题: application/temp_hum/device/cacbb80100002362/rx  ← 实际设备ID
  DevEUI: cacbb80100002362
  数据: Qp0mUUCC+NM=

📨 收到消息:
  主题: application/temp_hum/device/cacbb80100002364/rx  ← 实际设备ID
  DevEUI: cacbb80100002364
  数据: QGKCxj1Cs/ZBpAAAQi2Zmg==
```

注意 **主题** 字段应该包含实际的16位十六进制设备ID，而不是 `${dev_eui}` 字符串。
