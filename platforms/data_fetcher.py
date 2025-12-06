"""
数据获取器 - 基于平台抽象的数据获取
"""

import random
import time
from typing import Dict, List, Optional, Tuple, Union

from .factory import create_platform
from .base import BasePlatform


class DataFetcherV2:
    """数据获取器 - 通过平台抽象接口获取数据"""
    
    def __init__(self, proxy_url: Optional[str] = None):
        """
        初始化数据获取器
        
        Args:
            proxy_url: 代理URL（会传递给所有平台）
        """
        self.proxy_url = proxy_url
        self._platform_cache: Dict[str, BasePlatform] = {}
    
    def _get_platform(self, platform_config: Union[str, Dict, Tuple]) -> BasePlatform:
        """
        获取平台实例（带缓存）
        
        Args:
            platform_config: 平台配置
        
        Returns:
            平台实例
        """
        # 标准化配置
        if isinstance(platform_config, str):
            platform_config = {"id": platform_config}
        elif isinstance(platform_config, tuple):
            platform_config = {"id": platform_config[0], "name": platform_config[1]}
        
        # 生成缓存键
        cache_key = f"{platform_config.get('id')}_{id(platform_config.get('config', {}))}"
        
        # 从缓存获取或创建
        if cache_key not in self._platform_cache:
            # 如果配置中有 proxy_url，使用配置的；否则使用全局的
            if "config" not in platform_config:
                platform_config["config"] = {}
            if "proxy_url" not in platform_config["config"] and self.proxy_url:
                platform_config["config"]["proxy_url"] = self.proxy_url
            
            platform = create_platform(platform_config)
            self._platform_cache[cache_key] = platform
        
        return self._platform_cache[cache_key]
    
    def fetch_data(
        self,
        platform_config: Union[str, Dict, Tuple[str, str]],
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """
        获取单个平台数据
        
        Args:
            platform_config: 平台配置
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间
            max_retry_wait: 最大重试等待时间
        
        Returns:
            (数据字典, 平台ID, 平台名称)
        """
        platform = self._get_platform(platform_config)
        return platform.fetch_data(
            max_retries=max_retries,
            min_retry_wait=min_retry_wait,
            max_retry_wait=max_retry_wait
        )
    
    def crawl_websites(
        self,
        platforms: List[Union[str, Dict, Tuple[str, str]]],
        request_interval: int = 1000,
    ) -> Tuple[Dict, Dict, List]:
        """
        批量爬取多个平台数据
        
        Args:
            platforms: 平台列表
            request_interval: 请求间隔（毫秒）
        
        Returns:
            (results, id_to_name, failed_ids)
            results 格式:
            {
                "platform_id": {
                    "新闻标题": {
                        "ranks": [1, 3],
                        "url": "...",
                        "mobileUrl": "..."
                    }
                }
            }
        """
        results = {}
        id_to_name = {}
        failed_ids = []
        
        for i, platform_info in enumerate(platforms):
            # 获取平台实例
            platform = self._get_platform(platform_info)
            platform_id = platform.get_platform_id()
            platform_name = platform.get_platform_name()
            id_to_name[platform_id] = platform_name
            
            # 获取数据
            data, _, _ = platform.fetch_data()
            
            if data:
                try:
                    # 转换为统一格式
                    results[platform_id] = {}
                    for item in data.get("items", []):
                        title = item.get("title", "")
                        if not title or not str(title).strip():
                            continue
                        
                        title = str(title).strip()
                        url = item.get("url", "")
                        mobile_url = item.get("mobileUrl", "")
                        rank = item.get("rank", 1)
                        
                        if title in results[platform_id]:
                            results[platform_id][title]["ranks"].append(rank)
                        else:
                            results[platform_id][title] = {
                                "ranks": [rank],
                                "url": url,
                                "mobileUrl": mobile_url,
                            }
                
                except Exception as e:
                    print(f"处理 {platform_name} 数据出错: {e}")
                    failed_ids.append(platform_id)
            else:
                failed_ids.append(platform_id)
            
            # 请求间隔控制
            if i < len(platforms) - 1:
                actual_interval = request_interval + random.randint(-10, 20)
                actual_interval = max(50, actual_interval)
                time.sleep(actual_interval / 1000)
        
        print(f"成功: {list(results.keys())}, 失败: {failed_ids}")
        return results, id_to_name, failed_ids

