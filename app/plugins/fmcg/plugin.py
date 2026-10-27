"""超市/快消行业插件（阶段 1 空壳，阶段 2 引入模型）。"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.plugins.base import BasePlugin

if TYPE_CHECKING:
    from fastapi import FastAPI


class FmcgPlugin(BasePlugin):
    code = "fmcg"
    name = "超市/快消行业插件"
    permissions: list[str] = []

    def register_routes(self, app: "FastAPI") -> None:
        from app.plugins.fmcg.routers import wallet as wallet_router
        app.include_router(wallet_router.router)

    def register_models(self) -> None:
        # 触发 SQLModel.metadata 注册，必须在 Alembic autogenerate 之前完成
        from app.plugins.fmcg import models  # noqa: F401
