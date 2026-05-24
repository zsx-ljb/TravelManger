from typing import Dict, Any, List, Optional
from .base import BaseTool


class AttractionTool(BaseTool):
    """景点搜索工具"""

    def __init__(self):
        super().__init__()

    def search(self, city: str, interests: List[str] = None,
               max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索景点

        Args:
            city: 城市名称
            interests: 兴趣偏好列表
            max_results: 最大返回数量

        Returns:
            景点信息列表
        """
        cache_key = self._get_cache_key(city, tuple(interests or []))
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        # TODO: 集成TripAdvisor API
        results = self._get_mock_data(city, interests)

        self._set_cache(cache_key, results)
        return results[:max_results]

    def _get_mock_data(self, city: str, interests: List[str] = None) -> List[Dict]:
        """模拟数据"""
        attractions = {
            "东京": [
                {
                    "id": "AT001",
                    "name": "浅草寺",
                    "category": "历史古迹",
                    "description": "东京最古老的寺庙，可以体验日本传统文化",
                    "address": "东京都台东区浅草2-3-1",
                    "rating": 4.6,
                    "reviews": 8500,
                    "ticket_price": 0,
                    "duration": "1-2小时",
                    "best_time": "上午"
                },
                {
                    "id": "AT002",
                    "name": "秋叶原",
                    "category": "购物娱乐",
                    "description": "动漫迷的圣地，电子产品和二次元文化的中心",
                    "address": "东京都千代田区外神田",
                    "rating": 4.5,
                    "reviews": 12000,
                    "ticket_price": 0,
                    "duration": "3-4小时",
                    "best_time": "下午"
                },
                {
                    "id": "AT003",
                    "name": "东京塔",
                    "category": "地标建筑",
                    "description": "东京的标志性建筑，可以俯瞰整个城市",
                    "address": "东京都港区芝公园4-2-8",
                    "rating": 4.4,
                    "reviews": 6500,
                    "ticket_price": 300,
                    "duration": "1-2小时",
                    "best_time": "傍晚"
                },
                {
                    "id": "AT004",
                    "name": "筑地市场",
                    "category": "美食",
                    "description": "品尝最新鲜的寿司和海鲜",
                    "address": "东京都中央区筑地4-16-2",
                    "rating": 4.7,
                    "reviews": 9800,
                    "ticket_price": 0,
                    "duration": "2-3小时",
                    "best_time": "上午"
                },
                {
                    "id": "AT005",
                    "name": "涩谷十字路口",
                    "category": "地标建筑",
                    "description": "世界上最繁忙的十字路口，感受东京的活力",
                    "address": "东京都涩谷区道玄坂",
                    "rating": 4.3,
                    "reviews": 5200,
                    "ticket_price": 0,
                    "duration": "30分钟",
                    "best_time": "傍晚"
                }
            ],
            "大阪": [
                {
                    "id": "AT101",
                    "name": "大阪城",
                    "category": "历史古迹",
                    "description": "大阪的标志性建筑，日本三大名城之一",
                    "address": "大阪市中央区大阪城1-1",
                    "rating": 4.5,
                    "reviews": 7200,
                    "ticket_price": 600,
                    "duration": "2-3小时",
                    "best_time": "上午"
                },
                {
                    "id": "AT102",
                    "name": "道顿堀",
                    "category": "美食购物",
                    "description": "大阪最热闹的美食街，品尝大阪烧和章鱼烧",
                    "address": "大阪市中央区道顿堀",
                    "rating": 4.6,
                    "reviews": 15000,
                    "ticket_price": 0,
                    "duration": "2-3小时",
                    "best_time": "晚上"
                }
            ]
        }

        city_attractions = attractions.get(city, [
            {
                "id": "AT999",
                "name": f"{city}市中心",
                "category": "城市观光",
                "description": f"探索{city}的特色",
                "address": f"{city}中心区域",
                "rating": 4.0,
                "reviews": 1000,
                "ticket_price": 0,
                "duration": "半天",
                "best_time": "全天"
            }
        ])

        # 根据兴趣过滤（简化实现）
        if interests:
            # 这里可以添加更智能的过滤逻辑
            pass

        return city_attractions

    def format_results(self, attractions: List[Dict]) -> str:
        """格式化景点结果"""
        if not attractions:
            return "未找到相关景点"

        text = "## 景点推荐\n\n"
        for attr in attractions:
            price = "免费" if attr["ticket_price"] == 0 else f"¥{attr['ticket_price']}"
            text += f"**{attr['name']}** ({attr['category']})\n"
            text += f"- 介绍: {attr['description']}\n"
            text += f"- 地址: {attr['address']}\n"
            text += f"- 评分: {attr['rating']}/5 ({attr['reviews']}条评价)\n"
            text += f"- 门票: {price}\n"
            text += f"- 建议时长: {attr['duration']}\n"
            text += f"- 最佳时间: {attr['best_time']}\n\n"

        return text
