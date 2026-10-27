"""插件自动注册入口：import 本模块即完成所有行业插件注册。"""
from app.plugins import registry
from app.plugins.registry import register
from app.plugins.auto_parts.plugin import AutoPartsPlugin
from app.plugins.fmcg.plugin import FmcgPlugin

register(AutoPartsPlugin())
register(FmcgPlugin())

# 向后兼容：让 `from app import plugins; plugins.all_plugins()` 等用法生效
all_plugins = registry.all_plugins
collect_permissions = registry.collect_permissions
install_models = registry.install_models
install_routes = registry.install_routes
