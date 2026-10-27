"""插件协议：所有行业插件都继承 BasePlugin。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from fastapi import FastAPI


class BasePlugin(ABC):
    code: ClassVar[str]                    # 例如 "auto_parts" / "fmcg"
    name: ClassVar[str]                    # 人类可读名
    permissions: ClassVar[list[str]] = []  # 该插件贡献的权限位

    @abstractmethod
    def register_routes(self, app: "FastAPI") -> None:
        """把路由注册到 FastAPI 实例。阶段 1 允许空实现。"""

    def register_models(self) -> None:
        """在 bootstrap 早期 import 自己的 models 模块，把表注册进 SQLModel.metadata。
        默认不做事；有独立表的插件覆盖。"""
        return None