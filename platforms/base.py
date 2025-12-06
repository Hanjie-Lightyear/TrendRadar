"""
平台基类 - 所有平台必须实现此接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class BasePlatform(ABC):
    """平台基类 - 每个平台作为独立实体"""
    
    def __init__(
        self,
        platform_id: str,
        platform_name: str = None,
        proxy_url: Optional[str] = None,
        **kwargs
    ):
        """
        初始化平台
        
        Args:
            platform_id: 平台唯一标识
            platform_name: 平台显示名称
            proxy_url: 代理URL（可选）
            **kwargs: 平台特定配置
        """
        self.platform_id = platform_id
        self.platform_name = platform_name or platform_id
        self.proxy_url = proxy_url
        self.config = kwargs
    
    @abstractmethod
    def fetch_data(
        self,
        max_retries: int = 2,
        min_retry_wait: int = 3,
        max_retry_wait: int = 5,
    ) -> Tuple[Optional[Dict], str, str]:
        """
        获取平台数据
        
        Args:
            max_retries: 最大重试次数
            min_retry_wait: 最小重试等待时间（秒）
            max_retry_wait: 最大重试等待时间（秒）
        
        Returns:
            (数据字典, 平台ID, 平台名称)
            数据字典格式:
            {
                "items": [
                    {
                        "title": "新闻标题",
                        "url": "链接",
                        "mobileUrl": "移动端链接",
                        "rank": 排名
                    }
                ]
            }
            失败时返回 (None, 平台ID, 平台名称)
        """
        pass
    
    def get_proxy_url(self) -> Optional[str]:
        """获取代理URL"""
        return self.proxy_url
    
    def get_platform_id(self) -> str:
        """获取平台ID"""
        return self.platform_id
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return self.platform_name
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.platform_id}, name={self.platform_name})>"

