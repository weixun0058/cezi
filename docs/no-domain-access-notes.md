# 无域名阶段临时访问说明

本文档只用于还没有购买或解析域名时的临时验证。当前正式部署已采用 Cloudflare Tunnel，正式流程以项目根目录的 `部署指南.md` 为准。

## 为什么 `http://服务器IP:8000` 访问不了

当前 `deploy/compose.prod.yml` 的端口绑定是：

```yaml
ports:
  - "127.0.0.1:${APP_PORT:-8000}:8000"
```

这表示 Docker 容器只接受服务器本机访问：

```text
http://127.0.0.1:8000
```

公网浏览器访问：

```text
http://服务器IP:8000
```

会失败。这是生产部署的安全设计，不是容器坏了。

## 临时方案一：用服务器 IP 的 80 端口访问

这个方案不需要域名，也不需要暴露 Docker 的 8000 端口。浏览器访问：

```text
http://服务器IP/
```

服务器上安装并配置 Nginx：

```bash
sudo apt install -y nginx
sudo systemctl enable --now nginx
sudo nano /etc/nginx/sites-available/zhugeshensuan-ip
```

写入：

```nginx
server {
    listen 80 default_server;
    server_name _;

    client_max_body_size 1m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
    }

    location /api/lunming/stream {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 120s;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
    }
}
```

启用：

```bash
sudo ln -s /etc/nginx/sites-available/zhugeshensuan-ip /etc/nginx/sites-enabled/zhugeshensuan-ip
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

验证：

```bash
curl --fail http://127.0.0.1:8000/readyz
curl --fail http://127.0.0.1/readyz
```

然后访问：

```text
http://服务器IP/
```

## 临时方案二：SSH 隧道

如果只是自己检查，不想开放任何额外公网入口，在本地 Windows PowerShell 执行：

```powershell
ssh -L 8000:127.0.0.1:8000 root@服务器IP
```

保持 SSH 窗口不关闭，然后本地浏览器访问：

```text
http://127.0.0.1:8000
```

## 不推荐：直接暴露 8000 端口

不建议把 `deploy/compose.prod.yml` 改成公网绑定：

```yaml
ports:
  - "0.0.0.0:8000:8000"
```

这会让应用绕过 Nginx 直接暴露在公网。正式部署应使用 `80/443 -> Nginx -> 127.0.0.1:8000`。
