"""
吴说平台实现
从 https://api.wublock123.com/api/site/getAllArticleList API 获取数据
"""

import json
import random
import time
from typing import Dict, Optional, Tuple

import requests

from ..base import BasePlatform


class WushuoPlatform(BasePlatform):
    """吴说 - 从 Wushuo API 获取文章数据"""
    
    # API 基础 URL
    API_BASE_URL = "https://api.wublock123.com/api/site/getAllArticleList"
    
    def __init__(
        self,
        platform_id: str,
        platform_name: str = None,
        proxy_url: Optional[str] = None,
        max_items: int = 20,
        page_size: int = 20,
        **kwargs
    ):
        """
        初始化吴说平台
        
        Args:
            platform_id: 平台ID
            platform_name: 平台名称，默认 "吴说"
            proxy_url: 代理URL（可选）
            max_items: 最大获取条目数，默认 20
            page_size: 每页数量，默认 20（仅获取第一页）
        """
        super().__init__(
            platform_id,
            platform_name or "吴说",
            proxy_url,
            **kwargs
        )
        self.max_items = max_items
        self.page_size = page_size
    
    def fetch_data(
        self,
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """
        获取吴说文章数据
        
        Args:
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间（秒）
            max_retry_wait: 最大重试等待时间（秒）
        
        Returns:
            (数据字典, 平台ID, 平台名称)
        """
        # 构建请求头（模拟浏览器请求）
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.wublock123.com",
            "Referer": "https://www.wublock123.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
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
                # 构建 POST 数据（仅获取第一页）
                data = {
                    "pageIndex": 1,
                    "pageSize": self.page_size,
                }
                
                response = requests.post(
                    self.API_BASE_URL,
                    data=data,
                    headers=headers,
                    proxies=proxies,
                    timeout=10
                )
                
                response.raise_for_status()
                data_json = json.loads(response.text)
                
                # 检查 API 响应状态
                # 吴说 API: code: 1 且 success: true 表示成功
                code = data_json.get("code")
                success = data_json.get("success", False)
                
                if code != 1 or not success:
                    error_msg = data_json.get("msg", data_json.get("message", "未知错误"))
                    raise ValueError(f"API 返回错误: {error_msg} (code: {code}, success: {success})")
                
                # 解析数据
                # 响应格式：{"code": 1, "success": true, "data": [...]}
                data_list = data_json.get("data", [])
                
                if not data_list or not isinstance(data_list, list):
                    print(f"[{self.platform_name}] 未获取到数据")
                    return None, self.platform_id, self.platform_name
                
                # 转换为标准格式
                items = []
                for index, item in enumerate(data_list[:self.max_items], 1):
                    title = item.get("title", "")
                    if not title or not str(title).strip():
                        continue
                    
                    # 获取 URL（API 已返回完整 URL）
                    url = item.get("url", "")
                    
                    # 如果 url 为空，尝试从 URL 中提取 id 构造
                    if not url or not str(url).strip():
                        # 尝试从其他字段获取 id（如果有）
                        # 从 URL 格式看：https://www.wublock123.com/index.php?m=content&c=index&a=show&catid=6&id=53004
                        # 如果 URL 为空，可能需要其他方式构造，但根据响应数据，URL 应该总是存在
                        url = ""
                    
                    # 确保 URL 是完整的（根据响应数据，URL 已经是完整 URL）
                    if url and not url.startswith(("http://", "https://")):
                        url = f"https://www.wublock123.com{url}" if url.startswith("/") else url
                    
                    items.append({
                        "title": str(title).strip(),
                        "url": url,
                        "mobileUrl": url,  # 吴说使用相同 URL
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

