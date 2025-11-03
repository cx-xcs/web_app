# Linux 部署指南

## 系统要求

- **操作系统**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **Python**: 3.10+
- **InfluxDB**: 2.x
- **EMQX**: 5.x (或其他MQTT Broker)
- **Node.js**: 18+ (用于前端构建)

## 快速部署

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install -y python3 python3-pip git
```

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd web_app
```

### 3. 部署后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 测试运行
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 配置 systemd 服务（后端）

创建 `/etc/systemd/system/lorawan-backend.service`:

```ini
[Unit]
Description=LoRaWAN Web App Backend
After=network.target influxdb.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/web_app/backend
Environment="PATH=/opt/web_app/backend/venv/bin"
ExecStart=/opt/web_app/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable lorawan-backend
sudo systemctl start lorawan-backend
sudo systemctl status lorawan-backend
```

### 5. 部署前端

```bash
cd ../frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 输出在 dist/ 目录
```

### 6. 配置 Nginx

创建 `/etc/nginx/sites-available/lorawan-webapp`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /opt/web_app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/lorawan-webapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker 部署（推荐）

### 1. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MQTT_HOSTNAME=mqtt
      - MQTT_PORT=1883
      - INFLUXDB_URL=http://influxdb:8086
      - INFLUXDB_TOKEN=${INFLUXDB_TOKEN}
      - INFLUXDB_ORG=${INFLUXDB_ORG}
      - INFLUXDB_BUCKET=sensor_data
    depends_on:
      - influxdb
      - mqtt
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  mqtt:
    image: emqx/emqx:5
    ports:
      - "1883:1883"
      - "18083:18083"
    environment:
      - EMQX_NAME=emqx
      - EMQX_HOST=127.0.0.1
    volumes:
      - emqx-data:/opt/emqx/data
      - emqx-log:/opt/emqx/log
    restart: unless-stopped

  influxdb:
    image: influxdb:2
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUXDB_ADMIN_USER}
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_ADMIN_PASSWORD}
      - DOCKER_INFLUXDB_INIT_ORG=${INFLUXDB_ORG}
      - DOCKER_INFLUXDB_INIT_BUCKET=sensor_data
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}
    volumes:
      - influxdb-data:/var/lib/influxdb2
      - influxdb-config:/etc/influxdb2
    restart: unless-stopped

volumes:
  emqx-data:
  emqx-log:
  influxdb-data:
  influxdb-config:
```

### 2. 创建 .env 文件

```bash
INFLUXDB_ADMIN_USER=admin
INFLUXDB_ADMIN_PASSWORD=your-secure-password
INFLUXDB_ORG=my-org
INFLUXDB_TOKEN=your-token-here
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f backend
```

## 性能优化

### 1. 数据库优化

```bash
# InfluxDB配置
# 编辑 /etc/influxdb/config.toml
[data]
  cache-max-memory-size = "1g"
  cache-snapshot-write-cold-duration = "10m"
  
[coordinator]
  write-timeout = "10s"
  max-concurrent-queries = 0
  query-timeout = "0s"
```

### 2. Nginx缓存

```nginx
# 添加到 nginx配置
location /api/devices {
    proxy_pass http://127.0.0.1:8000;
    proxy_cache_valid 200 10s;  # 缓存10秒
    add_header X-Cache-Status $upstream_cache_status;
}
```

### 3. 后端并发

```bash
# 使用 gunicorn + uvicorn workers
pip install gunicorn

# 启动命令
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

## 监控和日志

### 1. 系统监控

```bash
# 安装 Prometheus 和 Grafana
docker run -d --name=prometheus -p 9090:9090 prom/prometheus
docker run -d --name=grafana -p 3000:3000 grafana/grafana
```

### 2. 日志收集

```bash
# 使用 journalctl 查看服务日志
sudo journalctl -u lorawan-backend -f

# 日志轮转
sudo nano /etc/logrotate.d/lorawan
```

```
/var/log/lorawan/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

## 故障排查

### MQTT连接失败

```bash
# 检查MQTT broker状态
sudo systemctl status emqx

# 测试MQTT连接
mosquitto_sub -h localhost -t 'application/temp_hum/device/#' -v

# 查看后端日志
sudo journalctl -u lorawan-backend --since "10 minutes ago"
```

### InfluxDB写入失败

```bash
# 检查InfluxDB状态
sudo systemctl status influxdb

# 测试连接
curl -I http://localhost:8086/ping

# 查看数据
influx query 'from(bucket:"sensor_data") |> range(start:-1h)'
```

### 内存占用过高

```bash
# 查看进程内存
ps aux | grep uvicorn

# 限制内存使用（systemd）
[Service]
MemoryMax=512M
MemoryHigh=384M
```

## 安全加固

### 1. 防火墙配置

```bash
# UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL证书（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. MQTT认证

编辑 backend/.env:
```
MQTT_USERNAME=your-mqtt-user
MQTT_PASSWORD=your-secure-password
```

## 备份策略

### 1. 数据库备份

```bash
#!/bin/bash
# backup-influxdb.sh
DATE=$(date +%Y%m%d_%H%M%S)
influx backup /backup/influxdb_$DATE --bucket sensor_data
find /backup -name "influxdb_*" -mtime +7 -delete
```

### 2. 配置备份

```bash
# 每天备份
0 2 * * * /usr/local/bin/backup-influxdb.sh
```

## 更新部署

```bash
# 拉取最新代码
git pull

# 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart lorawan-backend

# 更新前端
cd ../frontend
npm install
npm run build
```

## 参考资料

- [FastAPI部署文档](https://fastapi.tiangolo.com/deployment/)
- [Nginx反向代理](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [InfluxDB运维指南](https://docs.influxdata.com/influxdb/v2/)
- [EMQX部署文档](https://www.emqx.io/docs/en/latest/deploy/install.html)
