"""插件注册表：集中收集、装配所有行业插件。"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.plugins.base import BasePlugin

if TYPE_CHECKING:
    from fastapi import FastAPI

_ENABLED: list[BasePlugin] = []


def register(plugin: BasePlugin) -> None:
    _ENABLED.append(plugin)


def all_plugins() -> list[BasePlugin]:
    return list(_ENABLED)


def collect_permissions() -> list[str]:
    """把所有插件声明的权限去重合并（阶段 2 才接入 ALL_PERMISSIONS）。"""
    perms: list[str] = []
    for p in _ENABLED:
        for perm in p.permissions:
            if perm not in perms:
                perms.append(perm)
    return perms


def install_models() -> None:
    """bootstrap 早期调用，触发所有插件模型注册到 SQLModel.metadata。"""
    for p in _ENABLED:
        p.register_models()


def install_routes(app: "FastAPI") -> None:
    """阶段 2 才开始使用；阶段 1 不调用，保持 main.py 现有 include 顺序。"""
    for p in _ENABLED:
        p.register_routes(app)