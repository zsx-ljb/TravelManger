from typing import Dict, Any, List, Optional
from .base import BaseTool


class HotelSearchTool(BaseTool):
    """酒店搜索工具"""

    def __init__(self):
        super().__init__()
        self.api_key = None

    def search(self, location: str, check_in: str, check_out: str,
               budget: Optional[float] = None,
               max_results: int = 5) -> List[Dict[str, Any]]:
        """
        搜索酒店

        Args:
            location: 目的地
            check_in: 入住日期
            check_out: 退房日期
            budget: 预算范围
            max_results: 最大返回数量

        Returns:
            酒店信息列表
        """
        cache_key = self._get_cache_key(location, check_in, check_out, budget)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        # TODO: 集成Booking API
        results = self._get_mock_data(location, check_in, check_out, budget)

        self._set_cache(cache_key, results)
        return results[:max_results]

    def _get_mock_data(self, location: str, check_in: str,
                       check_out: str, budget: Optional[float]) -> List[Dict]:
        """模拟数据"""
        hotels = [
            {
                "id": "HT001",
                "name": f"{location}大酒店",
                "star": 5,
                "address": f"{location}市中心",
                "check_in": check_in,
                "check_out": check_out,
                "price_per_night": 800,
                "total_price": 1600,
                "currency": "CNY",
                "rating": 4.8,
                "reviews": 1250,
                "amenities": ["WiFi", "早餐", "健身房", "游泳池"],
                "room_type": "豪华大床房"
            },
            {
                "id": "HT002",
                "name": f"{location}商务酒店",
                "star": 4,
                "address": f"{location}商业区",
                "check_in": check_in,
                "check_out": check_out,
                "price_per_night": 450,
                "total_price": 900,
                "currency": "CNY",
                "rating": 4.5,
                "reviews": 890,
                "amenities": ["WiFi", "早餐"],
                "room_type": "标准双床房"
            },
            {
                "id": "HT003",
                "name": f"{location}民宿",
                "star": 3,
                "address": f"{location}老城区",
                "check_in": check_in,
                "check_out": check_out,
                "price_per_night": 280,
                "total_price": 560,
                "currency": "CNY",
                "rating": 4.6,
                "reviews": 320,
                "amenities": ["WiFi"],
                "room_type": "特色民宿"
            }
        ]

        # 根据预算过滤
        if budget:
            hotels = [h for h in hotels if h["total_price"] <= budget * 0.4]

        return hotels

    def format_results(self, hotels: List[Dict]) -> str:
        """格式化酒店结果"""
        if not hotels:
            return "未找到符合条件的酒店"

        text = "## 酒店推荐\n\n"
        for hotel in hotels:
            stars = "⭐" * hotel["star"]
            text += f"**{hotel['name']}** {stars}\n"
            text += f"- 地址: {hotel['address']}\n"
            text += f"- 房型: {hotel['room_type']}\n"
            text += f"- 评分: {hotel['rating']}/5 ({hotel['reviews']}条评价)\n"
            text += f"- 价格: ¥{hotel['price_per_night']}/晚\n"
            text += f"- 总价: ¥{hotel['total_price']} ({hotel['check_in']} 至 {hotel['check_out']})\n"
            text += f"- 设施: {', '.join(hotel['amenities'])}\n\n"

        return text
