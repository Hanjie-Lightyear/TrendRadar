"""
数据源实现模块 - 各种平台的具体实现
"""

from .newsnow import (
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
)

from .blockbeats_news import BlockBeatsNews
from .wushuo import WushuoPlatform
from .panews import PanewsPlatform
from .binance_news import BinanceNewsPlatform
from .aibase import AIBasePlatform

__all__ = [
    "NewsNowPlatform",
    "ZhihuPlatform",
    "WeiboPlatform",
    "DouyinPlatform",
    "BaiduPlatform",
    "ToutiaoPlatform",
    "BilibiliPlatform",
    "TiebaPlatform",
    "ThepaperPlatform",
    "IfengPlatform",
    "WallstreetcnPlatform",
    "ClsHotPlatform",
    "BlockBeatsNews",
    "WushuoPlatform",
    "PanewsPlatform",
    "BinanceNewsPlatform",
    "AIBasePlatform",
]

