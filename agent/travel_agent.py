import json
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage

from config.settings import settings
from .state import AgentState
from .prompts import PARSE_INTENT_PROMPT, GENERATE_RESPONSE_PROMPT, CHAT_PROMPT
from tools.flight import FlightSearchTool
from tools.hotel import HotelSearchTool
from tools.attraction import AttractionTool
from tools.weather import WeatherTool
from tools.map import MapTool


class TravelAgent:
    def __init__(self):
        self._init_llm()

        # 初始化工具
        self.flight_tool = FlightSearchTool()
        self.hotel_tool = HotelSearchTool()
        self.attraction_tool = AttractionTool()
        self.weather_tool = WeatherTool()
        self.map_tool = MapTool()

    def _init_llm(self):
        """根据配置初始化LLM"""
        provider = settings.AI_PROVIDER

        if provider == "siliconflow":
            # 使用硅基流动 (OpenAI兼容接口)
            from langchain_openai import ChatOpenAI

            if not settings.SILICONFLOW_API_KEY:
                raise ValueError("未配置SILICONFLOW_API_KEY")

            self.llm = ChatOpenAI(
                model=settings.SILICONFLOW_MODEL,
                api_key=settings.SILICONFLOW_API_KEY,
                base_url=settings.SILICONFLOW_BASE_URL,
                temperature=0.7
            )
            print(f"[INFO] 使用硅基流动模型: {settings.SILICONFLOW_MODEL}")

        elif provider == "claude":
            # 使用Claude API
            from langchain_anthropic import ChatAnthropic

            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("未配置ANTHROPIC_API_KEY")

            self.llm = ChatAnthropic(
                model=settings.CLAUDE_MODEL,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.7
            )
            print(f"[INFO] 使用Claude模型: {settings.CLAUDE_MODEL}")

        else:
            raise ValueError(f"不支持的AI提供商: {provider}")

        # 初始化工具
        self.flight_tool = FlightSearchTool()
        self.hotel_tool = HotelSearchTool()
        self.attraction_tool = AttractionTool()
        self.weather_tool = WeatherTool()
        self.map_tool = MapTool()

    def chat(self, user_input: str, user_id: str = "default",
             history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        处理用户对话

        Args:
            user_input: 用户输入
            user_id: 用户ID
            history: 对话历史

        Returns:
            包含回复和推荐结果的字典
        """
        try:
            # 构建历史消息
            messages = self._build_history(history or [])

            # 直接使用LLM生成回复
            response = self.llm.invoke(
                CHAT_PROMPT.format_messages(
                    user_info=f"用户ID: {user_id}",
                    history=messages,
                    input=user_input
                )
            )

            return {
                "message": response.content,
                "success": True
            }

        except Exception as e:
            return {
                "message": f"抱歉，处理您的请求时出现了错误: {str(e)}",
                "success": False,
                "error": str(e)
            }

    def plan_trip(self, user_input: str, user_id: str = "default") -> Dict[str, Any]:
        """
        规划旅行行程

        Args:
            user_input: 用户输入
            user_id: 用户ID

        Returns:
            包含行程规划的字典
        """
        try:
            # 1. 解析用户意图
            parsed = self._parse_intent(user_input)

            # 2. 调用API获取数据
            results = self._call_apis(parsed)

            # 3. 生成回复
            response = self._generate_response(results)

            return {
                "message": response,
                "parsed_intent": parsed,
                "query_results": results,
                "success": True
            }

        except Exception as e:
            return {
                "message": f"规划旅行时出现错误: {str(e)}",
                "success": False,
                "error": str(e)
            }

    def _parse_intent(self, user_input: str) -> Dict[str, Any]:
        """解析用户意图"""
        try:
            response = self.llm.invoke(
                PARSE_INTENT_PROMPT.format(user_input=user_input)
            )

            # 清理响应内容，提取JSON
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            return json.loads(content)

        except json.JSONDecodeError:
            # 如果解析失败，返回基本结构
            return {
                "destination": None,
                "origin": None,
                "departure_date": None,
                "return_date": None,
                "duration": None,
                "budget": None,
                "travelers": 1,
                "preferences": [],
                "accommodation_preference": None,
                "transport_preference": None,
                "special_requirements": None
            }

    def _call_apis(self, parsed_intent: Dict[str, Any]) -> Dict[str, Any]:
        """调用各种API获取数据"""
        results = {}

        destination = parsed_intent.get("destination")
        if not destination:
            return results

        # 使用高德地图搜索景点POI
        preferences = parsed_intent.get("preferences", [])
        # 根据偏好选择搜索关键词
        keywords = destination
        if preferences:
            keywords = f"{destination} {' '.join(preferences[:2])}"

        amap_pois = self.map_tool.search_poi(keywords, city=destination)
        results["amap_attractions"] = amap_pois

        # 同时保留原有的景点数据作为补充
        attractions = self.attraction_tool.search(destination, preferences)
        results["attractions"] = attractions

        # 获取目的地坐标
        location = self.map_tool.geocode(destination)
        if location:
            results["destination_location"] = location

        # 搜索天气
        if parsed_intent.get("departure_date"):
            weather = self.weather_tool.get_forecast(
                destination,
                parsed_intent["departure_date"]
            )
            results["weather"] = weather

        # 搜索机票（如果有出发地）
        if parsed_intent.get("origin") and parsed_intent.get("departure_date"):
            flights = self.flight_tool.search(
                parsed_intent["origin"],
                destination,
                parsed_intent["departure_date"]
            )
            results["flights"] = flights

        # 搜索酒店
        if parsed_intent.get("departure_date") and parsed_intent.get("return_date"):
            hotels = self.hotel_tool.search(
                destination,
                parsed_intent["departure_date"],
                parsed_intent.get("return_date"),
                parsed_intent.get("budget")
            )
            results["hotels"] = hotels

        # 如果有出发地，规划路线
        if parsed_intent.get("origin") and location:
            origin_location = self.map_tool.geocode(parsed_intent["origin"])
            if origin_location:
                route = self.map_tool.get_route_driving(
                    origin_location["lng"], origin_location["lat"],
                    location["lng"], location["lat"]
                )
                results["route"] = route

        return results

    def _generate_response(self, results: Dict[str, Any]) -> str:
        """生成最终回复"""
        try:
            response = self.llm.invoke(
                GENERATE_RESPONSE_PROMPT.format(
                    query_results=json.dumps(results, ensure_ascii=False, indent=2)
                )
            )
            return response.content

        except Exception as e:
            return f"生成回复时出现错误: {str(e)}"

    def _build_history(self, history: List[Dict]) -> List:
        """构建对话历史"""
        messages = []
        for msg in history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages


# 全局Agent实例
travel_agent = TravelAgent()
