"""配置管理模块"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Settings:
    """应用配置"""
    
    # GitHub 配置
    GITHUB_TOKEN: str = os.getenv('GITHUB_TOKEN', '')
    GITHUB_API_BASE: str = 'https://api.github.com'
    
    # Gitee 配置
    GITEE_TOKEN: str = os.getenv('GITEE_TOKEN', '')
    GITEE_API_BASE: str = 'https://gitee.com/api/v5'
    
    # 应用配置
    APP_TITLE: str = '🚀 GitHub/Gitee 仓库管理器'
    PAGE_ICON: str = '🚀'
    
    @classmethod
    def is_github_configured(cls) -> bool:
        """检查 GitHub 是否已配置"""
        return bool(cls.GITHUB_TOKEN and cls.GITHUB_TOKEN != 'your_github_token_here')
    
    @classmethod
    def is_gitee_configured(cls) -> bool:
        """检查 Gitee 是否已配置"""
        return bool(cls.GITEE_TOKEN and cls.GITEE_TOKEN != 'your_gitee_token_here')

settings = Settings()
