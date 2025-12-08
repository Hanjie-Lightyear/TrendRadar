"""
AIBase 平台实现
从 https://mcpapi.aibase.cn/api/aiInfo/aiNews API 获取数据
"""

import json
import random
import time
from typing import Dict, Optional, Tuple

import requests

from ..base import BasePlatform


class AIBasePlatform(BasePlatform):
    """AIBase - 从 AIBase API 获取新闻数据"""
    
    # API 基础 URL
    API_BASE_URL = "https://mcpapi.aibase.cn/api/aiInfo/aiNews"
    
    def __init__(
        self,
        platform_id: str,
        platform_name: str = None,
        proxy_url: Optional[str] = None,
        max_items: int = 20,
        page_no: int = 1,
        lang_type: str = "zh_cn",
        **kwargs
    ):
        """
        初始化 AIBase 平台
        
        Args:
            platform_id: 平台ID
            platform_name: 平台名称，默认 "AIBase"
            proxy_url: 代理URL（可选）
            max_items: 最大获取条目数，默认 20
            page_no: 页码，默认 1
            lang_type: 语言类型，默认 "zh_cn"
        """
        super().__init__(
            platform_id,
            platform_name or "AIBase",
            proxy_url,
            **kwargs
        )
        self.max_items = max_items
        self.page_no = page_no
        self.lang_type = lang_type
    
    def fetch_data(
        self,
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """
        获取 AIBase 新闻数据
        
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
            "content-type": "application/json",
            "origin": "https://news.aibase.com",
            "priority": "u=1, i",
            "referer": "https://news.aibase.com/",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        }
        
        proxies = None
        if self.proxy_url:
            proxies = {"http": self.proxy_url, "https": self.proxy_url}
        
        retries = 0
        
        # 重试逻辑
        while retries <= max_retries:
            try:
                # 生成时间戳
                timestamp = int(time.time() * 1000)
                
                # 构建查询参数
                params = {
                    "t": timestamp,
                    "langType": self.lang_type,
                    "pageNo": self.page_no,
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
                
                # 先尝试解析数据，如果数据存在就认为成功
                # 这样可以兼容不同的成功状态码（0, 200, 1 等）
                data_list = []
                if "data" in data:
                    data_content = data["data"]
                    if isinstance(data_content, list):
                        data_list = data_content
                    elif isinstance(data_content, dict):
                        # 尝试常见的字段名
                        data_list = (
                            data_content.get("list", []) or
                            data_content.get("items", []) or
                            data_content.get("data", []) or
                            []
                        )
                
                # 如果数据存在，就认为成功，跳过 code 检查
                # 如果数据不存在，再检查错误状态码
                if not data_list:
                    # 检查 API 响应状态（仅在无数据时检查）
                    # 常见的响应格式可能是 {"code": 0, "data": [...]} 或 {"success": true, "data": [...]}
                    code = data.get("code")
                    # 常见的成功状态码：0, 200, 1
                    if code is not None and code not in [0, 200, 1]:
                        error_msg = data.get("msg", data.get("message", "未知错误"))
                        raise ValueError(f"API 返回错误: {error_msg}")
                    
                    if "success" in data and not data.get("success"):
                        error_msg = data.get("message", "未知错误")
                        raise ValueError(f"API 返回错误: {error_msg}")
                    
                    print(f"[{self.platform_name}] 未获取到数据")
                    return None, self.platform_id, self.platform_name
                
                # 转换为标准格式
                items = []
                for index, item in enumerate(data_list[:self.max_items], 1):
                    # 尝试常见的标题字段
                    title = (
                        item.get("title", "") or
                        item.get("name", "") or
                        item.get("headline", "") or
                        ""
                    )
                    
                    if not title or not str(title).strip():
                        continue
                    
                    # 优先使用 oid 构造 URL
                    oid = item.get("oid")
                    if oid:
                        url = f"https://news.aibase.com/zh/news/{oid}"
                    else:
                        # 如果没有 oid，尝试常见的 URL 字段
                        url = (
                            item.get("url", "") or
                            item.get("link", "") or
                            item.get("href", "") or
                            ""
                        )
                        
                        # 如果还是没有 URL，尝试用其他 ID 字段构造
                        if not url:
                            item_id = item.get("id") or item.get("newsId") or item.get("articleId")
                            if item_id:
                                url = f"https://news.aibase.com/zh/daily/{item_id}"
                    
                    items.append({
                        "title": str(title).strip(),
                        "url": url,
                        "mobileUrl": url,  # AIBase 使用相同 URL
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
