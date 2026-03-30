# report-reader

A fast markdown document viewer built with Go. Fetches remote markdown files and renders them as styled HTML.

## Usage

```
# With URL parameter (auto-fetch and render)
http://localhost:31313/?url=https://example.com/document.md

# Without URL parameter (shows input form)
http://localhost:31313/
```

## Build & Run

```bash
go build -o report-reader .
./report-reader
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_READER_PORT` | `31313` | Server listen port |
| `FETCH_TIMEOUT` | `30` | HTTP fetch timeout in seconds |
| `TLS_SKIP_VERIFY` | `true` | Skip TLS certificate verification |

## Docker

```bash
docker compose -f docker/docker-compose.yaml up -d
```

## Quick start

### Ubuntu 部署依赖

1. 更新包列表

   ```bash
   apt update
   ```

2. 安装 Nginx

   ```bash
   apt install nginx
   ```

3. 安装 Certbot

   ```bash
   apt install certbot python3-certbot-nginx
   ```

4. 运行 Certbot 命令

   ```bash
   certbot --nginx -d YOUR_DOMAIN
   ```

### 配置 Nginx 反代

1. 参考配置，将 YOUR_DOMAIN 替换

   ```nginx
   server {
           listen 80 default_server;
           listen [::]:80 default_server;
           server_name _;
           return 404;
   }

   server {
       server_name YOUR_DOMAIN; # managed by Certbot

       listen [::]:443 ssl ipv6only=on; # managed by Certbot
       listen 443 ssl; # managed by Certbot
       ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem; # managed by Certbot
       ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem; # managed by Certbot
       include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
       ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

       location / {
           proxy_pass http://127.0.0.1:31313;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }

   server {
       listen 80;
       listen [::]:80;
       server_name YOUR_DOMAIN;
       return 301 https://$host$request_uri; # managed by Certbot
   }
   ```

2. **编辑配置文件**

   ```bash
   sudo nano /etc/nginx/sites-enabled/default
   ```

3. 测试 Nginx 配置

   ```bash
   sudo nginx -t
   ```

4. 重新加载 Nginx 服务

   ```bash
   systemctl reload nginx
   ```
