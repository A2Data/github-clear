"""
GitHub/Gitee 仓库管理工具 - FastAPI 版本
使用 Jinja2 模板实现现代化 UI
"""
from fastapi import FastAPI, Request, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json

from core import token_manager
from core.github_api import GitHubAPI
from core.gitee_api import GiteeAPI
from core.profile_generator import ProfileGenerator
from config.settings import settings

app = FastAPI(title="GitHub Clear", version="2.0.0")

# 配置静态文件和模板
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# token_manager 模块已在顶部导入，使用其模块级函数


# ================== 页面路由 ==================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    github_configured = token_manager.is_github_configured()
    gitee_configured = token_manager.is_gitee_configured()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "github_configured": github_configured,
        "gitee_configured": gitee_configured,
    })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """仪表板 - 快速渲染，数据异步加载"""
    github_configured = token_manager.is_github_configured()
    gitee_configured = token_manager.is_gitee_configured()

    # 只获取用户基本信息（快速）
    github_user = None
    gitee_user = None

    if github_configured:
        try:
            api = GitHubAPI(token_manager.get_github_token())
            github_user = api.get_user_info()
        except Exception as e:
            print(f"GitHub API error: {e}")

    if gitee_configured:
        try:
            api = GiteeAPI(token_manager.get_gitee_token())
            gitee_user = api.get_user_info()
        except Exception as e:
            print(f"Gitee API error: {e}")

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "github_configured": github_configured,
        "gitee_configured": gitee_configured,
        "github_user": github_user,
        "gitee_user": gitee_user,
    })


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """获取仪表板统计数据（异步加载）"""
    if not token_manager.is_github_configured():
        return {"repos": [], "stats": None}

    try:
        api = GitHubAPI(token_manager.get_github_token())
        all_repos = api.list_repos(sort='updated')
        recent_repos = all_repos[:10]

        # 计算统计
        own_repos = [r for r in all_repos if not r['fork']]
        stats = {
            "public_repos": sum(1 for r in own_repos if not r['private']),
            "private_repos": sum(1 for r in own_repos if r['private']),
            "total_repos": len(own_repos),
            "fork_repos": len(all_repos) - len(own_repos),
        }

        return {"repos": recent_repos, "stats": stats}
    except Exception as e:
        return {"repos": [], "stats": None, "error": str(e)}


@app.get("/repositories", response_class=HTMLResponse)
async def repositories(request: Request):
    """仓库管理"""
    github_configured = token_manager.is_github_configured()
    gitee_configured = token_manager.is_gitee_configured()
    return templates.TemplateResponse("repositories.html", {
        "request": request,
        "github_configured": github_configured,
        "gitee_configured": gitee_configured,
    })


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    """主页美化"""
    github_configured = token_manager.is_github_configured()
    generator = ProfileGenerator()
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "github_configured": github_configured,
        "available_skills": generator.get_available_skills(),
        "available_themes": generator.get_available_themes(),
        "stats_url": token_manager.get_stats_url() or ProfileGenerator.DEFAULT_STATS_URL,
        "streak_url": token_manager.get_streak_url() or ProfileGenerator.DEFAULT_STREAK_URL,
        "trophies_url": token_manager.get_trophies_url() or ProfileGenerator.DEFAULT_TROPHIES_URL,
    })


@app.get("/DOCKER_DEPLOYMENT.md", response_class=FileResponse)
async def docker_deployment_guide():
    """Docker 部署指南"""
    return FileResponse(
        BASE_DIR / "DOCKER_DEPLOYMENT.md",
        media_type="text/markdown",
        filename="DOCKER_DEPLOYMENT.md"
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """设置页面"""
    github_configured = token_manager.is_github_configured()
    gitee_configured = token_manager.is_gitee_configured()
    
    # 获取 SSH Keys
    ssh_keys = []
    ssh_dir = Path.home() / '.ssh'
    if ssh_dir.exists():
        for pub_path in ssh_dir.glob('id_*.pub'):
            try:
                with open(pub_path, 'r') as f:
                    ssh_keys.append({
                        'name': pub_path.name,
                        'content': f.read()
                    })
            except:
                pass
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "github_configured": github_configured,
        "gitee_configured": gitee_configured,
        "ssh_keys": ssh_keys,
        "stats_url": token_manager.get_stats_url(),
        "streak_url": token_manager.get_streak_url(),
    })


# ================== API 路由 ==================

