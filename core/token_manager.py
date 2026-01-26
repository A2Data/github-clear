"""Token 管理模块 - 统一管理所有页面的 Token 存取（无 Streamlit 依赖）"""
from pathlib import Path
import os


class TokenManager:
    """Token 管理器 - 使用文件存储"""
    
    _instance = None
    _env_path = Path(__file__).parent.parent / '.env'
    _cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_tokens()
        return cls._instance
    
    def _load_tokens(self):
        """从 .env 文件加载 tokens"""
        self._cache = {'github': '', 'gitee': ''}
        
        if self._env_path.exists():
            with open(self._env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('GITHUB_TOKEN='):
                        self._cache['github'] = line.split('=', 1)[1]
                    elif line.startswith('GITEE_TOKEN='):
                        self._cache['gitee'] = line.split('=', 1)[1]
    
    def get_github_token(self) -> str:
        """获取 GitHub Token"""
        return self._cache.get('github', '')
    
    def get_gitee_token(self) -> str:
        """获取 Gitee Token"""
        return self._cache.get('gitee', '')
    
    def set_github_token(self, token: str):
        """设置 GitHub Token"""
        self._cache['github'] = token
        self._save_to_env('GITHUB_TOKEN', token)
    
    def set_gitee_token(self, token: str):
        """设置 Gitee Token"""
        self._cache['gitee'] = token
        self._save_to_env('GITEE_TOKEN', token)
    
    def _save_to_env(self, key: str, value: str):
        """保存 token 到 .env 文件"""
        env_content = ""
        if self._env_path.exists():
            with open(self._env_path, 'r') as f:
                env_content = f.read()
        
        lines = env_content.split('\n')
        new_lines = []
        found = False
        for line in lines:
            if line.startswith(f'{key}='):
                new_lines.append(f'{key}={value}')
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f'{key}={value}')
        
        with open(self._env_path, 'w') as f:
            f.write('\n'.join(new_lines))
    
    def is_github_configured(self) -> bool:
        """检查 GitHub 是否已配置"""
        token = self.get_github_token()
        return bool(token and token != 'your_github_token_here' and len(token) > 10)
    
    def is_gitee_configured(self) -> bool:
        """检查 Gitee 是否已配置"""
        token = self.get_gitee_token()
        return bool(token and token != 'your_gitee_token_here' and len(token) > 10)


# 便捷函数（使用单例）
_manager = None

def _get_manager() -> TokenManager:
    global _manager
    if _manager is None:
        _manager = TokenManager()
    return _manager

def get_github_token() -> str:
    return _get_manager().get_github_token()

def get_gitee_token() -> str:
    return _get_manager().get_gitee_token()

def set_github_token(token: str):
    _get_manager().set_github_token(token)

def set_gitee_token(token: str):
    _get_manager().set_gitee_token(token)

def is_github_configured() -> bool:
    return _get_manager().is_github_configured()

def is_gitee_configured() -> bool:
    return _get_manager().is_gitee_configured()

def get_stats_url() -> str:
    """获取自定义 Stats URL"""
    return os.getenv('STATS_URL', '')

def get_streak_url() -> str:
    """获取自定义 Streak Stats URL"""
    return os.getenv('STREAK_URL', '')

def get_trophies_url() -> str:
    """获取自定义 Trophies URL"""
    return os.getenv('TROPHIES_URL', '')

def set_stats_url(stats_url: str, streak_url: str, trophies_url: str = ""):
    """保存自定义 Stats URLs"""
    # 自动补充 https:// 协议头
    if stats_url and not stats_url.startswith(('http://', 'https://')):
        stats_url = f'https://{stats_url}'
    if streak_url and not streak_url.startswith(('http://', 'https://')):
        streak_url = f'https://{streak_url}'
    if trophies_url and not trophies_url.startswith(('http://', 'https://')):
        trophies_url = f'https://{trophies_url}'

    env_path = Path(__file__).parent.parent / '.env'
    
    # 读取现有内容
    content = ""
    if env_path.exists():
        content = env_path.read_text()
    
    # 更新或添加 URL
    lines = content.split('\n')
    new_lines = []
    stats_found = False
    streak_found = False
    trophies_found = False
    
    for line in lines:
        if line.startswith('STATS_URL='):
            new_lines.append(f'STATS_URL={stats_url}')
            stats_found = True
        elif line.startswith('STREAK_URL='):
            new_lines.append(f'STREAK_URL={streak_url}')
            streak_found = True
        elif line.startswith('TROPHIES_URL='):
            new_lines.append(f'TROPHIES_URL={trophies_url}')
            trophies_found = True
        else:
            new_lines.append(line)
    
    if not stats_found:
        new_lines.append(f'STATS_URL={stats_url}')
    if not streak_found:
        new_lines.append(f'STREAK_URL={streak_url}')
    if not trophies_found:
        new_lines.append(f'TROPHIES_URL={trophies_url}')
    
    env_path.write_text('\n'.join(new_lines))
    
    # 更新环境变量
    os.environ['STATS_URL'] = stats_url
    os.environ['STREAK_URL'] = streak_url
    os.environ['TROPHIES_URL'] = trophies_url
