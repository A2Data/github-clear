"""GitHub/Gitee repository manager with Jinja2 pages and JSON APIs."""

from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Literal

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from github import GithubException
from requests import RequestException

from config.git_reference import ACCOUNT_STEPS, COMMAND_GROUPS
from core import token_manager
from core.github_api import GitHubAPI
from core.gitee_api import GiteeAPI
from core.profile_generator import ProfileGenerator
from core.schemas import (
    ProfileDeployRequest,
    RepoBatchRequest,
    StatsURLRequest,
    TokenRequest,
)

app = FastAPI(title="GitHub Clear", version="2.0.0")
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
# Inline the shared SVG shapes so individual icon parts can respond to hover.
# The source is a bundled local asset; no user-supplied markup is rendered here.
_icon_sheet = ET.parse(BASE_DIR / "static" / "icons.svg").getroot()
for _element in _icon_sheet.iter():
    _element.tag = _element.tag.split("}")[-1]
templates.env.globals["ui_icons"] = {
    symbol.attrib["id"]: "".join(
        ET.tostring(part, encoding="unicode") for part in symbol
    )
    for symbol in _icon_sheet
}


# These clients perform blocking I/O. Synchronous routes run in FastAPI's
# worker pool, leaving the event loop available to serve other requests.
Visibility = Literal["all", "public", "private"]
RepoSort = Literal["updated", "created", "pushed", "full_name"]


def upstream_error(exc):
    status = getattr(exc, "status", None)
    if status is None and getattr(exc, "response", None) is not None:
        status = exc.response.status_code
    messages = {
        401: "Token 无效或已过期，请检查设置",
        403: "权限不足或请求频率受限，请检查 Token 权限",
        404: "仓库或资源不存在",
        429: "请求频率受限，请稍后重试",
    }
    return status if status in messages else 502, messages.get(
        status, "上游服务请求失败，请检查网络后重试"
    )


@app.exception_handler(GithubException)
@app.exception_handler(RequestException)
async def handle_upstream_error(request: Request, exc: Exception):
    status, detail = upstream_error(exc)
    return JSONResponse(status_code=status, content={"detail": detail})


def github_api():
    if not token_manager.is_github_configured():
        raise HTTPException(status_code=401, detail="GitHub Token 未配置")
    return GitHubAPI(token_manager.get_github_token())


def gitee_api():
    if not token_manager.is_gitee_configured():
        raise HTTPException(status_code=401, detail="Gitee Token 未配置")
    return GiteeAPI(token_manager.get_gitee_token())


def page_context(request: Request):
    return {
        "request": request,
        "github_configured": token_manager.is_github_configured(),
        "gitee_configured": token_manager.is_gitee_configured(),
    }


@app.get("/health")
async def health():
    """Local liveness check; never depends on third-party credentials or APIs."""
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            **page_context(request),
            "command_count": sum(len(group["commands"]) for group in COMMAND_GROUPS),
        },
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    context = page_context(request)
    for platform, factory in (("github", github_api), ("gitee", gitee_api)):
        context[f"{platform}_user"] = None
        if context[f"{platform}_configured"]:
            try:
                with factory() as api:
                    context[f"{platform}_user"] = api.get_user_info()
            except (GithubException, RequestException):
                pass  # The page displays its connection error state.
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context=context
    )


@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    if not token_manager.is_github_configured():
        return {"repos": [], "stats": None}
    with github_api() as api:
        repos = api.list_repos(sort="updated")
    own_repos = [repo for repo in repos if not repo["fork"]]
    return {
        "repos": repos[:10],
        "stats": {
            "public_repos": sum(not repo["private"] for repo in own_repos),
            "private_repos": sum(repo["private"] for repo in own_repos),
            "total_repos": len(own_repos),
            "fork_repos": len(repos) - len(own_repos),
        },
    }


@app.get("/repositories", response_class=HTMLResponse)
def repositories(request: Request):
    return templates.TemplateResponse(
        request=request, name="repositories.html", context=page_context(request)
    )


@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):
    generator = ProfileGenerator()
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            **page_context(request),
            "available_skills": generator.get_available_skills(),
            "available_themes": generator.get_available_themes(),
            "stats_url": token_manager.get_stats_url()
            or ProfileGenerator.DEFAULT_STATS_URL,
            "streak_url": token_manager.get_streak_url()
            or ProfileGenerator.DEFAULT_STREAK_URL,
            "trophies_url": token_manager.get_trophies_url()
            or ProfileGenerator.DEFAULT_TROPHIES_URL,
        },
    )


@app.get("/guide", response_class=HTMLResponse)
def guide(request: Request):
    return templates.TemplateResponse(
        request=request, name="guide.html", context=page_context(request)
    )


@app.get("/DOCKER_DEPLOYMENT.md", response_class=FileResponse)
def docker_deployment_guide():
    return FileResponse(
        BASE_DIR / "DOCKER_DEPLOYMENT.md",
        media_type="text/markdown",
        filename="DOCKER_DEPLOYMENT.md",
    )


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    ssh_keys = []
    for pub_path in (Path.home() / ".ssh").glob("id_*.pub"):
        try:
            ssh_keys.append(
                {"name": pub_path.name, "content": pub_path.read_text(encoding="utf-8")}
            )
        except (OSError, UnicodeError):
            continue
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            **page_context(request),
            "ssh_keys": ssh_keys,
            "command_groups": COMMAND_GROUPS,
            "command_count": sum(len(group["commands"]) for group in COMMAND_GROUPS),
            "account_steps": ACCOUNT_STEPS,
            "stats_url": token_manager.get_stats_url(),
            "streak_url": token_manager.get_streak_url(),
            "trophies_url": token_manager.get_trophies_url(),
        },
    )


