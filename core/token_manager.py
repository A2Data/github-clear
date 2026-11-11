"""Thread-safe configuration shared by pages and API clients."""

import os
from pathlib import Path
from threading import RLock

from dotenv import dotenv_values, set_key


class TokenManager:
    """Load process environment first, then .env; persist UI edits before caching."""

    _env_path = Path(__file__).resolve().parent.parent / ".env"
    _keys = ("GITHUB_TOKEN", "GITEE_TOKEN", "STATS_URL", "STREAK_URL", "TROPHIES_URL")

    def __init__(self, env_path: Path | None = None):
        self._env_path = env_path if env_path is not None else self._env_path
        self._lock = RLock()
        values = dotenv_values(self._env_path, interpolate=False)
        self._cache = {
            key: os.environ.get(key, values.get(key) or "").strip()
            for key in self._keys
        }

    def _get(self, key: str) -> str:
        with self._lock:
            return self._cache.get(key, "")

    def _save_values(self, values: dict[str, str]):
        with self._lock:
            for key, value in values.items():
                # dotenv quotes values and atomically replaces the file, preserving
                # comments and unrelated settings. Failed writes leave the cache intact.
                set_key(
                    self._env_path, key, value, quote_mode="always", encoding="utf-8"
                )
                self._cache[key] = value

    def get_github_token(self) -> str:
        return self._get("GITHUB_TOKEN")

    def get_gitee_token(self) -> str:
        return self._get("GITEE_TOKEN")

    def set_github_token(self, token: str):
        self._save_values({"GITHUB_TOKEN": token})

    def set_gitee_token(self, token: str):
        self._save_values({"GITEE_TOKEN": token})

    def is_github_configured(self) -> bool:
        token = self.get_github_token()
        return bool(token and token != "your_github_token_here" and len(token) > 10)

    def is_gitee_configured(self) -> bool:
        token = self.get_gitee_token()
        return bool(token and token != "your_gitee_token_here" and len(token) > 10)


_manager = None
_manager_lock = RLock()


def _get_manager() -> TokenManager:
    global _manager
    with _manager_lock:
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
    return _get_manager()._get("STATS_URL")


def get_streak_url() -> str:
    return _get_manager()._get("STREAK_URL")


def get_trophies_url() -> str:
    return _get_manager()._get("TROPHIES_URL")


def set_stats_url(stats_url: str, streak_url: str, trophies_url: str | None = None):
    from core.schemas import StatsURLRequest

    data = StatsURLRequest(
        stats_url=stats_url, streak_url=streak_url, trophies_url=trophies_url
    )
    values = {"STATS_URL": data.stats_url, "STREAK_URL": data.streak_url}
    if data.trophies_url is not None:
        values["TROPHIES_URL"] = data.trophies_url
    _get_manager()._save_values(values)
