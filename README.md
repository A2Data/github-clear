<div align="center">
  <img src="static/favicon.svg" alt="GitHub Clear" width="100" height="100">
  <h1>GitHub Clear</h1>
  <p><strong>All-in-one GitHub/Gitee Repository Manager & Profile Beautifier</strong></p>
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
    <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  </p>

  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-docker-deployment">Docker</a> •
    <a href="#-screenshots">Screenshots</a> •
    <a href="#-contributing">Contributing</a>
  </p>

  <p>
    <a href="./README_CN.md">🇨🇳 中文文档</a>
  </p>
</div>

---

## ✨ Features



### Preview

Front Page：
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261855820.png)


Dashboard：
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261855596.png)

Warehouse Management:
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261856073.png)

Homepage beautification:
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261856872.png)


Set up：
> Token Configuration
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261857535.png)
> Common commands：
![](https://nas.a2data.cn:9002/datascience/2026/01/26/202601261857995.png)


### 📦 Repository Management
- View all repositories (public / private / forked)
- Multiple sorting and filtering options
- **Batch delete** repositories
- **Batch archive** repositories
- Leave collaboration repositories

### 🎨 Profile Beautifier
- Visual editor with **real-time preview**
- **100+ preset skill badges**
  - Programming: Python, JavaScript, Go, Rust, Java, TypeScript...
  - Big Data: Hadoop, Spark, Hive, Kafka, Flink, Airflow...
  - Visualization: Tableau, Power BI, ECharts, Grafana...
  - AI/ML: TensorFlow, PyTorch, Pandas, HuggingFace...
  - Cloud: AWS, GCP, Azure, Alibaba Cloud...
- **Custom skills** - Add any skill badge
- **Custom social links** - Support Chinese labels (Discord, 知乎, Bilibili...)
- **GitHub Stats** card with customizable service URL
- **Streak Stats** contribution card
- **Typing animation** header
- **30+ themes** to choose from
- One-click deploy to GitHub

### 📊 Dashboard
- Account overview
- Repository statistics
- Async loading for fast response

### ⚙️ Settings
- Token management (GitHub / Gitee)
- SSH Key viewer
- Stats service URL configuration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### 1. Clone the repository

```bash
git clone https://github.com/A2Data/github-clear.git
cd github-clear
```

### 2. Install dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 3. Configure Token

```bash
cp .env.example .env
```

Edit `.env` file:
```env
GITHUB_TOKEN=your_github_token_here
GITEE_TOKEN=your_gitee_token_here  # Optional
```

**Get your Token:**
- GitHub: https://github.com/settings/tokens
  - Required scopes: `repo`, `delete_repo`, `user`
- Gitee: https://gitee.com/profile/personal_access_tokens

### 4. Start the application

```bash
uv run uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000

---

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build image
docker build -t github-clear .

# Run container
docker run -d -p 8000:8000 \
  -e GITHUB_TOKEN=your_token \
  --name github-clear \
  github-clear
```

### Docker Compose

```bash
# Copy and edit environment file
cp .env.example .env

# Start services
docker-compose up -d
```

For detailed deployment guide, see [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

---

## 📸 Screenshots

<details>
<summary>Click to expand screenshots</summary>

### Dashboard
Quick overview of your account and recent repositories

### Repository Management
Batch manage, delete, and archive repositories

### Profile Beautifier
Visual editor for Profile README with real-time preview

### Settings
Token and service configuration

</details>

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | Jinja2, HTML5, CSS3, JavaScript |
| API | GitHub REST API, Gitee API |
| Styling | Custom CSS (Dark theme) |
| Deployment | Docker, Docker Compose |

---

## 📁 Project Structure

```
github-clear/
├── main.py                   # FastAPI main entry
├── pyproject.toml            # Project configuration
├── docker-compose.yml        # Docker Compose config
├── Dockerfile                # Docker image config
├── .env.example              # Environment variables example
├── config/
│   └── settings.py           # Settings management
├── core/
│   ├── github_api.py         # GitHub API wrapper
│   ├── gitee_api.py          # Gitee API wrapper
│   ├── profile_generator.py  # Profile README generator
│   └── token_manager.py      # Token management
├── templates/                # Jinja2 templates
│   ├── base.html             # Base template
│   ├── index.html            # Home page
│   ├── dashboard.html        # Dashboard
│   ├── repositories.html     # Repository management
│   ├── profile.html          # Profile beautifier
│   └── settings.html         # Settings
└── static/                   # Static assets
    ├── css/style.css         # Global styles
    ├── js/app.js             # JavaScript
    └── favicon.svg           # Favicon
```

---

## 🌐 i18n Support

GitHub Clear supports multiple languages:
- 🇨🇳 Chinese (中文)
- 🇺🇸 English

Language can be switched using the toggle button in the bottom-left corner.

---

## ❓ FAQ

### Q: Profile preview images fail to load?

**A:** This is usually a network issue and doesn't affect actual deployment. GitHub loads images from the server side.

Solutions:
1. Click "Deploy to GitHub" directly - it will work on GitHub
2. Expand "Service URL Config" and click "Test Connection"
3. Try using mirror service URLs
4. Enable VPN and refresh the page

### Q: How to self-host Stats services?

**A:** See these projects:
- [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) - Deploy to Vercel
- [github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) - Official: streak-stats.demolab.com

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

For detailed guidelines, see [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**JackFeng** - [@A2Data](https://github.com/A2Data)

- GitHub: https://github.com/A2Data
- Project: https://github.com/A2Data/github-clear

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=A2Data/github-clear&type=Date)](https://star-history.com/#A2Data/github-clear&Date)

---

<div align="center">
  <p>
    If you find this project helpful, please consider giving it a ⭐️
  </p>
  <p>
    Made with ❤️ by <a href="https://github.com/A2Data">JackFeng</a>
  </p>
</div>
