"""
平台工厂 - 创建平台实例
"""

from .base import BasePlatform
from .sources import (
    NewsNowPlatform,
    ZhihuPlatform,
    WeiboPlatform,
    DouyinPlatform,
    BaiduPlatform,
    ToutiaoPlatform,
    BilibiliPlatform,
    TiebaPlatform,
    ThepaperPlatform,
    IfengPlatform,
    WallstreetcnPlatform,
    ClsHotPlatform,
    BlockBeatsNews,
    WushuoPlatform,
    PanewsPlatform,
    BinanceNewsPlatform,
)

# 平台注册表 - 根据 platform_id 自动识别平台类型
PLATFORM_REGISTRY = {
    # NewsNow 平台
    "zhihu": ZhihuPlatform,
    "weibo": WeiboPlatform,
    "douyin": DouyinPlatform,
    "baidu": BaiduPlatform,
    "toutiao": ToutiaoPlatform,
    "bilibili-hot-search": BilibiliPlatform,
    "tieba": TiebaPlatform,
    "thepaper": ThepaperPlatform,
    "ifeng": IfengPlatform,
    "wallstreetcn-hot": WallstreetcnPlatform,
    "cls-hot": ClsHotPlatform,

    "blockbeats-news": BlockBeatsNews,
    "wushuo": WushuoPlatform,
    "panews": PanewsPlatform,
    "binance-news": BinanceNewsPlatform,
}


def create_platform(platform_config: dict) -> BasePlatform:
    """
    根据配置创建平台实例
    
    Args:
        platform_config: 平台配置字典，包含:
            - id: 平台ID
            - name: 平台名称（可选）
            - platform_class: 平台类名（可选，用于自定义平台）
            - config: 平台特定配置（可选）
    
    Returns:
        平台实例
    
    Examples:
        >>> config = {"id": "zhihu", "name": "知乎"}
        >>> platform = create_platform(config)
        >>> data = platform.fetch_data()
    """
    platform_id = platform_config.get("id")
    platform_name = platform_config.get("name", platform_id)
    platform_specific_config = platform_config.get("config", {})
    
    # 方式 1: 根据 platform_id 自动识别
    platform_class = PLATFORM_REGISTRY.get(platform_id)
    if platform_class:
        return platform_class(platform_id, platform_name, **platform_specific_config)
    
    # 方式 2: 默认使用 NewsNow（向后兼容）
    return NewsNowPlatform(platform_id, platform_name, **platform_specific_config)


def register_platform(platform_id: str, platform_class: type):
    """
    注册自定义平台
    
    Args:
        platform_id: 平台ID
        platform_class: 平台类（必须继承 BasePlatform）
    
    Example:
        >>> class MyCustomPlatform(BasePlatform):
        ...     def fetch_data(self):
        ...         ...
        >>> register_platform("my_platform", MyCustomPlatform)
    """
    if not issubclass(platform_class, BasePlatform):
        raise TypeError(f"平台类必须继承 BasePlatform: {platform_class}")
    PLATFORM_REGISTRY[platform_id] = platform_class

