"""FMCG 服务层业务异常。"""


class FmcgError(Exception):
    """FMCG 插件所有业务异常的基类。"""


class WalletError(FmcgError):
    """钱包操作异常（金额非法、参数错误等）。"""


class InsufficientBalance(WalletError):
    """扣减时余额不足。"""


class WalletNotFound(WalletError):
    """查询的钱包不存在。"""
