"""超市/快消行业插件（阶段 1 空壳）。"""
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
        return None

    def register_models(self) -> None:
        return None