from typing import Dict, Any, List, Optional
from .base import BaseTool


class FlightSearchTool(BaseTool):
    """机票搜索工具"""

    def __init__(self):
        super().__init__()
        self.api_key = None
        self.api_secret = None

    def search(self, *args, **kwargs):
        """搜索接口（抽象方法实现）"""
        return self._search_flights(*args, **kwargs)

    def _search_flights(self, origin: str, destination: str, date: str,
               adults: int = 1, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        搜索机票

        Args:
            origin: 出发城市代码（如 PEK）
            destination: 目的城市代码（如 NRT）
            date: 出发日期（YYYY-MM-DD）
            adults: 成人数量
            max_results: 最大返回数量

        Returns:
            航班信息列表
        """
        cache_key = self._get_cache_key(origin, destination, date, adults)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        # TODO: 集成Amadeus API
        # 这里返回模拟数据用于开发测试
        results = self._get_mock_data(origin, destination, date)

        self._set_cache(cache_key, results)
        return results[:max_results]

    def _get_mock_data(self, origin: str, destination: str, date: str) -> List[Dict]:
        """模拟数据（开发测试用）"""
        return [
            {
                "id": "FL001",
                "airline": "中国国航",
                "flight_number": "CA927",
                "origin": origin,
                "destination": destination,
                "departure_time": f"{date}T08:30:00",
                "arrival_time": f"{date}T12:45:00",
                "duration": "4小时15分",
                "price": 3500,
                "currency": "CNY",
                "class": "经济舱",
                "stops": 0
            },
            {
                "id": "FL002",
                "airline": "全日空",
                "flight_number": "NH964",
                "origin": origin,
                "destination": destination,
                "departure_time": f"{date}T10:15:00",
                "arrival_time": f"{date}T14:30:00",
                "duration": "4小时15分",
                "price": 4200,
                "currency": "CNY",
                "class": "经济舱",
                "stops": 0
            },
            {
                "id": "FL003",
                "airline": "春秋航空",
                "flight_number": "9C8589",
                "origin": origin,
                "destination": destination,
                "departure_time": f"{date}T06:00:00",
                "arrival_time": f"{date}T10:20:00",
                "duration": "4小时20分",
                "price": 1800,
                "currency": "CNY",
                "class": "经济舱",
                "stops": 0
            }
        ]

    def format_results(self, flights: List[Dict]) -> str:
        """格式化航班结果为可读文本"""
        if not flights:
            return "未找到符合条件的航班"

        text = "## 机票信息\n\n"
        for flight in flights:
            text += f"**{flight['airline']} {flight['flight_number']}**\n"
            text += f"- 时间: {flight['departure_time']} - {flight['arrival_time']}\n"
            text += f"- 飞行时长: {flight['duration']}\n"
            text += f"- 价格: ¥{flight['price']}\n"
            text += f"- 舱位: {flight['class']}\n"
            stops = flight['stops']
            stops_text = '是' if stops == 0 else f'{stops}次转机'
            text += f"- 直飞: {stops_text}\n\n"

        return text
