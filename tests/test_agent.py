"""Agent单元测试"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTravelAgent:
    """旅行Agent测试类"""

    def test_parse_intent_basic(self):
        """测试基本意图解析"""
        from agent.travel_agent import TravelAgent

        agent = TravelAgent()

        # 测试解析逻辑（使用mock数据）
        intent = agent._parse_intent("我想下周去日本玩5天")

        assert isinstance(intent, dict)
        assert "destination" in intent

    def test_chat_response(self):
        """测试对话响应"""
        from agent.travel_agent import TravelAgent

        agent = TravelAgent()

        # 这里需要mock LLM调用
        # result = agent.chat("你好", "test_user")
        # assert result["success"] is True
        pass


class TestTools:
    """工具测试类"""

    def test_flight_search_mock(self):
        """测试机票搜索（模拟数据）"""
        from tools.flight import FlightSearchTool

        tool = FlightSearchTool()
        results = tool.search("PEK", "NRT", "2024-03-01")

        assert isinstance(results, list)
        assert len(results) > 0
        assert "airline" in results[0]
        assert "price" in results[0]

    def test_hotel_search_mock(self):
        """测试酒店搜索（模拟数据）"""
        from tools.hotel import HotelSearchTool

        tool = HotelSearchTool()
        results = tool.search("东京", "2024-03-01", "2024-03-05")

        assert isinstance(results, list)
        assert len(results) > 0
        assert "name" in results[0]
        assert "price_per_night" in results[0]

    def test_attraction_search_mock(self):
        """测试景点搜索（模拟数据）"""
        from tools.attraction import AttractionTool

        tool = AttractionTool()
        results = tool.search("东京", ["动漫", "美食"])

        assert isinstance(results, list)
        assert len(results) > 0
        assert "name" in results[0]
        assert "category" in results[0]

    def test_weather_mock(self):
        """测试天气查询（模拟数据）"""
        from tools.weather import WeatherTool

        tool = WeatherTool()
        result = tool.get_current("东京")

        assert isinstance(result, dict)
        assert "temperature" in result
        assert "description" in result


class TestMemory:
    """记忆系统测试类"""

    def test_save_and_get_preferences(self):
        """测试保存和获取偏好"""
        from memory.user_memory import UserMemory

        memory = UserMemory(":memory:")  # 使用内存数据库

        # 保存偏好
        memory.save_preference("test_user", "home_city", "北京")

        # 获取偏好
        prefs = memory.get_preferences("test_user")

        assert "home_city" in prefs
        assert prefs["home_city"] == "北京"

    def test_save_conversation(self):
        """测试保存对话"""
        from memory.user_memory import UserMemory

        memory = UserMemory(":memory:")

        # 保存对话
        memory.save_conversation(
            "test_user",
            "我想去日本",
            "好的，我来帮您规划日本旅行"
        )

        # 获取历史
        history = memory.get_conversation_history("test_user")

        assert len(history) == 1
        assert history[0]["message"] == "我想去日本"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
