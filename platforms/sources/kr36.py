"""
36氪平台实现
从 https://www.36kr.com/newsflashes 爬取 HTML 并解析 window.initialState 获取数据
"""

import json
import random
import re
import time
from typing import Dict, Optional, Tuple

import requests

from ..base import BasePlatform


class Kr36Platform(BasePlatform):
    """36氪 - 从 36氪快讯页面爬取数据"""
    
    # 页面 URL
    PAGE_URL = "https://www.36kr.com/newsflashes"
    
    def __init__(
        self,
        platform_id: str,
        platform_name: str = None,
        proxy_url: Optional[str] = None,
        max_items: int = 20,
        **kwargs
    ):
        """
        初始化 36氪平台
        
        Args:
            platform_id: 平台ID
            platform_name: 平台名称，默认 "36氪"
            proxy_url: 代理URL（可选）
            max_items: 最大获取条目数，默认 20
        """
        super().__init__(
            platform_id,
            platform_name or "36氪",
            proxy_url,
            **kwargs
        )
        self.max_items = max_items
    
    def _extract_initial_state(self, html: str) -> Optional[Dict]:
        """
        从 HTML 中提取 window.initialState 的 JSON 数据
        
        Args:
            html: HTML 内容
            
        Returns:
            JSON 对象，如果提取失败返回 None
        """
        try:
            # 查找 window.initialState 的位置
            pattern = r'window\.initialState\s*=\s*'
            match = re.search(pattern, html)
            
            if not match:
                print(f"[{self.platform_name}] 未找到 window.initialState")
                return None
            
            # 从匹配位置开始提取 JSON
            start_pos = match.end()
            
            # 使用栈来匹配大括号，处理嵌套结构
            brace_count = 0
            in_string = False
            escape_next = False
            json_start = start_pos
            
            for i in range(start_pos, len(html)):
                char = html[i]
                
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '{':
                        if brace_count == 0:
                            json_start = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # 找到了完整的 JSON 对象
                            json_str = html[json_start:i+1]
                            try:
                                data = json.loads(json_str)
                                return data
                            except json.JSONDecodeError:
                                # 如果解析失败，可能后面还有分号或其他字符
                                # 尝试继续查找
                                pass
                    elif char == ';' and brace_count == 0:
                        # 如果遇到分号且大括号已匹配，说明 JSON 已结束
                        break
            
            # 如果上面的方法失败，尝试简单的正则匹配
            pattern = r'window\.initialState\s*=\s*({.+?});'
            match = re.search(pattern, html, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                try:
                    data = json.loads(json_str)
                    return data
                except json.JSONDecodeError:
                    pass
            
            print(f"[{self.platform_name}] 无法解析 window.initialState 的 JSON 数据")
            return None
                
        except json.JSONDecodeError as e:
            print(f"[{self.platform_name}] JSON 解析失败: {e}")
            return None
        except Exception as e:
            print(f"[{self.platform_name}] 提取 initialState 失败: {e}")
            return None
    
    def _parse_news_data(self, initial_state: Dict) -> list:
        """
        从 initialState 中解析新闻数据
        
        Args:
            initial_state: window.initialState 的 JSON 对象
            
        Returns:
            新闻列表
        """
        news_list = []
        
        try:
            # 36氪的数据结构：newsflashCatalogData.data.newsflashList.data.itemList
            if "newsflashCatalogData" in initial_state:
                newsflash_catalog = initial_state["newsflashCatalogData"]
                if isinstance(newsflash_catalog, dict) and "data" in newsflash_catalog:
                    catalog_data = newsflash_catalog["data"]
                    if isinstance(catalog_data, dict) and "newsflashList" in catalog_data:
                        newsflash_list = catalog_data["newsflashList"]
                        if isinstance(newsflash_list, dict) and "data" in newsflash_list:
                            list_data = newsflash_list["data"]
                            if isinstance(list_data, dict) and "itemList" in list_data:
                                news_list = list_data["itemList"]
                                if isinstance(news_list, list):
                                    return news_list
            
            # 如果上面的路径失败，尝试其他可能的路径（向后兼容）
            if not news_list:
                # 方法1: 直接查找 newsflashList
                if "newsflashList" in initial_state:
                    newsflash_data = initial_state["newsflashList"]
                    if isinstance(newsflash_data, dict):
                        if "newsflashList" in newsflash_data:
                            items = newsflash_data["newsflashList"]
                            if isinstance(items, list):
                                news_list = items
                            elif isinstance(items, dict) and "items" in items:
                                news_list = items["items"]
                        elif "items" in newsflash_data:
                            news_list = newsflash_data["items"]
                        elif "data" in newsflash_data and isinstance(newsflash_data["data"], dict):
                            if "itemList" in newsflash_data["data"]:
                                news_list = newsflash_data["data"]["itemList"]
                    elif isinstance(newsflash_data, list):
                        news_list = newsflash_data
                
                # 方法2: 查找 data 字段
                if not news_list and "data" in initial_state:
                    data = initial_state["data"]
                    if isinstance(data, dict):
                        if "itemList" in data:
                            news_list = data["itemList"]
                        elif "items" in data:
                            news_list = data["items"]
                        elif "list" in data:
                            news_list = data["list"]
                        elif "newsflashList" in data:
                            newsflash_data = data["newsflashList"]
                            if isinstance(newsflash_data, list):
                                news_list = newsflash_data
                            elif isinstance(newsflash_data, dict):
                                if "data" in newsflash_data and isinstance(newsflash_data["data"], dict):
                                    if "itemList" in newsflash_data["data"]:
                                        news_list = newsflash_data["data"]["itemList"]
                                elif "items" in newsflash_data:
                                    news_list = newsflash_data["items"]
            
        except Exception as e:
            print(f"[{self.platform_name}] 解析新闻数据失败: {e}")
        
        return news_list if isinstance(news_list, list) else []
    
    def fetch_data(
        self,
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """
        获取 36氪快讯数据
        
        Args:
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间（秒）
            max_retry_wait: 最大重试等待时间（秒）
        
        Returns:
            (数据字典, 平台ID, 平台名称)
        """
        # 构建请求头（模拟浏览器请求）
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "connection": "keep-alive",
            "referer": "https://www.36kr.com/",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        }
        
        proxies = None
        if self.proxy_url:
            proxies = {"http": self.proxy_url, "https": self.proxy_url}
        
        retries = 0
        
        # 重试逻辑
        while retries <= max_retries:
            try:
                response = requests.get(
                    self.PAGE_URL,
                    headers=headers,
                    proxies=proxies,
                    timeout=15
                )
                
                response.raise_for_status()
                html = response.text
                
                # 提取 window.initialState
                initial_state = self._extract_initial_state(html)
                if not initial_state:
                    raise ValueError("无法从 HTML 中提取 window.initialState")
                
                # 解析新闻数据
                news_list = self._parse_news_data(initial_state)
                
                if not news_list:
                    print(f"[{self.platform_name}] 未获取到新闻数据")
                    # 打印数据结构以便调试
                    print(f"[{self.platform_name}] initialState 的键: {list(initial_state.keys())[:10]}")
                    return None, self.platform_id, self.platform_name
                
                # 转换为标准格式
                items = []
                for index, item in enumerate(news_list[:self.max_items], 1):
                    # 36氪的数据结构：item.templateMaterial.widgetTitle
                    title = ""
                    template_material = item.get("templateMaterial", {})
                    if isinstance(template_material, dict):
                        title = (
                            template_material.get("widgetTitle", "") or
                            template_material.get("title", "") or
                            ""
                        )
                    
                    # 如果 templateMaterial 中没有标题，尝试直接从 item 获取
                    if not title:
                        title = (
                            item.get("title", "") or
                            item.get("name", "") or
                            item.get("newsflashTitle", "") or
                            item.get("headline", "") or
                            ""
                        )
                    
                    if not title or not str(title).strip():
                        continue
                    
                    # 使用 itemId 构造 URL：https://www.36kr.com/newsflashes/${itemId}
                    item_id = item.get("itemId")
                    if item_id:
                        url = f"https://www.36kr.com/newsflashes/{item_id}"
                    else:
                        # 如果没有 itemId，尝试其他 ID 字段
                        item_id = (
                            item.get("id") or
                            item.get("newsflashId") or
                            ""
                        )
                        if item_id:
                            url = f"https://www.36kr.com/newsflashes/{item_id}"
                        else:
                            # 最后尝试从 route 中提取 ID
                            route = item.get("route", "")
                            if route and "itemId=" in route:
                                try:
                                    route_id = route.split("itemId=")[1].split("&")[0]
                                    url = f"https://www.36kr.com/newsflashes/{route_id}"
                                except:
                                    url = ""
                            else:
                                url = ""
                    
                    items.append({
                        "title": str(title).strip(),
                        "url": url,
                        "mobileUrl": url,  # 36氪使用相同 URL
                        "rank": index
                    })
                
                print(f"[{self.platform_name}] 获取成功，共 {len(items)} 条")
                return {"items": items}, self.platform_id, self.platform_name
                
            except requests.exceptions.ConnectionError as e:
                retries += 1
                error_msg = str(e)
                if "Connection refused" in error_msg or "Failed to establish" in error_msg:
                    proxy_hint = f"（提示：当前代理设置: {'已启用' if self.proxy_url else '未启用'}）"
                    error_msg = f"连接被拒绝，无法访问36氪服务器{proxy_hint}"
                
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
