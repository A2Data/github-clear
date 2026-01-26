"""Gitee API 封装"""
from typing import Optional, List, Dict, Any
import requests


class GiteeAPI:
    """Gitee API 操作封装"""
    
    def __init__(self, token: str):
        """初始化 Gitee API 客户端
        
        Args:
            token: Gitee Personal Access Token
        """
        self.token = token
        self.base_url = 'https://gitee.com/api/v5'
        self._user_info: Optional[Dict] = None
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """发送 API 请求"""
        url = f"{self.base_url}{endpoint}"
        params = kwargs.get('params', {})
        params['access_token'] = self.token
        kwargs['params'] = params
        
        response = requests.request(method, url, **kwargs)
        return response
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        if self._user_info:
            return self._user_info
        
        response = self._request('GET', '/user')
        if response.status_code == 200:
            data = response.json()
            self._user_info = {
                'login': data.get('login', ''),
                'name': data.get('name', data.get('login', '')),
                'avatar_url': data.get('avatar_url', ''),
                'bio': data.get('bio', ''),
                'public_repos': data.get('public_repos', 0),
                'private_repos': data.get('private_repos', 0),
                'followers': data.get('followers', 0),
                'following': data.get('following', 0),
                'html_url': data.get('html_url', ''),
                'created_at': data.get('created_at', ''),
            }
            return self._user_info
        return {}
    
    def list_repos(self,
                   visibility: str = 'all',
                   sort: str = 'updated',
                   include_forks: bool = True) -> List[Dict[str, Any]]:
        """列出用户的所有仓库
        
        Args:
            visibility: 可见性过滤 ('all', 'public', 'private')
            sort: 排序方式 ('updated', 'created', 'full_name')
            include_forks: 是否包含 Fork 的仓库
            
        Returns:
            仓库信息列表
        """
        repos = []
        page = 1
        per_page = 100
        
        while True:
            params = {
                'sort': sort,
                'page': page,
                'per_page': per_page,
            }
            
            if visibility != 'all':
                params['visibility'] = visibility
            
            response = self._request('GET', '/user/repos', params=params)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            if not data:
                break
            
            for repo in data:
                # 过滤 Fork
                if not include_forks and repo.get('fork', False):
                    continue
                
                repos.append({
                    'id': repo.get('id'),
                    'name': repo.get('name', ''),
                    'full_name': repo.get('full_name', ''),
                    'description': repo.get('description', '') or '',
                    'html_url': repo.get('html_url', ''),
                    'clone_url': repo.get('clone_url', ''),
                    'ssh_url': repo.get('ssh_url', ''),
                    'private': repo.get('private', False),
                    'fork': repo.get('fork', False),
                    'archived': repo.get('archived', False),
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'watchers': repo.get('watchers_count', 0),
                    'language': repo.get('language') or 'Unknown',
                    'size': repo.get('size', 0),
                    'default_branch': repo.get('default_branch', 'master'),
                    'created_at': repo.get('created_at', ''),
                    'updated_at': repo.get('updated_at', ''),
                    'pushed_at': repo.get('pushed_at', ''),
                })
            
            page += 1
        
        return repos
    
    def delete_repo(self, owner: str, repo_name: str) -> bool:
        """删除仓库
        
        Args:
            owner: 仓库所有者
            repo_name: 仓库名称
            
        Returns:
            是否删除成功
        """
        # Gitee 删除 API 需要在 body 中传递 access_token
        url = f"{self.base_url}/repos/{owner}/{repo_name}"
        data = {'access_token': self.token}
        
        try:
            response = requests.delete(url, data=data)
            print(f"Delete {owner}/{repo_name}: status={response.status_code}")
            # Gitee 返回 204 或 200 都算成功
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Delete error: {e}")
            return False
    
    def batch_delete_repos(self, repo_full_names: List[str]) -> Dict[str, bool]:
        """批量删除仓库
        
        Args:
            repo_full_names: 仓库完整名称列表 (owner/repo)
            
        Returns:
            每个仓库的删除结果
        """
        results = {}
        for full_name in repo_full_names:
            parts = full_name.split('/')
            if len(parts) == 2:
                owner, name = parts
                results[full_name] = self.delete_repo(owner, name)
            else:
                results[full_name] = False
        return results
    
    def change_visibility(self, owner: str, repo_name: str, private: bool) -> bool:
        """更改仓库可见性
        
        Args:
            owner: 仓库所有者
            repo_name: 仓库名称
            private: True 为私有，False 为公开
            
        Returns:
            是否更改成功
        """
        url = f"{self.base_url}/repos/{owner}/{repo_name}"
        data = {
            'access_token': self.token,
            'private': private
        }
        
        try:
            response = requests.patch(url, data=data)
            print(f"Change visibility {owner}/{repo_name} to {'private' if private else 'public'}: status={response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Change visibility error: {e}")
            return False
    
    def update_repo(self, owner: str, repo_name: str, **kwargs) -> bool:
        """更新仓库信息"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}"
        data = {'access_token': self.token}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        response = requests.patch(url, data=data)
        return response.status_code == 200
    
    def get_readme(self, owner: str, repo_name: str) -> Optional[str]:
        """获取仓库 README 内容"""
        response = self._request('GET', f'/repos/{owner}/{repo_name}/readme')
        if response.status_code == 200:
            data = response.json()
            import base64
            content = data.get('content', '')
            if content:
                return base64.b64decode(content).decode('utf-8')
        return None
