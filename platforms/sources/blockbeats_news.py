"""
BlockBeats 律动快讯平台实现
从 https://api.blockbeats.cn/v2/newsflash/list API 获取数据
"""

import json
import random
import time
from typing import Dict, Optional, Tuple

import requests

from ..base import BasePlatform


class BlockBeatsNews(BasePlatform):
    """律动快讯 - 从 BlockBeats API 获取快讯数据"""
    
    # API 基础 URL
    API_BASE_URL = "https://api.blockbeats.cn/v2/newsflash/list"
    
    def __init__(
        self,
        platform_id: str,
        platform_name: str = None,
        proxy_url: Optional[str] = None,
        max_items: int = 20,
        limit: int = 20,
        **kwargs
    ):
        """
        初始化 BlockBeats 平台
        
        Args:
            platform_id: 平台ID
            platform_name: 平台名称，默认 "律动快讯"
            proxy_url: 代理URL（可选）
            max_items: 最大获取条目数，默认 20
            limit: 每页数量，默认 20（API 最大支持 50，仅获取第一页）
        """
        super().__init__(
            platform_id,
            platform_name or "律动快讯",
            proxy_url,
            **kwargs
        )
        self.max_items = max_items
        self.limit = min(limit, 50)  # API 限制每页最多 50 条
    
    def fetch_data(
        self,
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """
        获取 BlockBeats 快讯数据
        
        Args:
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间（秒）
            max_retry_wait: 最大重试等待时间（秒）
        
        Returns:
            (数据字典, 平台ID, 平台名称)
        """
        # 构建请求头（模拟浏览器请求）
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://www.theblockbeats.info",
            "Referer": "https://www.theblockbeats.info/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "lang": "cn",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }
        
        proxies = None
        if self.proxy_url:
            proxies = {"http": self.proxy_url, "https": self.proxy_url}
        
        retries = 0
        
        # 重试逻辑
        while retries <= max_retries:
            try:
                # 构建查询参数（仅获取第一页）
                params = {
                    "page": 1,
                    "limit": self.limit,
                    "ios": -2,  # -2 表示获取所有（iOS 和非 iOS）
                    "detective": -2,  # -2 表示获取所有（侦探和非侦探）
                }
                
                response = requests.get(
                    self.API_BASE_URL,
                    params=params,
                    headers=headers,
                    proxies=proxies,
                    timeout=10
                )
                
                response.raise_for_status()
                data = json.loads(response.text)
                
                # 检查 API 响应状态
                if data.get("code") != 0:
                    error_msg = data.get("msg", "未知错误")
                    raise ValueError(f"API 返回错误: {error_msg}")
                
                # 解析数据
                data_list = data.get("data", {}).get("list", [])
                
                if not data_list:
                    print(f"[{self.platform_name}] 未获取到数据")
                    return None, self.platform_id, self.platform_name
                
                # 转换为标准格式
                items = []
                for index, item in enumerate(data_list[:self.max_items], 1):
                    title = item.get("title", "")
                    if not title or not str(title).strip():
                        continue
                    
                    # 构建完整 URL
                    url = item.get("url", "")
                    
                    # 如果 url 为空，使用 article_id 构造 URL
                    if not url or not str(url).strip():
                        article_id = item.get("article_id")
                        if article_id:
                            url = f"https://www.theblockbeats.info/flash/{article_id}"
                        else:
                            url = ""  # 如果 article_id 也不存在，保持为空
                    # 如果 url 存在但不是完整 URL，处理相对路径
                    elif url and not url.startswith(("http://", "https://")):
                        url = f"https://www.theblockbeats.info{url}" if url.startswith("/") else url
                    
                    items.append({
                        "title": str(title).strip(),
                        "url": url,
                        "mobileUrl": url,  # BlockBeats 使用相同 URL
                        "rank": index
                    })
                
                print(f"[{self.platform_name}] 获取成功，共 {len(items)} 条")
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

