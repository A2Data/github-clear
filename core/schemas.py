"""Validated inputs for settings and repository mutations."""

import re
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, field_validator


class RepoBatchRequest(BaseModel):
    repos: list[str] = Field(min_length=1, max_length=1000)

    @field_validator("repos")
    @classmethod
    def validate_repos(cls, repos: list[str]) -> list[str]:
        normalized = []
        for repo in repos:
            repo = repo.strip()
            if (
                len(repo) > 255
                or not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?", repo)
                or any(part in {".", ".."} for part in repo.split("/"))
            ):
                raise ValueError("仓库名称必须为 name 或 owner/name")
            normalized.append(repo)
        return list(dict.fromkeys(normalized))


class TokenRequest(BaseModel):
    platform: Literal["github", "gitee"]
    token: str = Field(min_length=1, max_length=4096)

    @field_validator("token")
    @classmethod
    def validate_token(cls, token: str) -> str:
        token = token.strip()
        if not token or any(char.isspace() or ord(char) < 32 for char in token):
            raise ValueError("Token 不能为空或包含空白字符")
        return token


class StatsURLRequest(BaseModel):
    stats_url: str = ""
    streak_url: str = ""
    # Omitted fields must not erase the Trophy URL saved by another page.
    trophies_url: str | None = None

    @field_validator("stats_url", "streak_url", "trophies_url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return ""
        if any(char.isspace() or ord(char) < 32 for char in value):
            raise ValueError("服务 URL 不能包含空白字符")
        if "://" not in value:
            value = f"https://{value}"
        parsed = urlsplit(value)
        # Accessing .port also validates malformed or out-of-range ports.
        parsed.port
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            raise ValueError("请输入有效的 HTTP(S) 服务 URL")
        return value


class ProfileDeployRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1_000_000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, content: str) -> str:
        if not content.strip():
            raise ValueError("内容为空")
        return content
