"""
Panews 平台实现
从 https://api.panewslab.com/webapi/flashnews API 获取数据
"""

import json
import random
import time
from typing import Dict, Optional, Tuple

import requests

from ..base import BasePlatform


class PanewsPlatform(BasePlatform):
    """Panews - 从 Panews API 获取快讯数据"""
    
    # API 基础 URL
    API_BASE_URL = "https://api.panewslab.com/webapi/flashnews"
    
    def __init__(
        self,
        platform_id: str,
        platform_name: str = None,
        proxy_url: Optional[str] = None,
        max_items: int = 20,
        rn: int = 20,
        lid: int = 1,
        **kwargs
    ):
        """
        初始化 Panews 平台
        
        Args:
            platform_id: 平台ID
            platform_name: 平台名称，默认 "Panews"
            proxy_url: 代理URL（可选）
            max_items: 最大获取条目数，默认 20
            rn: 每页数量，默认 20（仅获取第一页）
            lid: 列表ID，默认 1
        """
        super().__init__(
            platform_id,
            platform_name or "Panews",
            proxy_url,
            **kwargs
        )
        self.max_items = max_items
        self.rn = rn
        self.lid = lid
    
    def fetch_data(
        self,
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """
        获取 Panews 快讯数据
        
        Args:
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间（秒）
            max_retry_wait: 最大重试等待时间（秒）
        
        Returns:
            (数据字典, 平台ID, 平台名称)
        """
        # 构建请求头（模拟浏览器请求）
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "https://www.panewslab.com",
            "priority": "u=1, i",
            "referer": "https://www.panewslab.com/",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
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
                    "rn": self.rn,
                    "lid": self.lid,
                    "apppush": 0,
                }
                
                response = requests.get(
                    self.API_BASE_URL,
                    params=params,
                    headers=headers,
                    proxies=proxies,
                    timeout=10
                )
                
                response.raise_for_status()
                data_json = json.loads(response.text)
                
                # 检查 API 响应状态
                # Panews API: errno: 0 表示成功
                errno = data_json.get("errno")
                if errno != 0:
                    error_msg = data_json.get("msg", "未知错误")
                    raise ValueError(f"API 返回错误: {error_msg} (errno: {errno})")
                
                # 解析数据
                # 响应格式：{"errno": 0, "data": {"flashNews": [{"list": [...]}]}}
                data = data_json.get("data", {})
                flash_news = data.get("flashNews", [])
                
                # 获取第一个日期组的快讯列表（最新的）
                data_list = []
                if flash_news and isinstance(flash_news, list) and len(flash_news) > 0:
                    first_group = flash_news[0]
                    if isinstance(first_group, dict) and "list" in first_group:
                        data_list = first_group["list"]
                
                if not data_list or not isinstance(data_list, list):
                    print(f"[{self.platform_name}] 未获取到数据")
                    return None, self.platform_id, self.platform_name
                
                # 转换为标准格式
                items = []
                for index, item in enumerate(data_list[:self.max_items], 1):
                    title = item.get("title", "")
                    if not title or not str(title).strip():
                        continue
                    
                    # 使用 id 构造 URL
                    # Panews 快讯 URL 格式：https://www.panewslab.com/flash/{id}
                    item_id = item.get("id", "")
                    if item_id:
                        url = f"https://www.panewslab.com/zh/articles/{item_id}"
                    else:
                        url = ""
                    
                    items.append({
                        "title": str(title).strip(),
                        "url": url,
                        "mobileUrl": url,  # Panews 使用相同 URL
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

