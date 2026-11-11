"""GitHub API 封装"""
from typing import Optional, List, Dict, Any
from github import Auth, Github, GithubException
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser


class GitHubAPI:
    """GitHub API 操作封装"""
    
    def __init__(self, token: str):
        """初始化 GitHub API 客户端
        
        Args:
            token: GitHub Personal Access Token
        """
        self.token = token
        self.client = Github(auth=Auth.Token(token), per_page=100, timeout=15, retry=2)
        self._user: Optional[AuthenticatedUser] = None
    
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.client.close()

    def _owned_repo(self, repo_name: str) -> Repository:
        """Resolve both name and owner/name, keeping management on this account."""
        username = self.user.login
        full_name = repo_name if '/' in repo_name else f"{username}/{repo_name}"
        if full_name.split('/', 1)[0].lower() != username.lower():
            raise ValueError("只能管理当前账户拥有的仓库")
        repo = self.client.get_repo(full_name)
        # GitHub can redirect an old repository URL after a transfer.
        if repo.owner.login.lower() != username.lower():
            raise ValueError("仓库已转移，不能管理其他账户拥有的仓库")
        return repo

    @property
    def user(self) -> AuthenticatedUser:
        """获取当前认证用户"""
        if self._user is None:
            self._user = self.client.get_user()
        return self._user
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        user = self.user
        return {
            'login': user.login,
            'name': user.name or user.login,
            'avatar_url': user.avatar_url,
            'bio': user.bio or '',
            'public_repos': user.public_repos,
            'private_repos': user.owned_private_repos or 0,
            'followers': user.followers,
            'following': user.following,
            'html_url': user.html_url,
            'created_at': user.created_at,
        }
    
    def list_repos(self, 
                   visibility: str = 'all',
                   sort: str = 'updated',
                   include_forks: bool = True) -> List[Dict[str, Any]]:
        """列出用户的所有仓库
        
        Args:
            visibility: 可见性过滤 ('all', 'public', 'private')
            sort: 排序方式 ('updated', 'created', 'pushed', 'full_name')
            include_forks: 是否包含 Fork 的仓库
            
        Returns:
            仓库信息列表
        """
        repos = []
        
        for repo in self.user.get_repos(affiliation='owner', visibility=visibility, sort=sort):
            # 只显示用户自己拥有的仓库，排除作为协作者的仓库
            if repo.owner.login != self.user.login:
                continue
            
            # 过滤可见性
            if visibility == 'public' and repo.private:
                continue
            if visibility == 'private' and not repo.private:
                continue
            
            # 过滤 Fork
            if not include_forks and repo.fork:
                continue
            
            repos.append({
                'id': repo.id,
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description or '',
                'html_url': repo.html_url,
                'clone_url': repo.clone_url,
                'ssh_url': repo.ssh_url,
                'private': repo.private,
                'fork': repo.fork,
                'archived': repo.archived,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'watchers': repo.watchers_count,
                'language': repo.language or 'Unknown',
                'size': repo.size,
                'default_branch': repo.default_branch,
                'created_at': repo.created_at,
                'updated_at': repo.updated_at,
                'pushed_at': repo.pushed_at,
            })
        
        return repos
    
    def list_collaborator_repos(self) -> List[Dict[str, Any]]:
        """列出用户作为协作者参与的仓库（不是所有者）"""
        repos = []
        
        for repo in self.user.get_repos(affiliation='collaborator', sort='updated'):
            # 只显示作为协作者的仓库
            if repo.owner.login == self.user.login:
                continue
            
            repos.append({
                'id': repo.id,
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description or '',
                'html_url': repo.html_url,
                'private': repo.private,
                'owner': repo.owner.login,
                'owner_avatar': repo.owner.avatar_url,
            })
        
        return repos
    
    def leave_repo(self, full_name: str) -> tuple[bool, str]:
        """退出协作仓库（移除自己的协作者权限）
        
        Args:
            full_name: 仓库完整名称 (owner/repo)
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            repo = self.client.get_repo(full_name)
            # 使用 remove_from_collaborators 移除自己
            repo.remove_from_collaborators(self.user.login)
            return True, ""
        except GithubException as e:
            error_msg = str(e)
            if e.status == 403:
                error_msg = "没有权限退出此仓库"
            elif e.status == 404:
                error_msg = "仓库不存在或你不是协作者"
            print(f"退出仓库失败 [{full_name}]: {error_msg}")
            return False, error_msg
    
    def delete_repo(self, repo_name: str) -> tuple[bool, str]:
        """删除仓库
        
        Args:
            repo_name: 仓库名称（可以是 name 或 full_name）
            
        Returns:
            (是否删除成功, 错误消息)
        """
        try:
            repo = self._owned_repo(repo_name)
            repo.delete()
            return True, ""
        except GithubException as e:
            error_msg = str(e)
            if e.status == 403:
                error_msg = "权限不足，请确保 Token 有 delete_repo 权限"
            elif e.status == 404:
                error_msg = f"仓库不存在: {repo_name}"
            print(f"删除仓库失败 [{repo_name}]: {error_msg}")
            return False, error_msg
    
    def batch_delete_repos(self, repo_names: List[str]) -> Dict[str, dict]:
        """批量删除仓库
        
        Args:
            repo_names: 仓库名称列表
            
        Returns:
            每个仓库的删除结果 {name: {success: bool, error: str}}
        """
        results = {}
        for name in repo_names:
            success, error = self.delete_repo(name)
            results[name] = {"success": success, "error": error}
        return results

    
    def archive_repo(self, repo_name: str) -> bool:
        """归档仓库
        
        Args:
            repo_name: 仓库名称
            
        Returns:
            是否归档成功
        """
        try:
            repo = self._owned_repo(repo_name)
            repo.edit(archived=True)
            return True
        except GithubException as e:
            print(f"归档仓库失败: {e}")
            return False
    
    def unarchive_repo(self, repo_name: str) -> bool:
        """取消归档仓库"""
        try:
            repo = self._owned_repo(repo_name)
            repo.edit(archived=False)
            return True
        except GithubException as e:
            print(f"取消归档失败: {e}")
            return False
    
    def update_repo_visibility(self, repo_name: str, private: bool) -> bool:
        """更新仓库可见性"""
        try:
            repo = self._owned_repo(repo_name)
            repo.edit(private=private)
            return True
        except GithubException as e:
            print(f"更新可见性失败: {e}")
            return False
    
    def get_profile_readme(self) -> Optional[str]:
        """获取用户的 Profile README 内容"""
        try:
            username = self.user.login
            repo = self.client.get_repo(f"{username}/{username}")
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')
        except GithubException:
            return None
    
    def update_profile_readme(self, content: str) -> bool:
        """更新 Profile README
        
        如果 profile 仓库不存在，会自动创建
        """
        try:
            username = self.user.login
            
            # 尝试获取或创建 profile 仓库
            try:
                repo = self.client.get_repo(f"{username}/{username}")
            except GithubException as exc:
                if exc.status != 404:
                    raise
                # 创建 profile 仓库
                repo = self.user.create_repo(
                    name=username,
                    description="My GitHub Profile",
                    private=False,
                    auto_init=True
                )
            
            # Only a missing README lookup should trigger file creation.
            try:
                readme = repo.get_readme()
            except GithubException as exc:
                if exc.status != 404:
                    raise
                repo.create_file(
                    path="README.md",
                    message="Create profile README",
                    content=content
                )
            else:
                repo.update_file(
                    path=readme.path,
                    message="Update profile README",
                    content=content,
                    sha=readme.sha
                )

            return True
        except GithubException as e:
            print(f"更新 Profile README 失败: {e}")
            return False
    
    def delete_profile_readme(self) -> bool:
        """删除 Profile README，恢复默认状态

        Returns:
            是否删除成功
        """
        try:
            username = self.user.login
            repo = self.client.get_repo(f"{username}/{username}")

            # 获取 README 文件
            try:
                readme = repo.get_readme()
                # 删除 README.md 文件
                repo.delete_file(
                    path=readme.path,
                    message="Restore default profile",
                    sha=readme.sha
                )
                return True
            except GithubException as e:
                if e.status == 404:
                    # README 不存在，认为已经是默认状态
                    return True
                raise e

        except GithubException as e:
            if e.status == 404:
                # Profile 仓库不存在，认为已经是默认状态
                return True
            print(f"删除 Profile README 失败: {e}")
            return False

    def get_contribution_stats(self) -> Dict[str, int]:
        """获取贡献统计（简化版）"""
        user = self.user
        return {
            'public_repos': user.public_repos,
            'public_gists': user.public_gists,
            'followers': user.followers,
            'following': user.following,
        }