@app.get("/api/repos/github")
def get_github_repos(
    visibility: Visibility = "all",
    sort: RepoSort = "updated",
    include_forks: bool = True,
):
    with github_api() as api:
        return {
            "repos": api.list_repos(
                visibility=visibility, sort=sort, include_forks=include_forks
            )
        }


@app.get("/api/repos/github/collaborator")
def get_github_collaborator_repos():
    with github_api() as api:
        return {"repos": api.list_collaborator_repos()}


@app.get("/api/repos/gitee")
def get_gitee_repos(
    visibility: Visibility = "all",
    sort: RepoSort = "updated",
    include_forks: bool = True,
):
    with gitee_api() as api:
        return {
            "repos": api.list_repos(
                visibility=visibility, sort=sort, include_forks=include_forks
            )
        }


def run_batch(repos, operation):
    """Report each result, preserving completed work if a later request fails."""
    results, errors = {}, []
    for name in repos:
        try:
            result = operation(name)
            success, error = (
                result
                if isinstance(result, tuple)
                else (result, "操作失败，请检查仓库权限")
            )
        except (GithubException, RequestException) as exc:
            success, error = False, upstream_error(exc)[1]
        except ValueError as exc:
            success, error = False, str(exc)
        results[name] = bool(success)
        if not success:
            errors.append(f"{name}: {error}")
    response = {
        "success": sum(results.values()),
        "total": len(results),
        "results": results,
    }
    if errors:
        response["errors"] = errors
    return response


@app.post("/api/repos/github/leave")
def leave_github_repos(data: RepoBatchRequest):
    if any("/" not in name for name in data.repos):
        raise HTTPException(status_code=422, detail="协作仓库名称必须为 owner/name")
    with github_api() as api:
        return run_batch(data.repos, api.leave_repo)


@app.post("/api/repos/github/delete")
def delete_github_repos(data: RepoBatchRequest):
    with github_api() as api:
        return run_batch(data.repos, api.delete_repo)


@app.post("/api/repos/github/archive")
def archive_github_repos(data: RepoBatchRequest):
    with github_api() as api:
        return run_batch(data.repos, api.archive_repo)


@app.post("/api/repos/gitee/delete")
def delete_gitee_repos(data: RepoBatchRequest):
    if any("/" not in name for name in data.repos):
        raise HTTPException(status_code=422, detail="Gitee 仓库名称必须为 owner/name")
    with gitee_api() as api:
        return run_batch(data.repos, lambda name: api.delete_repo(*name.split("/")))


@app.post("/api/settings/token")
def save_token(data: TokenRequest):
    setter = (
        token_manager.set_github_token
        if data.platform == "github"
        else token_manager.set_gitee_token
    )
    setter(data.token)
    return {"success": True, "message": "Token 已保存"}


@app.post("/api/settings/stats-url")
def save_stats_url(data: StatsURLRequest):
    token_manager.set_stats_url(data.stats_url, data.streak_url, data.trophies_url)
    return {"success": True, "message": "Stats 配置已保存"}


@app.post("/api/settings/test-token")
def test_token(data: TokenRequest):
    factory = GitHubAPI if data.platform == "github" else GiteeAPI
    with factory(data.token) as api:
        return {"success": True, "user": api.get_user_info()}


@app.post("/api/profile/generate")
def generate_profile(data: dict = Body(...)):
    generator = ProfileGenerator(
        stats_url=token_manager.get_stats_url(),
        streak_url=token_manager.get_streak_url(),
        trophies_url=token_manager.get_trophies_url(),
    )
    config = {
        "username": data.get("username", "username"),
        "name": data.get("name", "Developer"),
        "bio": data.get("bio", ""),
        "greeting": data.get("greeting", "Hi there! 👋"),
        "header_style": data.get("header_style", "typing"),
        "skills": data.get("skills", []),
        "custom_skills": data.get("custom_skills", []),
        "socials": data.get("socials", {}),
        "custom_socials": data.get("custom_socials", []),
        "show_stats": data.get("show_stats", True),
        "show_streak": data.get("show_streak", True),
        "show_languages": data.get("show_languages", True),
        "show_trophy": data.get("show_trophy", False),
        "show_activity": data.get("show_activity", False),
        "show_quote": data.get("show_quote", False),
        "show_joke": data.get("show_joke", False),
        "show_snake": data.get("show_snake", False),
        "theme": data.get("theme", "radical"),
        "intro_items": data.get("intro_items", []),
        "layout": data.get("layout", "single"),
        "streak_locale": data.get("streak_locale", "en"),
        "badge_layout": data.get("badge_layout", "inline"),
        "components": data.get("components", []),
        "components_title": data.get("components_title", "Components"),
    }

    return {"content": generator.generate_profile(config)}


@app.post("/api/profile/deploy")
def deploy_profile(data: ProfileDeployRequest):
    with github_api() as api:
        if not api.update_profile_readme(data.content):
            raise HTTPException(status_code=502, detail="部署失败，请检查仓库权限")
        user = api.get_user_info()
        return {"success": True, "profile_url": f"https://github.com/{user['login']}"}


@app.post("/api/profile/restore")
def restore_profile():
    with github_api() as api:
        if not api.delete_profile_readme():
            raise HTTPException(status_code=502, detail="恢复失败，请检查仓库权限")
        user = api.get_user_info()
        return {"success": True, "profile_url": f"https://github.com/{user['login']}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
