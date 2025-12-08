"""
币安广场平台实现
从 https://www.binance.com/bapi/composite/v4/friendly/pgc/feed/news/list API 获取数据
"""

import json
import random
import time
from typing import Dict, Optional, Tuple

import requests

from ..base import BasePlatform


class BinanceNewsPlatform(BasePlatform):
    """币安广场 - 从 Binance API 获取新闻数据"""
    
    # API 基础 URL
    API_BASE_URL = "https://www.binance.com/bapi/composite/v4/friendly/pgc/feed/news/list"
    
    def __init__(
        self,
        platform_id: str,
        platform_name: str = None,
        proxy_url: Optional[str] = None,
        max_items: int = 20,
        page_size: int = 20,
        strategy: int = 6,
        tag_id: int = 0,
        featured: bool = False,
        **kwargs
    ):
        """
        初始化币安广场平台
        
        Args:
            platform_id: 平台ID
            platform_name: 平台名称，默认 "币安广场"
            proxy_url: 代理URL（可选）
            max_items: 最大获取条目数，默认 20
            page_size: 每页数量，默认 20（仅获取第一页）
            strategy: 策略ID，默认 6
            tag_id: 标签ID，默认 0
            featured: 是否精选，默认 False
        """
        super().__init__(
            platform_id,
            platform_name or "币安广场",
            proxy_url,
            **kwargs
        )
        self.max_items = max_items
        self.page_size = page_size
        self.strategy = strategy
        self.tag_id = tag_id
        self.featured = featured
    
    def fetch_data(
        self,
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """
        获取币安广场新闻数据
        
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
            "bnc-level": "0",
            "bnc-location": "CN",
            "bnc-time-zone": "Asia/Shanghai",
            "clienttype": "web",
            "content-type": "application/json",
            "lang": "zh-CN",
            "priority": "u=1, i",
            "referer": "https://www.binance.com/zh-CN/square/news/binance-news",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
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
                    "pageIndex": 1,
                    "pageSize": self.page_size,
                    "strategy": self.strategy,
                    "tagId": self.tag_id,
                    "featured": str(self.featured).lower(),
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
                # 币安 API: code: "000000" 且 success: true 表示成功
                code = data_json.get("code")
                success = data_json.get("success", False)
                
                if code != "000000" or not success:
                    error_msg = data_json.get("message", data_json.get("messageDetail", "未知错误"))
                    raise ValueError(f"API 返回错误: {error_msg} (code: {code}, success: {success})")
                
                # 解析数据
                # 响应格式：{"code": "000000", "success": true, "data": {"vos": [...]}}
                data = data_json.get("data", {})
                data_list = data.get("vos", [])
                
                if not data_list or not isinstance(data_list, list):
                    print(f"[{self.platform_name}] 未获取到数据")
                    return None, self.platform_id, self.platform_name
                
                # 转换为标准格式
                items = []
                for index, item in enumerate(data_list[:self.max_items], 1):
                    title = item.get("title", "")
                    if not title or not str(title).strip():
                        continue
                    
                    # 获取 URL（优先使用 webLink）
                    url = item.get("webLink", "")
                    
                    # 如果 webLink 为空，使用 id 构造 URL
                    if not url or not str(url).strip():
                        item_id = item.get("id", "")
                        if item_id:
                            url = f"https://www.binance.com/zh-CN/square/post/{item_id}"
                        else:
                            url = ""
                    
                    items.append({
                        "title": str(title).strip(),
                        "url": url,
                        "mobileUrl": url,  # 币安广场使用相同 URL
                        "rank": index
                    })
                
                print(f"[{self.platform_name}] 获取成功，共 {len(items)} 条")
                return {"items": items}, self.platform_id, self.platform_name
                
            except requests.exceptions.ConnectionError as e:
                retries += 1
                error_msg = str(e)
                # 提供更友好的错误提示
                if "Connection refused" in error_msg or "Failed to establish" in error_msg:
                    proxy_hint = f"（提示：当前代理设置: {'已启用' if self.proxy_url else '未启用'}）"
                    error_msg = f"连接被拒绝，无法访问币安服务器{proxy_hint}"
                
                if retries <= max_retries:
                    base_wait = random.uniform(min_retry_wait, max_retry_wait)
                    additional_wait = (retries - 1) * random.uniform(1, 2)
                    wait_time = base_wait + additional_wait
                    print(f"[{self.platform_name}] 请求失败: {error_msg}. {wait_time:.2f}秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"[{self.platform_name}] 请求失败: {error_msg}。已重试 {max_retries} 次，跳过此平台")
                    return None, self.platform_id, self.platform_name
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

