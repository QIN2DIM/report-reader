# report-reader

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
   ##
   # You should look at the following URL's in order to grasp a solid understanding
   # of Nginx configuration files in order to fully unleash the power of Nginx.
   # https://www.nginx.com/resources/wiki/start/
   # https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/
   # https://wiki.debian.org/Nginx/DirectoryStructure
   #
   # In most cases, administrators will remove this file from sites-enabled/ and
   # leave it as reference inside of sites-available where it will continue to be
   # updated by the nginx packaging team.
   #
   # This file will automatically load configuration files provided by other
   # applications, such as Drupal or Wordpress. These applications will be made
   # available underneath a path with that package name, such as /drupal8.
   #
   # Please see /usr/share/doc/nginx-doc/examples/ for more detailed examples.
   ##
   
   # Default server configuration - This block should remain for other domains or default handling
   # If YOUR_DOMAIN is your ONLY domain, you might simplify or remove this block
   # but it's safer to keep a default server for any unmatched requests.
   server {
           listen 80 default_server;
           listen [::]:80 default_server;
           server_name _; # Catches requests not matching other server_name directives
           return 404; # Or serve a default page, or redirect to a main site
   }
   
   
   # Configuration for YOUR_DOMAIN - HTTPS block with reverse proxy
   server {
       server_name YOUR_DOMAIN; # managed by Certbot
   
       listen [::]:443 ssl ipv6only=on; # managed by Certbot
       listen 443 ssl; # managed by Certbot
       ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem; # managed by Certbot
       ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem; # managed by Certbot
       include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
       ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
   
       # 反向代理配置
       location / {
           proxy_pass http://127.0.0.1:31313; # 将所有请求转发到 0.0.0.0:31313
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   
   # Configuration for YOUR_DOMAIN - HTTP to HTTPS redirect
   server {
       listen 80;
       listen [::]:80;
       server_name YOUR_DOMAIN;
   
       # 所有的 HTTP 请求都重定向到 HTTPS
       return 301 https://$host$request_uri; # managed by Certbot
   }
   ```

2. **编辑配置文件**

   使用 nano 或 vim 编辑 /etc/nginx/sites-enabled/default 文件。

   ```bash
   sudo nano /etc/nginx/sites-enabled/default
   ```

3. 测试 Nginx 配置

   在重新加载 Nginx 之前，测试配置文件的语法是否正确。

   ```bash
   sudo nginx -t
   ```

   如果一切正常，你会看到：

   ```bash
   nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
   nginx: configuration file /etc/nginx/nginx.conf test is successful
   ```

4. 重新加载 Nginx 服务

   ```bash
   systemctl reload nginx
   ```

   