@app.get("/api/repos/github")
async def get_github_repos(
    visibility: str = "all",
    sort: str = "updated",
    include_forks: bool = True
):
    """获取 GitHub 仓库列表"""
    if not token_manager.is_github_configured():
        raise HTTPException(status_code=401, detail="GitHub Token 未配置")
    
    try:
        api = GitHubAPI(token_manager.get_github_token())
        repos = api.list_repos(visibility=visibility, sort=sort, include_forks=include_forks)
        return {"repos": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/repos/github/collaborator")
async def get_github_collaborator_repos():
    """获取用户作为协作者的仓库列表"""
    if not token_manager.is_github_configured():
        raise HTTPException(status_code=401, detail="GitHub Token 未配置")
    
    try:
        api = GitHubAPI(token_manager.get_github_token())
        repos = api.list_collaborator_repos()
        return {"repos": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/repos/github/leave")
async def leave_github_repos(request: Request):
    """退出协作仓库"""
    if not token_manager.is_github_configured():
        raise HTTPException(status_code=401, detail="GitHub Token 未配置")
    
    data = await request.json()
    repo_full_names = data.get("repos", [])
    
    if not repo_full_names:
        raise HTTPException(status_code=400, detail="请选择要退出的仓库")
    
    api = GitHubAPI(token_manager.get_github_token())
    results = {}
    errors = []
    
    for full_name in repo_full_names:
        success, error = api.leave_repo(full_name)
        results[full_name] = success
        if not success:
            errors.append(f"{full_name}: {error}")
    
    success_count = sum(results.values())
    
    response = {
        "success": success_count,
        "total": len(repo_full_names),
        "results": results
    }
    
    if errors:
        response["errors"] = errors
    
    return response


@app.get("/api/repos/gitee")
async def get_gitee_repos(
    visibility: str = "all",
    sort: str = "updated",
    include_forks: bool = True
):
    """获取 Gitee 仓库列表"""
    if not token_manager.is_gitee_configured():
        raise HTTPException(status_code=401, detail="Gitee Token 未配置")
    
    try:
        api = GiteeAPI(token_manager.get_gitee_token())
        repos = api.list_repos(visibility=visibility, sort=sort, include_forks=include_forks)
        return {"repos": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/repos/github/delete")
async def delete_github_repos(request: Request):
    """批量删除 GitHub 仓库"""
    if not token_manager.is_github_configured():
        raise HTTPException(status_code=401, detail="GitHub Token 未配置")
    
    data = await request.json()
    repo_names = data.get("repos", [])
    
    if not repo_names:
        raise HTTPException(status_code=400, detail="请选择要删除的仓库")
    
    api = GitHubAPI(token_manager.get_github_token())
    results = {}
    errors = []
    
    for name in repo_names:
        success, error = api.delete_repo(name)
        results[name] = success
        if not success:
            errors.append(f"{name}: {error}")
    
    success_count = sum(results.values())
    
    response = {
        "success": success_count,
        "total": len(repo_names),
        "results": results
    }
    
    if errors:
        response["errors"] = errors
    
    return response


@app.post("/api/repos/github/archive")
async def archive_github_repos(request: Request):
    """批量归档 GitHub 仓库"""
    if not token_manager.is_github_configured():
        raise HTTPException(status_code=401, detail="GitHub Token 未配置")
    
    data = await request.json()
    repo_names = data.get("repos", [])
    
    if not repo_names:
        raise HTTPException(status_code=400, detail="请选择要归档的仓库")
    
    api = GitHubAPI(token_manager.get_github_token())
    results = {}
    for name in repo_names:
        results[name] = api.archive_repo(name)
    
    success = sum(results.values())
    return {
        "success": success,
        "total": len(repo_names),
        "results": results
    }


@app.post("/api/repos/gitee/delete")
async def delete_gitee_repos(request: Request):
    """批量删除 Gitee 仓库"""
    if not token_manager.is_gitee_configured():
        raise HTTPException(status_code=401, detail="Gitee Token 未配置")
    
    data = await request.json()
    repo_full_names = data.get("repos", [])
    
    if not repo_full_names:
        raise HTTPException(status_code=400, detail="请选择要删除的仓库")
    
    api = GiteeAPI(token_manager.get_gitee_token())
    results = api.batch_delete_repos(repo_full_names)
    
    success = sum(results.values())
    return {
        "success": success,
        "total": len(repo_full_names),
        "results": results
    }


@app.post("/api/settings/token")
async def save_token(request: Request):
    """保存 Token"""
    data = await request.json()
    platform = data.get("platform")
    token = data.get("token")
    
    if not platform or not token:
        raise HTTPException(status_code=400, detail="参数错误")
    
    if platform == "github":
        token_manager.set_github_token(token)
    elif platform == "gitee":
        token_manager.set_gitee_token(token)
    else:
        raise HTTPException(status_code=400, detail="未知平台")
    
    return {"success": True, "message": "Token 已保存"}


@app.post("/api/settings/stats-url")
async def save_stats_url(request: Request):
    """保存 Stats 服务 URL"""
    data = await request.json()
    stats_url = data.get("stats_url", "")
    streak_url = data.get("streak_url", "")
    trophies_url = data.get("trophies_url", "")
    
    token_manager.set_stats_url(stats_url, streak_url, trophies_url)
    
    return {"success": True, "message": "Stats 配置已保存"}


@app.post("/api/settings/test-token")
async def test_token(request: Request):
    """测试 Token 连接"""
    data = await request.json()
    platform = data.get("platform")
    token = data.get("token")
    
    if not token:
        raise HTTPException(status_code=400, detail="请输入 Token")
    
    try:
        if platform == "github":
            api = GitHubAPI(token)
            user = api.get_user_info()
            return {"success": True, "user": user}
        elif platform == "gitee":
            api = GiteeAPI(token)
            user = api.get_user_info()
            return {"success": True, "user": user}
        else:
            raise HTTPException(status_code=400, detail="未知平台")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"连接失败: {str(e)}")


@app.post("/api/profile/generate")
async def generate_profile(request: Request):
    """生成 Profile README"""
    data = await request.json()

    # 使用自定义 Stats URL（如果配置了的话）
    stats_url = token_manager.get_stats_url()
    streak_url = token_manager.get_streak_url()
    trophies_url = token_manager.get_trophies_url()
    generator = ProfileGenerator(stats_url=stats_url, streak_url=streak_url, trophies_url=trophies_url)

    config = {
        'username': data.get('username', 'username'),
        'name': data.get('name', 'Developer'),
        'bio': data.get('bio', ''),
        'greeting': data.get('greeting', 'Hi there! 👋'),
        'skills': data.get('skills', []),
        'custom_skills': data.get('custom_skills', []),
        'socials': data.get('socials', {}),
        'custom_socials': data.get('custom_socials', []),
        'show_stats': data.get('show_stats', True),
        'show_streak': data.get('show_streak', True),
        'show_languages': data.get('show_languages', True),
        'show_trophy': data.get('show_trophy', False),
        'show_activity': data.get('show_activity', False),
        'show_quote': data.get('show_quote', False),
        'show_joke': data.get('show_joke', False),
        'show_snake': data.get('show_snake', False),
        'theme': data.get('theme', 'radical'),
        'intro_items': data.get('intro_items', []),
        'layout': data.get('layout', 'single'),
        'streak_locale': data.get('streak_locale', 'en'),
        'badge_layout': data.get('badge_layout', 'inline'),
    }

    readme_content = generator.generate_profile(config)
    return {"content": readme_content}


@app.post("/api/profile/deploy")
async def deploy_profile(request: Request):
    """部署 Profile README"""
    if not token_manager.is_github_configured():
        raise HTTPException(status_code=401, detail="GitHub Token 未配置")

    data = await request.json()
    content = data.get("content")

    if not content:
        raise HTTPException(status_code=400, detail="内容为空")

    try:
        api = GitHubAPI(token_manager.get_github_token())
        success = api.update_profile_readme(content)
        if success:
            user = api.get_user_info()
            return {"success": True, "profile_url": f"https://github.com/{user['login']}"}
        else:
            raise HTTPException(status_code=500, detail="部署失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/profile/restore")
async def restore_profile():
    """恢复默认 GitHub Profile（删除自定义 README）"""
    if not token_manager.is_github_configured():
        raise HTTPException(status_code=401, detail="GitHub Token 未配置")

    try:
        api = GitHubAPI(token_manager.get_github_token())
        success = api.delete_profile_readme()
        if success:
            user = api.get_user_info()
            return {"success": True, "profile_url": f"https://github.com/{user['login']}"}
        else:
            raise HTTPException(status_code=500, detail="恢复失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 启动入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
