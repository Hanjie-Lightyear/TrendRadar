"""
平台模块 - 每个平台作为独立实体，拥有自己的数据采集实现
"""

from .factory import create_platform, register_platform, PLATFORM_REGISTRY
from .data_fetcher import DataFetcherV2

# 导出主要接口
__all__ = [
    "create_platform",
    "register_platform",
    "PLATFORM_REGISTRY",
    "DataFetcherV2",
]

