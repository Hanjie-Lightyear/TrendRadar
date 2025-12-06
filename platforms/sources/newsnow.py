"""
NewsNow 平台实现 - 基于 NewsNow API 的平台
"""

import json
import random
import time
from typing import Dict, Optional, Tuple

import requests

from ..base import BasePlatform


class NewsNowPlatform(BasePlatform):
    """NewsNow 平台基类"""
    
    def __init__(
        self,
        platform_id: str,
        platform_name: str = None,
        proxy_url: Optional[str] = None,
        api_base_url: str = None,
        **kwargs
    ):
        """
        初始化 NewsNow 平台
        
        Args:
            platform_id: 平台ID（对应 NewsNow API 的 id 参数）
            platform_name: 平台名称
            proxy_url: 代理URL
            api_base_url: API基础URL，默认使用官方地址
        """
        super().__init__(platform_id, platform_name, proxy_url, **kwargs)
        self.api_base_url = api_base_url or "https://newsnow.busiyi.world/api/s"
    
    def fetch_data(
        self,
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """获取平台数据"""
        url = f"{self.api_base_url}?id={self.platform_id}&latest"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }
        
        proxies = None
        if self.proxy_url:
            proxies = {"http": self.proxy_url, "https": self.proxy_url}
        
        retries = 0
        while retries <= max_retries:
            try:
                response = requests.get(
                    url, proxies=proxies, headers=headers, timeout=10
                )
                response.raise_for_status()
                
                data_text = response.text
                data_json = json.loads(data_text)
                
                status = data_json.get("status", "未知")
                if status not in ["success", "cache"]:
                    raise ValueError(f"响应状态异常: {status}")
                
                # 转换为标准格式
                items = []
                for index, item in enumerate(data_json.get("items", []), 1):
                    title = item.get("title")
                    if title is None or isinstance(title, float) or not str(title).strip():
                        continue
                    
                    items.append({
                        "title": str(title).strip(),
                        "url": item.get("url", ""),
                        "mobileUrl": item.get("mobileUrl", ""),
                        "rank": index
                    })
                
                status_info = "最新数据" if status == "success" else "缓存数据"
                print(f"[{self.platform_name}] 获取成功（{status_info}），共 {len(items)} 条")
                
                return {"items": items}, self.platform_id, self.platform_name
                
            except Exception as e:
                retries += 1
                if retries <= max_retries:
                    base_wait = random.uniform(min_retry_wait, max_retry_wait)
                    additional_wait = (retries - 1) * random.uniform(1, 2)
                    wait_time = base_wait + additional_wait
                    print(f"[{self.platform_name}] 请求失败: {e}. {wait_time:.2f}秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"[{self.platform_name}] 请求失败: {e}")
                    return None, self.platform_id, self.platform_name
        
        return None, self.platform_id, self.platform_name


# 各个平台的具体实现（可以添加平台特定的逻辑）
class ZhihuPlatform(NewsNowPlatform):
    """知乎平台"""
    pass


class WeiboPlatform(NewsNowPlatform):
    """微博平台"""
    pass


class DouyinPlatform(NewsNowPlatform):
    """抖音平台"""
    pass


class BaiduPlatform(NewsNowPlatform):
    """百度热搜平台"""
    pass


class ToutiaoPlatform(NewsNowPlatform):
    """今日头条平台"""
    pass


class BilibiliPlatform(NewsNowPlatform):
    """Bilibili 热搜平台"""
    pass


class TiebaPlatform(NewsNowPlatform):
    """贴吧平台"""
    pass


class ThepaperPlatform(NewsNowPlatform):
    """澎湃新闻平台"""
    pass


class IfengPlatform(NewsNowPlatform):
    """凤凰网平台"""
    pass


class WallstreetcnPlatform(NewsNowPlatform):
    """华尔街见闻平台"""
    pass


class ClsHotPlatform(NewsNowPlatform):
    """财联社热门平台"""
    pass

