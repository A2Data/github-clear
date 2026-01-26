# 🐳 Docker/NAS 一键部署指南

## 📋 方案说明

### ✅ 为什么选择 Docker 自部署？

1. **彻底告别限流** - 不再依赖公共服务，不会再看到 500/503 错误
2. **一个命令启动** - 使用 Docker Compose 一次性部署所有服务
3. **完全免费** - 运行在你自己的 NAS/服务器上，无需付费
4. **自动重启** - 服务挂了自动重启，无需人工干预
5. **统一访问** - 通过 Nginx 反向代理，所有服务统一入口

---

## 🚀 快速开始 (3 步搞定)

### 步骤 1: 准备环境

确保你的 NAS 或服务器已安装：
- ✅ Docker (版本 20.10+)
- ✅ Docker Compose (版本 2.0+)

#### Synology NAS
1. 打开 **套件中心**
2. 搜索并安装 **Container Manager** (新版) 或 **Docker** (旧版)
3. 完成！

#### QNAP NAS
1. 打开 **App Center**
2. 搜索并安装 **Container Station**
3. 完成！

#### 其他 Linux 服务器
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo apt install docker-compose-plugin

# CentOS/RHEL
sudo yum install -y docker docker-compose-plugin
sudo systemctl start docker
```

---

### 步骤 2: 配置 GitHub Token

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 GitHub Token：
```bash
nano .env  # 或使用任何文本编辑器
```

内容示例：
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**如何获取 GitHub Token？**
1. 访问 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 勾选权限：`repo`, `read:user`
4. 生成并复制 Token

---

### 步骤 3: 一键启动

```bash
# 启动所有服务
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

✅ **完成！** 服务已经在后台运行了。

---

## 🔗 访问你的服务

部署完成后，你有两种访问方式：

### 方式 1: 直接访问各个服务

```bash
# GitHub Stats (基础统计)
http://你的NAS地址:3001/api?username=你的用户名

# Streak Stats (连续打卡)
http://你的NAS地址:3002/?user=你的用户名

# Top Languages (语言统计)
http://你的NAS地址:3001/api/top-langs?username=你的用户名
```

### 方式 2: 统一入口 (推荐)

通过 Nginx 代理，所有服务使用一个端口 `8080`：

```bash
# GitHub Stats
http://你的NAS地址:8080/api?username=你的用户名

# Streak Stats
http://你的NAS地址:8080/streak?user=你的用户名

# Top Languages
http://你的NAS地址:8080/api/top-langs?username=你的用户名
```

---

## ⚙️ 在 GitHub Clear 中配置

1. 访问 http://localhost:8888/settings
2. 找到 **Profile Stats 服务** 配置区
3. 填入以下 URL：

```
GitHub Stats URL: http://你的NAS地址:8080/api
Streak Stats URL: http://你的NAS地址:8080/streak
```

4. 点击 **保存所有配置**
5. 前往 **主页美化** 页面，重新生成 Profile

---

## 🎛️ 高级配置

### 修改端口

如果默认端口冲突，编辑 `docker-compose.yml`：

```yaml
services:
  github-stats:
    ports:
      - "3001:3000"  # 改成你想要的端口，如 "9001:3000"
```

### 添加域名访问

如果你有域名，可以配置反向代理：

1. 在路由器中设置端口转发：`8080 -> NAS内网IP:8080`
2. 配置域名 DNS 解析到你的公网 IP
3. 使用域名访问：`https://stats.yourdomain.com/api?username=xxx`

### 调整缓存时间

编辑 `docker-compose.yml`：

```yaml
environment:
  - CACHE_SECONDS=1800  # 默认 30 分钟，改成你想要的秒数
```

---

## 🛠️ 管理命令

```bash
# 查看运行状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 更新镜像
docker-compose pull
docker-compose up -d

# 查看资源占用
docker stats github-stats streak-stats stats-proxy
```

---

## ❓ 常见问题

### Q1: 启动后访问返回 404

**原因**: 镜像还在拉取中

**解决**:
```bash
# 查看日志
docker-compose logs github-stats

# 等待镜像拉取完成
docker-compose ps
```

### Q2: GitHub Stats 返回 403

**原因**: GitHub Token 配置错误或权限不足

**解决**:
1. 检查 `.env` 文件中的 Token 是否正确
2. 确保 Token 有 `repo` 和 `read:user` 权限
3. 重启服务：`docker-compose restart`

### Q3: Synology NAS 上无法启动

**原因**: Docker Compose 版本太旧

**解决**:
```bash
# SSH 登录 NAS
ssh admin@你的NAS地址

# 安装最新 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### Q4: 端口被占用

**解决**:
```bash
# 查看端口占用
sudo netstat -tulpn | grep :3001

# 修改 docker-compose.yml 中的端口映射
ports:
  - "9001:3000"  # 使用其他端口
```

### Q5: 服务占用太多资源

**解决**: 添加资源限制到 `docker-compose.yml`：

```yaml
services:
  github-stats:
    deploy:
      resources:
        limits:
          cpus: '0.5'      # 限制 CPU 使用率
          memory: 256M     # 限制内存使用
```

---

## 🔒 安全建议

1. **不要公开暴露服务** - 建议仅在内网使用，或配置防火墙规则
2. **定期更新镜像** - 运行 `docker-compose pull && docker-compose up -d`
3. **保护 GitHub Token** - 不要提交 `.env` 文件到 Git 仓库
4. **启用 HTTPS** - 如果公网访问，建议配置 SSL 证书

---

## 📊 对比：Docker vs Vercel

| 特性 | Docker (NAS) | Vercel |
|------|--------------|--------|
| 💰 成本 | 免费（已有NAS） | 免费（有限额） |
| ⚡ 速度 | 内网极快 | 全球CDN |
| 🔒 隐私 | 完全私有 | 数据经过第三方 |
| 🛠️ 维护 | 需要自行管理 | 零维护 |
| 📈 扩展 | 受 NAS 性能限制 | 自动扩展 |
| 🌐 访问 | 需要配置公网访问 | 自动全球访问 |

**推荐**:
- 🏠 **仅自己使用**: Docker (NAS) - 速度快、完全私有
- 🌍 **分享给他人**: Vercel - 全球访问、零维护

---

## 📞 需要帮助？

- 📖 查看完整文档: `STATS_SERVICES.md`
- 🐛 遇到问题: 查看日志 `docker-compose logs`
- 💬 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)

---

## 🎉 总结

✅ **一个命令** 部署所有服务
✅ **统一入口** 通过 Nginx 访问
✅ **自动重启** 服务挂了自动恢复
✅ **完全私有** 数据不经过第三方
✅ **零限流** 再也不会 500 错误

现在就开始享受你自己的 GitHub Stats 服务吧！🚀
