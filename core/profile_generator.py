"""Profile README 生成器"""
import re
from typing import Dict, Any, List
from pathlib import Path


class ProfileGenerator:
    """GitHub/Gitee Profile README 生成器"""
    
    # 预定义的技能图标 (使用 shields.io)
    SKILL_ICONS = {
        # ========== 编程语言 ==========
        'python': '![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)',
        'javascript': '![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)',
        'typescript': '![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)',
        'go': '![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)',
        'rust': '![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)',
        'java': '![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)',
        'kotlin': '![Kotlin](https://img.shields.io/badge/Kotlin-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white)',
        'swift': '![Swift](https://img.shields.io/badge/Swift-FA7343?style=for-the-badge&logo=swift&logoColor=white)',
        'cpp': '![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)',
        'c': '![C](https://img.shields.io/badge/C-A8B9CC?style=for-the-badge&logo=c&logoColor=black)',
        'csharp': '![C#](https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=c-sharp&logoColor=white)',
        'php': '![PHP](https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white)',
        'ruby': '![Ruby](https://img.shields.io/badge/Ruby-CC342D?style=for-the-badge&logo=ruby&logoColor=white)',
        'dart': '![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)',
        'shell': '![Shell](https://img.shields.io/badge/Shell-121011?style=for-the-badge&logo=gnu-bash&logoColor=white)',
        'scala': '![Scala](https://img.shields.io/badge/Scala-DC322F?style=for-the-badge&logo=scala&logoColor=white)',
        'r': '![R](https://img.shields.io/badge/R-276DC3?style=for-the-badge&logo=r&logoColor=white)',
        'julia': '![Julia](https://img.shields.io/badge/Julia-9558B2?style=for-the-badge&logo=julia&logoColor=white)',
        'lua': '![Lua](https://img.shields.io/badge/Lua-2C2D72?style=for-the-badge&logo=lua&logoColor=white)',
        'perl': '![Perl](https://img.shields.io/badge/Perl-39457E?style=for-the-badge&logo=perl&logoColor=white)',
        'haskell': '![Haskell](https://img.shields.io/badge/Haskell-5D4F85?style=for-the-badge&logo=haskell&logoColor=white)',
        'elixir': '![Elixir](https://img.shields.io/badge/Elixir-4B275F?style=for-the-badge&logo=elixir&logoColor=white)',
        'clojure': '![Clojure](https://img.shields.io/badge/Clojure-5881D8?style=for-the-badge&logo=clojure&logoColor=white)',

        # ========== 前端框架 ==========
        'react': '![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)',
        'vue': '![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D)',
        'angular': '![Angular](https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white)',
        'svelte': '![Svelte](https://img.shields.io/badge/Svelte-FF3E00?style=for-the-badge&logo=svelte&logoColor=white)',
        'nextjs': '![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)',
        'nuxt': '![Nuxt](https://img.shields.io/badge/Nuxt-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)',
        'tailwind': '![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)',
        'bootstrap': '![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)',
        'sass': '![Sass](https://img.shields.io/badge/Sass-CC6699?style=for-the-badge&logo=sass&logoColor=white)',
        'webpack': '![Webpack](https://img.shields.io/badge/Webpack-8DD6F9?style=for-the-badge&logo=webpack&logoColor=black)',
        'vite': '![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)',
        'jquery': '![jQuery](https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white)',

        # ========== 后端框架 ==========
        'nodejs': '![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)',
        'express': '![Express](https://img.shields.io/badge/Express-000000?style=for-the-badge&logo=express&logoColor=white)',
        'fastapi': '![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)',
        'django': '![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)',
        'flask': '![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)',
        'spring': '![Spring](https://img.shields.io/badge/Spring-6DB33F?style=for-the-badge&logo=spring&logoColor=white)',
        'springboot': '![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white)',
        'rails': '![Rails](https://img.shields.io/badge/Rails-CC0000?style=for-the-badge&logo=ruby-on-rails&logoColor=white)',
        'laravel': '![Laravel](https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white)',
        'nestjs': '![NestJS](https://img.shields.io/badge/NestJS-E0234E?style=for-the-badge&logo=nestjs&logoColor=white)',
        'graphql': '![GraphQL](https://img.shields.io/badge/GraphQL-E10098?style=for-the-badge&logo=graphql&logoColor=white)',
        'grpc': '![gRPC](https://img.shields.io/badge/gRPC-244c5a?style=for-the-badge&logo=google&logoColor=white)',

        # ========== 移动开发 ==========
        'flutter': '![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)',
        'reactnative': '![React Native](https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)',
        'android': '![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)',
        'ios': '![iOS](https://img.shields.io/badge/iOS-000000?style=for-the-badge&logo=ios&logoColor=white)',

        # ========== 数据库 ==========
        'mysql': '![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)',
        'postgresql': '![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)',
        'mongodb': '![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)',
        'redis': '![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)',
        'sqlite': '![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)',
        'oracle': '![Oracle](https://img.shields.io/badge/Oracle-F80000?style=for-the-badge&logo=oracle&logoColor=white)',
        'sqlserver': '![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)',
        'cassandra': '![Cassandra](https://img.shields.io/badge/Cassandra-1287B1?style=for-the-badge&logo=apache-cassandra&logoColor=white)',
        'neo4j': '![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)',
        'dynamodb': '![DynamoDB](https://img.shields.io/badge/DynamoDB-4053D6?style=for-the-badge&logo=amazon-dynamodb&logoColor=white)',

        # ========== 大数据 (Hadoop 生态) ==========
        'hadoop': '![Hadoop](https://img.shields.io/badge/Hadoop-66CCFF?style=for-the-badge&logo=apache-hadoop&logoColor=black)',
        'spark': '![Spark](https://img.shields.io/badge/Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white)',
        'hive': '![Hive](https://img.shields.io/badge/Hive-FDEE21?style=for-the-badge&logo=apache-hive&logoColor=black)',
        'kafka': '![Kafka](https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white)',
        'flink': '![Flink](https://img.shields.io/badge/Flink-E6526F?style=for-the-badge&logo=apache-flink&logoColor=white)',
        'airflow': '![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white)',
        'hbase': '![HBase](https://img.shields.io/badge/HBase-D22128?style=for-the-badge&logo=apache&logoColor=white)',
        'presto': '![Presto](https://img.shields.io/badge/Presto-5890FF?style=for-the-badge&logo=presto&logoColor=white)',
        'elasticsearch': '![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)',
        'clickhouse': '![ClickHouse](https://img.shields.io/badge/ClickHouse-FFCC01?style=for-the-badge&logo=clickhouse&logoColor=black)',
        'databricks': '![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)',
        'snowflake': '![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)',
        'zookeeper': '![Zookeeper](https://img.shields.io/badge/Zookeeper-D22128?style=for-the-badge&logo=apache&logoColor=white)',
        'nifi': '![NiFi](https://img.shields.io/badge/NiFi-017CEE?style=for-the-badge&logo=apache&logoColor=white)',

        # ========== 数据可视化 ==========
        'tableau': '![Tableau](https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white)',
        'powerbi': '![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=power-bi&logoColor=black)',
        'd3js': '![D3.js](https://img.shields.io/badge/D3.js-F9A03C?style=for-the-badge&logo=d3.js&logoColor=white)',
        'echarts': '![ECharts](https://img.shields.io/badge/ECharts-AA344D?style=for-the-badge&logo=apache-echarts&logoColor=white)',
        'plotly': '![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)',
        'grafana': '![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)',
        'matplotlib': '![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=python&logoColor=white)',
        'seaborn': '![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=for-the-badge&logo=python&logoColor=white)',
        'superset': '![Superset](https://img.shields.io/badge/Superset-20A6C9?style=for-the-badge&logo=apache-superset&logoColor=white)',
        'metabase': '![Metabase](https://img.shields.io/badge/Metabase-509EE3?style=for-the-badge&logo=metabase&logoColor=white)',

        # ========== AI/ML/数据科学 ==========
        'tensorflow': '![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)',
        'pytorch': '![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)',
        'openai': '![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)',
        'scikit': '![Scikit-learn](https://img.shields.io/badge/Scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)',
        'pandas': '![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)',
        'numpy': '![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)',
        'keras': '![Keras](https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=keras&logoColor=white)',
        'opencv': '![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)',
        'huggingface': '![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)',
        'jupyter': '![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)',
        'anaconda': '![Anaconda](https://img.shields.io/badge/Anaconda-44A833?style=for-the-badge&logo=anaconda&logoColor=white)',
        'mlflow': '![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)',
        'langchain': '![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)',

        # ========== DevOps & 云平台 ==========
        'docker': '![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)',
        'kubernetes': '![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)',
        'aws': '![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)',
        'gcp': '![GCP](https://img.shields.io/badge/GCP-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)',
        'azure': '![Azure](https://img.shields.io/badge/Azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)',
        'alicloud': '![Alibaba Cloud](https://img.shields.io/badge/Alibaba_Cloud-FF6A00?style=for-the-badge&logo=alibaba-cloud&logoColor=white)',
        'nginx': '![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)',
        'terraform': '![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)',
        'ansible': '![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=for-the-badge&logo=ansible&logoColor=white)',
        'jenkins': '![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)',
        'githubactions': '![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)',
        'gitlab': '![GitLab](https://img.shields.io/badge/GitLab-FCA121?style=for-the-badge&logo=gitlab&logoColor=white)',
        'prometheus': '![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)',
        'helm': '![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)',
        'argocd': '![ArgoCD](https://img.shields.io/badge/ArgoCD-EF7B4D?style=for-the-badge&logo=argo&logoColor=white)',
        'circleci': '![CircleCI](https://img.shields.io/badge/CircleCI-343434?style=for-the-badge&logo=circleci&logoColor=white)',
        'travisci': '![Travis CI](https://img.shields.io/badge/Travis_CI-3EAAAF?style=for-the-badge&logo=travis-ci&logoColor=white)',

        # ========== 消息队列 ==========
        'rabbitmq': '![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)',
        'activemq': '![ActiveMQ](https://img.shields.io/badge/ActiveMQ-D22128?style=for-the-badge&logo=apache&logoColor=white)',
        'pulsar': '![Pulsar](https://img.shields.io/badge/Pulsar-188FFF?style=for-the-badge&logo=apache-pulsar&logoColor=white)',

        # ========== 工具 ==========
        'linux': '![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)',
        'ubuntu': '![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)',
        'centos': '![CentOS](https://img.shields.io/badge/CentOS-262577?style=for-the-badge&logo=centos&logoColor=white)',
        'git': '![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)',
        'github': '![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)',
        'vscode': '![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)',
        'intellij': '![IntelliJ](https://img.shields.io/badge/IntelliJ-000000?style=for-the-badge&logo=intellij-idea&logoColor=white)',
        'pycharm': '![PyCharm](https://img.shields.io/badge/PyCharm-000000?style=for-the-badge&logo=pycharm&logoColor=white)',
        'vim': '![Vim](https://img.shields.io/badge/Vim-019733?style=for-the-badge&logo=vim&logoColor=white)',
        'neovim': '![Neovim](https://img.shields.io/badge/Neovim-57A143?style=for-the-badge&logo=neovim&logoColor=white)',
        'figma': '![Figma](https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white)',
        'postman': '![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)',
        'swagger': '![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)',
        'notion': '![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white)',
        'confluence': '![Confluence](https://img.shields.io/badge/Confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white)',
        'jira': '![Jira](https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white)',
    }
    
    # 社交链接模板
    SOCIAL_TEMPLATES = {
        'github': '[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)]({url})',
        'twitter': '[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)]({url})',
        'linkedin': '[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)]({url})',
        'email': '[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:{url})',
        'blog': '[![Blog](https://img.shields.io/badge/Blog-FF5722?style=for-the-badge&logo=blogger&logoColor=white)]({url})',
        'youtube': '[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)]({url})',
    }
    
    # 默认服务 URL (使用稳定的镜像)
    DEFAULT_STATS_URL = "https://github-readme-stats-git-masterrstaa-rickstaa.vercel.app"
    DEFAULT_STREAK_URL = "https://github-readme-streak-stats-ochre.vercel.app"  # 可用的公共镜像
    DEFAULT_TROPHIES_URL = "https://github-trophy.vercel.app"  # 可用的公共镜像

    # 备用服务列表
    BACKUP_STATS_URLS = [
        "https://github-readme-stats-git-masterrstaa-rickstaa.vercel.app",
        "https://github-readme-stats.zohan.tech",
        "https://github-readme-stats-sigma-five.vercel.app",
    ]
    
    def __init__(self, stats_url: str = "", streak_url: str = "", trophies_url: str = ""):
        self.templates_dir = Path(__file__).parent.parent / 'templates' / 'profile'
        
        # 处理 Stats URL
        if stats_url:
            stats_url = stats_url.rstrip('/')
            if not stats_url.startswith(('http://', 'https://')):
                stats_url = f'https://{stats_url}'
        self.stats_url = stats_url if stats_url else self.DEFAULT_STATS_URL
        
        # 处理 Streak URL
        if streak_url:
            streak_url = streak_url.rstrip('/')
            if not streak_url.startswith(('http://', 'https://')):
                streak_url = f'https://{streak_url}'
        self.streak_url = streak_url if streak_url else self.DEFAULT_STREAK_URL
        
        # 处理 Trophies URL
        if trophies_url:
            trophies_url = trophies_url.rstrip('/')
            if not trophies_url.startswith(('http://', 'https://')):
                trophies_url = f'https://{trophies_url}'
        self.trophies_url = trophies_url if trophies_url else self.DEFAULT_TROPHIES_URL
    
    def generate_stats_card(self, username: str, theme: str = 'tokyonight') -> str:
        """生成 GitHub 统计卡片"""
        return f'''
<p align="center">
  <a href="https://github.com/{username}">
    <img src="{self.stats_url}/api?username={username}&show_icons=true&theme={theme}&hide_border=true&count_private=true" alt="GitHub Stats" />
  </a>
</p>
'''
    
    def generate_streak_card(self, username: str, theme: str = 'tokyonight',
                              hide_border: bool = True, locale: str = 'en',
                              mode: str = 'daily', date_format: str = '') -> str:
        """生成连续贡献卡片 (使用 streak-stats.demolab.com)

        Args:
            username: GitHub 用户名
            theme: 主题 (dark, radical, tokyonight 等)
            hide_border: 是否隐藏边框
            locale: 语言 (en, zh_Hans, ja 等)
            mode: 统计模式 (daily, weekly)
            date_format: 日期格式 (如 M j[, Y], j M[ Y] 等)
        """
        params = [
            f"user={username}",
            f"theme={theme}",
            f"hide_border={'true' if hide_border else 'false'}",
        ]

        if locale and locale != 'en':
            params.append(f"locale={locale}")
        if mode and mode != 'daily':
            params.append(f"mode={mode}")
        if date_format:
            params.append(f"date_format={date_format}")

        query_string = "&".join(params)

        return f'''
<p align="center">
  <a href="https://git.io/streak-stats">
    <img src="{self.streak_url}?{query_string}" alt="GitHub Streak" />
  </a>
</p>
'''
    
    def generate_languages_card(self, username: str, theme: str = 'tokyonight') -> str:
        """生成语言统计卡片"""
        return f'''
<p align="center">
  <img src="{self.stats_url}/api/top-langs/?username={username}&layout=compact&theme={theme}&hide_border=true" alt="Top Languages" />
</p>
'''
    
    def generate_trophy_card(self, username: str, theme: str = 'tokyonight') -> str:
        """生成奖杯卡片"""
        return f'''
<p align="center">
  <img src="{self.trophies_url}/?username={username}&theme={theme}&no-frame=true&row=1&column=7" alt="Trophies" />
</p>
'''
    
    def generate_activity_graph(self, username: str, theme: str = 'radical') -> str:
        """生成活动图 (Contribution Graph)"""
        # 使用 ashutosh00710/github-readme-activity-graph
        return f'''
<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username={username}&theme={theme}&hide_border=true&area=true" alt="Activity Graph" />
</p>
'''

    def generate_intro_items(self, items: List[Dict]) -> str:
        """生成 emoji 列表式介绍
        items: [{'emoji': '👋', 'text': 'Hello...'}, ...]
        """
        if not items:
            return ''

        lines = []
        for item in items:
            emoji = item.get('emoji', '👋')
            text = item.get('text', '')
            if text:
                lines.append(f'- {emoji} {text}')

        if lines:
            return '\n'.join(lines) + '\n'
        return ''

    def generate_stats_side_by_side(self, username: str, theme: str = 'tokyonight') -> str:
        """生成并排的 Stats + Languages 卡片"""
        return f'''
<p align="center">
  <img src="{self.stats_url}/api?username={username}&show_icons=true&theme={theme}&hide_border=true&count_private=true" height="180" alt="GitHub Stats" />
  <img src="{self.stats_url}/api/top-langs/?username={username}&layout=compact&theme={theme}&hide_border=true" height="180" alt="Top Languages" />
</p>
'''
    
    def generate_contribution_calendar(self, username: str, theme: str = 'radical') -> str:
        """生成贡献日历 (Contribution Calendar)"""
        # 使用 ghchart 生成贡献日历图片
        # 颜色适配：根据主题调整（这里简单使用默认或特定颜色）
        color = "409ba5" # 默认青色
        if theme in ['radical', 'tokyonight']:
            color = "ff0055"
            
        return f'''
<p align="center">
  <img src="https://ghchart.rshah.org/{color}/{username}" alt="Contribution Calendar" />
</p>
'''

    def generate_snake_animation(self, username: str) -> str:
        """生成贪吃蛇动画"""
        # 注意：这需要 GitHub Actions 设置
        return f'''
<p align="center">
  <img src="https://github.com/{username}/{username}/blob/output/github-contribution-grid-snake.svg" alt="Snake Animation" />
</p>
'''
    
    def generate_random_quote(self) -> str:
        """生成随机名言"""
        return '''
<p align="center">
  <img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=radical&border=true" alt="Random Dev Quote" />
</p>
'''

    def generate_joke(self) -> str:
        """生成随机程序员笑话"""
        return '''
<p align="center">
  <img src="https://readme-jokes.vercel.app/api?theme=radical&hideBorder=false&bgColor=transparent" alt="Jokes Card" />
</p>
'''
    
    def generate_spotify(self, spotify_id: str) -> str:
        """生成 Spotify 正在播放"""
        return f'''
<p align="center">
  <a href="https://open.spotify.com/user/{spotify_id}">
    <img src="https://novatorem.vercel.app/api/spotify" alt="Spotify" width="400" />
  </a>
</p>
'''
    
    def generate_contribution_snake_setup(self, username: str) -> str:
        """生成设置贪吃蛇动画的说明"""
        return f'''
<details>
<summary>🐍 如何设置贪吃蛇动画</summary>

在你的 `{username}/{username}` 仓库中创建 `.github/workflows/snake.yml`:

```yaml
name: Generate Snake

on:
  schedule:
    - cron: "0 */12 * * *"
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: Platane/snk@v3
        with:
          github_user_name: {username}
          outputs: |
            dist/snake.svg
            dist/snake-dark.svg?palette=github-dark
      - uses: crazy-max/ghaction-github-pages@v2
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
```

</details>
'''
    
    def generate_skill_badges(self, skills: List[str], layout: str = 'inline', custom_skills: List[Dict] = None) -> str:
        """生成技能徽章

        Args:
            skills: 技能列表 (预设技能)
            layout: 布局方式
                - 'inline': 一行显示，自动换行
                - 'per-line': 每个徽章单独一行
                - 'table': 表格布局 (4列)
            custom_skills: 自定义技能列表 [{'name': 'xxx', 'color': 'xxx', 'logo': 'xxx'}, ...]
        """
        badges = []
        # 处理预设技能
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in self.SKILL_ICONS:
                md_badge = self.SKILL_ICONS[skill_lower]
                match = re.match(r'!\[(.*?)\]\((.*?)\)', md_badge)
                if match:
                    alt, url = match.groups()
                    badges.append(f'<img src="{url}" alt="{alt}" />')

        # 处理自定义技能
        if custom_skills:
            for item in custom_skills:
                name = item.get('name', '')
                color = item.get('color', '333333').lstrip('#')
                logo = item.get('logo', '')
                if name:
                    # 构建 shields.io URL
                    badge_url = f"https://img.shields.io/badge/{name}-{color}?style=for-the-badge"
                    if logo:
                        badge_url += f"&logo={logo}&logoColor=white"
                    badges.append(f'<img src="{badge_url}" alt="{name}" />')

        if not badges:
            return ''

        if layout == 'per-line':
            # 每行一个
            return '<br>\n'.join(badges)
        elif layout == 'table':
            # 表格布局 (4列)
            rows = []
            for i in range(0, len(badges), 4):
                row_badges = badges[i:i+4]
                # 补齐到4列
                while len(row_badges) < 4:
                    row_badges.append('')
                rows.append('| ' + ' | '.join(row_badges) + ' |')

            header = '| | | | |'
            separator = '|:---:|:---:|:---:|:---:|'
            return f'{header}\n{separator}\n' + '\n'.join(rows)
        else:
            # inline: 一行显示
            return ' '.join(badges)

    def generate_social_links(self, socials: Dict[str, str], custom_socials: List[Dict] = None) -> str:
        """生成社交链接 (使用 HTML 确保正确渲染)

        Args:
            socials: 预设社交链接 {'github': 'url', ...}
            custom_socials: 自定义社交链接 [{'label': 'xxx', 'url': 'xxx'}, ...]
        """
        from urllib.parse import quote

        links = []

        # 处理预设社交链接
        for platform, url in socials.items():
            platform_lower = platform.lower()
            if platform_lower in self.SOCIAL_TEMPLATES and url:
                template = self.SOCIAL_TEMPLATES[platform_lower]
                md_link = template.format(url=url)
                # 格式: [![Alt](img_url)](link_url)
                match = re.match(r'\[!\[(.*?)\]\((.*?)\)\]\((.*?)\)', md_link)
                if match:
                    alt, img_url, link_url = match.groups()
                    links.append(f'<a href="{link_url}"><img src="{img_url}" alt="{alt}" /></a>')

        # 处理自定义社交链接
        if custom_socials:
            # 预定义一些常见平台的品牌颜色
            brand_colors = {
                'discord': '5865F2',
                'telegram': '26A5E4',
                '微信': '07C160',
                '微信公众号': '07C160',
                'wechat': '07C160',
                '知乎': '0084FF',
                'zhihu': '0084FF',
                '掘金': '1E80FF',
                'juejin': '1E80FF',
                'bilibili': 'FB7299',
                'b站': 'FB7299',
                'website': '8B5CF6',
                '个人网站': '8B5CF6',
                'portfolio': 'F59E0B',
                '作品集': 'F59E0B',
                'instagram': 'E4405F',
                'tiktok': '000000',
                '抖音': '000000',
                'reddit': 'FF4500',
                'slack': '4A154B',
                'twitch': '9146FF',
                'medium': '000000',
                'dev.to': '0A0A0A',
                'stackoverflow': 'F58025',
                'codepen': '000000',
                'dribbble': 'EA4C89',
                'behance': '1769FF',
                'figma': 'F24E1E',
            }

            for item in custom_socials:
                label = item.get('label', '')
                url = item.get('url', '')
                if label and url:
                    # 使用 shields.io 的静态 API 格式，对中文字符更可靠
                    encoded_label = quote(label, safe='')
                    # 检查是否有预定义的品牌颜色
                    label_lower = label.lower()
                    if label_lower in brand_colors:
                        color = brand_colors[label_lower]
                    else:
                        # 使用随机颜色 (紫色系列，与主题协调)
                        colors = ['8B5CF6', '7C3AED', '6366F1', '4F46E5', 'A855F7']
                        color = colors[len(label) % len(colors)]
                    # 使用 query string 格式，对特殊字符更可靠
                    badge_url = f"https://img.shields.io/static/v1?label=&message={encoded_label}&color={color}&style=for-the-badge"
                    links.append(f'<a href="{url}"><img src="{badge_url}" alt="{label}" /></a>')

        if links:
            return ' '.join(links)
        return ''
    
    def generate_capsule_render(self, text: str, theme: str = 'tokyonight', desc: str = '') -> str:
        """生成 Capsule Render 动态波浪头图"""
        # 颜色映射
        color = "0d1117" # 默认深色背景
        if theme == 'radical':
            color = "141321"
        elif theme == 'tokyonight':
            color = "1a1b27"

        # 文本处理
        text = text.replace(" ", "%20")
        desc = desc.replace(" ", "%20") if desc else "Open%20Source%20Enthusiast"

        return f'''
<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=280&section=header&text={text}&fontSize=80&animation=fadeIn&fontAlignY=35&desc={desc}&descAlignY=55&descAlign=50" alt="Capsule Render" />
</div>
'''

    def generate_wave_header(self, text: str, theme: str = 'tokyonight') -> str:
        """生成打字机效果 (Typing SVG)

        支持多行文本，用 ; 分割。例如: "Hi there!;I'm a Developer;Open Source Lover"
        """
        # 用分号分割多行
        lines_list = [line.strip() for line in text.split(";") if line.strip()]
        if not lines_list:
            lines_list = [text]

        lines_param = "&lines=".join([line.replace(" ", "+") for line in lines_list])
        
        # 颜色适配
        color = "6366F1" # Indio
        if theme == 'radical':
            color = "fe428e"
        elif theme == 'tokyonight':
            color = "7aa2f7" # GitHub Blue
            
        return f'''
<h1 align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=1000&color={color}&center=true&vCenter=true&random=false&width=600&lines={lines_param}" alt="Typing SVG" />
</h1>
'''

    def generate_components_table(self, components: List[Dict]) -> str:
        """生成项目组件表格

        Args:
            components: [
                {
                    'name': '项目名',
                    'url': '项目链接',
                    'status': 'release' | 'private' | 'beta' | 'alpha' | 'dev',
                    'version': 'v1.0.0',  # 可选，仅 release 状态显示
                    'description': '项目描述'
                },
                ...
            ]
        """
        if not components:
            return ''

        # 状态徽章颜色映射
        status_colors = {
            'release': '67C23A',    # 绿色 - 正式发布
            'private': 'E6A23C',    # 橙色 - 私有
            'beta': '409EFF',       # 蓝色 - 测试版
            'alpha': '909399',      # 灰色 - 早期版本
            'dev': 'F56C6C',        # 红色 - 开发中
        }

        lines = []
        lines.append('| Project | Status | Description |')
        lines.append('|:--------|:-------|:------------|')

        for comp in components:
            name = comp.get('name', '')
            url = comp.get('url', '')
            status = comp.get('status', 'release').lower()
            version = comp.get('version', '')
            desc = comp.get('description', '')

            if not name:
                continue

            # 项目名链接
            if url:
                project_cell = f'[{name}]({url})'
            else:
                project_cell = name

            # 状态徽章
            color = status_colors.get(status, '67C23A')
            if status == 'release' and version:
                # 显示版本号
                badge_url = f'https://img.shields.io/badge/release-{version}-{color}'
            elif status == 'private':
                badge_url = f'https://img.shields.io/badge/release-private-{color}'
            else:
                badge_url = f'https://img.shields.io/badge/{status}-{color}'

            status_cell = f'![{status}]({badge_url})'

            lines.append(f'| {project_cell} | {status_cell} | {desc} |')

        return '\n'.join(lines) + '\n'

    def generate_profile(self, config: Dict[str, Any]) -> str:
        """根据配置生成完整的 Profile README"""
        username = config.get('username', 'username')
        name = config.get('name', username)
        bio = config.get('bio', '')
        greeting = config.get('greeting', "Hi there! 👋")
        skills = config.get('skills', [])
        socials = config.get('socials', {})
        custom_socials = config.get('custom_socials', [])
        theme = config.get('theme', 'radical')
        intro_items = config.get('intro_items', [])
        layout = config.get('layout', 'single')  # 'single' or 'side-by-side'
        streak_locale = config.get('streak_locale', 'en')  # Streak 卡片语言

        sections = []

        # 1. 顶部 Header
        header_style = config.get('header_style', 'typing')
        if header_style == 'capsule':
            sections.append(self.generate_capsule_render(greeting, theme))
        else:
            sections.append(self.generate_wave_header(greeting, theme))

        # 2. 个人简介 & 社交链接 (居中)
        intro_section = []
        if bio:
            intro_section.append(f'<em>{bio}</em>')

        if socials or custom_socials:
            intro_section.append(self.generate_social_links(socials, custom_socials))

        if intro_section:
            sections.append(f'''
<p align="center">
  {'<br>'.join(intro_section)}
</p>
''')

        # 2.5 Emoji 列表式介绍项
        if intro_items:
            intro_items_md = self.generate_intro_items(intro_items)
            if intro_items_md:
                sections.append('\n### 👋 About Me\n')
                sections.append(intro_items_md)

        sections.append('\n---\n')

        # 3. 核心数据区域
        show_stats = config.get('show_stats', True)
        show_languages = config.get('show_languages', True)
        show_streak = config.get('show_streak', True)

        # 根据布局生成统计卡片
        if layout == 'side-by-side' and show_stats and show_languages:
            # 并排布局: Stats + Languages 并排
            sections.append('### 📊 GitHub Stats\n')
            sections.append(self.generate_stats_side_by_side(username, theme))

            # Streak 单独一行
            if show_streak:
                sections.append(self.generate_streak_card(username, theme, locale=streak_locale))
        else:
            # 单列布局: 原有逻辑
            stats_cards = []
            if show_stats:
                stats_cards.append(self.generate_stats_card(username, theme).strip())
            if show_streak:
                stats_cards.append(self.generate_streak_card(username, theme, locale=streak_locale).strip())
            if show_languages:
                stats_cards.append(self.generate_languages_card(username, theme).strip())

            if stats_cards:
                sections.append('### 📊 GitHub Stats\n')
                # 使用居中的 flex 布局容器，比 table 更现代且在 GitHub 渲染良好
                sections.append('<div align="center">')
                for card in stats_cards:
                    # 提取 img标签
                    sections.append(card.replace('<p align="center">', '').replace('</p>', '').strip())
                    sections.append('<br>')
                sections.append('</div>\n')

        # 4. 技术栈 (技能徽章)
        badge_layout = config.get('badge_layout', 'inline')
        custom_skills = config.get('custom_skills', [])
        if skills or custom_skills:
            sections.append('\n### 🛠️ Tech Stack\n')
            badge_content = self.generate_skill_badges(skills, badge_layout, custom_skills)
            if badge_layout == 'table':
                # 表格不需要 div 包裹
                sections.append(f'\n{badge_content}\n')
            else:
                sections.append(f'<div align="center">\n{badge_content}\n</div>\n')

        # 5. 项目组件表格
        components = config.get('components', [])
        components_title = config.get('components_title', 'Components')
        if components:
            sections.append(f'\n### 📦 {components_title}\n')
            sections.append(self.generate_components_table(components))

        # 6. 更多展示 (奖杯、活动图)
        if config.get('show_trophy', False):
            sections.append('\n### 🏆 Trophies\n')
            sections.append(self.generate_trophy_card(username, theme))
            
        if config.get('show_activity', False):
            sections.append('\n### 📈 Activity\n')
            sections.append(self.generate_activity_graph(username, theme))
            
        # 6. 有趣的内容 (名言、笑话)
        show_quote = config.get('show_quote', False)
        show_joke = config.get('show_joke', False)

        if show_quote or show_joke:
            sections.append('\n### 🧩 Fun Zone\n')
            if show_quote:
                sections.append(self.generate_random_quote())
            if show_joke:
                sections.append(self.generate_joke())

        # 7. 贪吃蛇动画 (通常放在底部)
        if config.get('show_snake', False):
            sections.append('\n### 🐍 Contribution Snake\n')
            sections.append(self.generate_snake_animation(username))
            sections.append(self.generate_contribution_snake_setup(username))

        # 8. 页脚
        sections.append(f'''
---
<p align="center">
  <img src="https://komarev.com/ghpvc/?username={username}&color=blueviolet&style=flat-square&label=Profile+Views" alt="Profile Views" />
  <br>
  <br>
  ⭐️ From <a href="https://github.com/{username}">{name}</a>
</p>
''')
        
        return '\n'.join(sections)
    
    def get_available_themes(self) -> List[str]:
        """获取可用的主题列表"""
        return [
            'radical', 'merko', 'gruvbox', 'tokyonight', 'onedark',
            'cobalt', 'synthwave', 'highcontrast', 'dracula', 'prussian',
            'monokai', 'vue', 'vue-dark', 'shades-of-purple', 'nightowl',
            'buefy', 'blue-green', 'algolia', 'great-gatsby', 'darcula',
            'bear', 'solarized-dark', 'solarized-light', 'chartreuse-dark',
            'nord', 'gotham', 'material-palenight', 'graywhite', 'vision-friendly-dark',
            'ayu-mirage', 'midnight-purple', 'calm', 'flag-india', 'omni',
            'react', 'jolly', 'maroongold', 'yeblu', 'blueberry',
        ]
    
    def get_available_skills(self) -> List[str]:
        """获取可用的技能列表"""
        return list(self.SKILL_ICONS.keys())
