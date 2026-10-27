"""汽配行业插件（阶段 1 空壳，路由仍由 main.py 直接注册）。"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.plugins.base import BasePlugin

if TYPE_CHECKING:
    from fastapi import FastAPI


class AutoPartsPlugin(BasePlugin):
    code = "auto_parts"
    name = "汽配行业插件"
    permissions = [
        "parts:view",
        "parts:manage",
        "parts:import",
    ]

    def register_routes(self, app: "FastAPI") -> None:
        # 阶段 1 保持空：避免和 main.py 里既有的 app.include_router(parts.router) 重复注册
        return None

    def register_models(self) -> None:
        # 阶段 1 保持空：AutoPart 等表仍定义在 app/models.py
        return None