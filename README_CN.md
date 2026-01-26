<div align="center">
  <img src="static/favicon.svg" alt="GitHub Clear" width="100" height="100">
  <h1>GitHub Clear</h1>
  <p><strong>一站式 GitHub/Gitee 仓库管理 & 主页美化工具</strong></p>

  <p>
    <a href="https://github.com/A2Data/github-clear/stargazers"><img src="https://img.shields.io/github/stars/A2Data/github-clear?style=flat-square&logo=github" alt="Stars"></a>
    <a href="https://github.com/A2Data/github-clear/network/members"><img src="https://img.shields.io/github/forks/A2Data/github-clear?style=flat-square&logo=github" alt="Forks"></a>
    <a href="https://github.com/A2Data/github-clear/issues"><img src="https://img.shields.io/github/issues/A2Data/github-clear?style=flat-square&logo=github" alt="Issues"></a>
    <a href="https://github.com/A2Data/github-clear/blob/main/LICENSE"><img src="https://img.shields.io/github/license/A2Data/github-clear?style=flat-square" alt="License"></a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Docker-支持-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  </p>

  <p>
    <a href="#-功能特性">功能特性</a> •
    <a href="#-快速开始">快速开始</a> •
    <a href="#-docker-部署">Docker 部署</a> •
    <a href="#-截图预览">截图预览</a> •
    <a href="#-贡献">贡献</a>
  </p>

  <p>
    <a href="./README.md">🇺🇸 English</a>
  </p>
</div>

---

## ✨ 功能特性

### 📦 仓库管理
- 查看所有仓库（公开/私有/Fork）
- 支持多种排序和筛选方式
- **批量删除**仓库（支持多选）
- **批量归档**仓库
- 退出协作仓库

### 🎨 主页美化 (Profile Generator)
- 可视化编辑，**实时预览**
- **100+ 预设技能徽章**
  - 编程语言：Python, JavaScript, Go, Rust, Java, TypeScript...
  - 大数据：Hadoop, Spark, Hive, Kafka, Flink, Airflow...
  - 数据可视化：Tableau, Power BI, ECharts, Grafana...
  - AI/ML：TensorFlow, PyTorch, Pandas, HuggingFace...
  - 云平台：AWS, GCP, Azure, 阿里云...
- **自定义技能** - 添加任意技能徽章
- **自定义社交链接** - 支持中文标签（Discord, 知乎, B站...）
- **GitHub Stats** 统计卡片（支持自定义服务 URL）
- **Streak Stats** 连续贡献卡片
- **打字机动画** 头部效果
- **30+ 主题** 可选
- 一键部署到 GitHub

### 📊 仪表板
- 账户概览
- 仓库统计
- 异步加载，快速响应

### ⚙️ 设置
- Token 管理（GitHub / Gitee）
- SSH Key 查看
- Stats 服务 URL 配置

---

## 🚀 快速开始

### 预览

首页：
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261855820.png)


仪表板：
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261855596.png)

仓库管理:
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261856073.png)

主页美化:
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261856872.png)


设置：
> Token 配置
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261857535.png)
> 常用命令：
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261857995.png)

### 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip

### 1. 克隆项目

```bash
git clone https://github.com/A2Data/github-clear.git
cd github-clear
```

### 2. 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -e .
```

### 3. 配置 Token

```bash
cp .env.example .env
```

编辑 `.env` 文件:
```env
GITHUB_TOKEN=your_github_token_here
GITEE_TOKEN=your_gitee_token_here  # 可选
```

**获取 Token:**
- GitHub: https://github.com/settings/tokens
  - 需要权限: `repo`, `delete_repo`, `user`
- Gitee: https://gitee.com/profile/personal_access_tokens

### 4. 启动应用

```bash
uv run uvicorn main:app --reload --port 8000
```

访问 http://localhost:8000

---

## 🐳 Docker 部署

### 快速启动

```bash
# 构建镜像
docker build -t github-clear .

# 运行容器
docker run -d -p 8000:8000 \
  -e GITHUB_TOKEN=your_token \
  --name github-clear \
  github-clear
```

### Docker Compose

```bash
# 复制并编辑环境变量文件
cp .env.example .env

# 启动服务
docker-compose up -d
```

详细部署指南请参考 [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

---

## 📸 截图预览

<details>
<summary>点击展开截图</summary>

### 仪表板
快速查看账户概览和最近仓库

### 仓库管理
批量管理、删除、归档仓库

### 主页美化
可视化编辑 Profile README，实时预览

### 设置
Token 和服务配置

</details>

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python, FastAPI, Uvicorn |
| 前端 | Jinja2, HTML5, CSS3, JavaScript |
| API | GitHub REST API, Gitee API |
| 样式 | 自定义 CSS (暗色主题) |
| 部署 | Docker, Docker Compose |

---

## 📁 项目结构

```
github-clear/
├── main.py                   # FastAPI 主入口
├── pyproject.toml            # 项目配置
├── docker-compose.yml        # Docker Compose 配置
├── Dockerfile                # Docker 镜像配置
├── .env.example              # 环境变量示例
├── config/
│   └── settings.py           # 配置管理
├── core/
│   ├── github_api.py         # GitHub API 封装
│   ├── gitee_api.py          # Gitee API 封装
│   ├── profile_generator.py  # Profile README 生成器
│   └── token_manager.py      # Token 管理
├── templates/                # Jinja2 模板
│   ├── base.html             # 基础模板
│   ├── index.html            # 首页
│   ├── dashboard.html        # 仪表板
│   ├── repositories.html     # 仓库管理
│   ├── profile.html          # 主页美化
│   └── settings.html         # 设置
└── static/                   # 静态资源
    ├── css/style.css         # 全局样式
    ├── js/app.js             # JavaScript
    └── favicon.svg           # 网站图标
```

---

## 🌐 多语言支持

GitHub Clear 支持多种语言：
- 🇨🇳 中文
- 🇺🇸 English

可以通过左下角的语言切换按钮进行切换。

---

## ❓ 常见问题

### Q: Profile 预览图片加载失败？

**A:** 这通常是网络问题，不影响实际部署效果。GitHub 会从服务器端加载图片。

解决方案：
1. 直接点击「部署到 GitHub」，实际效果会正常
2. 展开「服务 URL 配置」，点击「测试连接」检查服务可用性
3. 尝试使用镜像服务 URL
4. 开启 VPN 后刷新页面

### Q: 如何自部署 Stats 服务？

**A:** 参考以下项目：
- [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) - 部署到 Vercel
- [github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) - 官方服务: streak-stats.demolab.com

---

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

详细指南请参考 [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件。

---

## 👤 作者

**JackFeng** - [@A2Data](https://github.com/A2Data)

- GitHub: https://github.com/A2Data
- 项目地址: https://github.com/A2Data/github-clear

---

## 🌟 Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=A2Data/github-clear&type=Date)](https://star-history.com/#A2Data/github-clear&Date)

---

<div align="center">
  <p>
    如果这个项目对你有帮助，请给一个 ⭐️ 支持一下！
  </p>
  <p>
    Made with ❤️ by <a href="https://github.com/A2Data">JackFeng</a>
  </p>
</div>
