from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import requests
import time
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """工具基类"""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1小时缓存

    def _get_cache_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return "|".join(key_parts)

    def _check_cache(self, key: str) -> Optional[Any]:
        """检查缓存"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None

    def _set_cache(self, key: str, data: Any):
        """设置缓存"""
        self.cache[key] = (data, time.time())

    @abstractmethod
    def search(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """搜索接口，子类必须实现"""
        pass

    def _make_request(self, url: str, headers: Dict = None,
                      params: Dict = None) -> Optional[Dict]:
        """发送HTTP请求"""
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API请求失败: url={url}, error={e}")
            return None
