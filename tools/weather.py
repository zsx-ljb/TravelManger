from typing import Dict, Any, List, Optional
from .base import BaseTool


class WeatherTool(BaseTool):
    """天气查询工具"""

    def __init__(self):
        super().__init__()
        self.api_key = None

    def search(self, *args, **kwargs):
        """搜索接口（抽象方法实现）"""
        return self.get_forecast(*args, **kwargs)

    def get_current(self, city: str) -> Dict[str, Any]:
        """
        获取当前天气

        Args:
            city: 城市名称

        Returns:
            天气信息
        """
        cache_key = self._get_cache_key("current", city)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        # TODO: 集成OpenWeatherMap API
        result = self._get_mock_current(city)

        self._set_cache(cache_key, result)
        return result

    def get_forecast(self, city: str, date: str) -> Dict[str, Any]:
        """
        获取天气预报

        Args:
            city: 城市名称
            date: 日期

        Returns:
            天气预报信息
        """
        cache_key = self._get_cache_key("forecast", city, date)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        # TODO: 集成OpenWeatherMap API
        result = self._get_mock_forecast(city, date)

        self._set_cache(cache_key, result)
        return result

    def _get_mock_current(self, city: str) -> Dict:
        """模拟当前天气数据"""
        return {
            "city": city,
            "temperature": 22,
            "feels_like": 20,
            "humidity": 65,
            "description": "晴朗",
            "icon": "01d",
            "wind_speed": 3.5,
            "wind_direction": "东南风"
        }

    def _get_mock_forecast(self, city: str, date: str) -> Dict:
        """模拟天气预报数据"""
        return {
            "city": city,
            "date": date,
            "temp_max": 25,
            "temp_min": 18,
            "humidity": 60,
            "description": "多云转晴",
            "icon": "02d",
            "precipitation": 10,
            "wind_speed": 4.0,
            "sunrise": "06:30",
            "sunset": "18:45",
            "uv_index": 6
        }

    def format_current(self, weather: Dict) -> str:
        """格式化当前天气"""
        text = f"## 当前天气 - {weather['city']}\n\n"
        text += f"- **天气**: {weather['description']}\n"
        text += f"- **温度**: {weather['temperature']}°C (体感 {weather['feels_like']}°C)\n"
        text += f"- **湿度**: {weather['humidity']}%\n"
        text += f"- **风速**: {weather['wind_speed']}m/s {weather['wind_direction']}\n"

        return text

    def format_forecast(self, weather: Dict) -> str:
        """格式化天气预报"""
        text = f"## 天气预报 - {weather['city']} ({weather['date']})\n\n"
        text += f"- **天气**: {weather['description']}\n"
        text += f"- **温度**: {weather['temp_min']}°C ~ {weather['temp_max']}°C\n"
        text += f"- **湿度**: {weather['humidity']}%\n"
        text += f"- **降水概率**: {weather['precipitation']}%\n"
        text += f"- **日出/日落**: {weather['sunrise']} / {weather['sunset']}\n"
        text += f"- **紫外线指数**: {weather['uv_index']}\n"

        return text
