from typing import Dict, Any, List, Optional
import requests
from .base import BaseTool
from config.settings import settings


class MapTool(BaseTool):
    """高德地图工具"""

    def __init__(self):
        super().__init__()
        self.api_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com"

    def search(self, *args, **kwargs):
        """搜索接口（抽象方法实现）"""
        return self.search_poi(*args, **kwargs)

    def geocode(self, address: str, city: str = "") -> Optional[Dict]:
        """
        地理编码：地址转坐标

        Args:
            address: 地址
            city: 城市

        Returns:
            坐标信息
        """
        cache_key = self._get_cache_key("geocode", address, city)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "key": self.api_key,
            "address": address,
            "output": "json"
        }
        if city:
            params["city"] = city

        result = self._make_request(f"{self.base_url}/v3/geocode/geo", params=params)

        if result and result.get("status") == "1" and result.get("geocodes"):
            geocode = result["geocodes"][0]
            location = geocode.get("location", "0,0").split(",")
            data = {
                "address": geocode.get("formatted_address", address),
                "lng": float(location[0]) if len(location) == 2 else 0,
                "lat": float(location[1]) if len(location) == 2 else 0,
                "level": geocode.get("level", ""),
                "adcode": geocode.get("adcode", "")
            }
            self._set_cache(cache_key, data)
            return data

        return None

    def reverse_geocode(self, lng: float, lat: float) -> Optional[Dict]:
        """
        逆地理编码：坐标转地址

        Args:
            lng: 经度
            lat: 纬度

        Returns:
            地址信息
        """
        cache_key = self._get_cache_key("reverse_geocode", lng, lat)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "key": self.api_key,
            "location": f"{lng},{lat}",
            "output": "json"
        }

        result = self._make_request(f"{self.base_url}/v3/geocode/regeo", params=params)

        if result and result.get("status") == "1" and result.get("regeocode"):
            regeocode = result["regeocode"]
            data = {
                "address": regeocode.get("formatted_address", ""),
                "province": regeocode.get("addressComponent", {}).get("province", ""),
                "city": regeocode.get("addressComponent", {}).get("city", ""),
                "district": regeocode.get("addressComponent", {}).get("district", "")
            }
            self._set_cache(cache_key, data)
            return data

        return None

    def search_poi(self, keywords: str, city: str = "", types: str = "") -> List[Dict]:
        """
        POI搜索：搜索地点

        Args:
            keywords: 关键词
            city: 城市
            types: POI类型

        Returns:
            POI列表
        """
        cache_key = self._get_cache_key("poi", keywords, city, types)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "key": self.api_key,
            "keywords": keywords,
            "output": "json"
        }
        if city:
            params["city"] = city
        if types:
            params["types"] = types

        result = self._make_request(f"{self.base_url}/v5/place/text", params=params)

        pois = []
        if result and result.get("status") == "1" and result.get("pois"):
            for poi in result["pois"]:
                location = poi.get("location", "0,0").split(",")
                pois.append({
                    "name": poi.get("name", ""),
                    "address": poi.get("address", ""),
                    "type": poi.get("type", ""),
                    "lng": float(location[0]) if len(location) == 2 else 0,
                    "lat": float(location[1]) if len(location) == 2 else 0,
                    "tel": poi.get("tel", ""),
                    "distance": poi.get("distance", ""),
                    "rating": poi.get("biz_ext", {}).get("rating", "")
                })

        self._set_cache(cache_key, pois)
        return pois

    def get_route_driving(self, origin_lng: float, origin_lat: float,
                          dest_lng: float, dest_lat: float) -> Optional[Dict]:
        """
        驾车路线规划

        Args:
            origin_lng: 起点经度
            origin_lat: 起点纬度
            dest_lng: 终点经度
            dest_lat: 终点纬度

        Returns:
            路线信息
        """
        cache_key = self._get_cache_key("route_driving", origin_lng, origin_lat, dest_lng, dest_lat)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "key": self.api_key,
            "origin": f"{origin_lng},{origin_lat}",
            "destination": f"{dest_lng},{dest_lat}",
            "output": "json"
        }

        result = self._make_request(f"{self.base_url}/v3/direction/driving", params=params)

        if result and result.get("status") == "1" and result.get("route"):
            route = result["route"]
            paths = route.get("paths", [])
            if paths:
                path = paths[0]
                data = {
                    "distance": route.get("distance", "0"),
                    "duration": route.get("duration", "0"),
                    "toll": route.get("tolls", "0"),
                    "toll_distance": route.get("toll_distance", "0"),
                    "steps": self._parse_driving_steps(path.get("steps", []))
                }
                self._set_cache(cache_key, data)
                return data

        return None

    def get_route_transit(self, origin_lng: float, origin_lat: float,
                          dest_lng: float, dest_lat: float, city: str) -> Optional[Dict]:
        """
        公交路线规划

        Args:
            origin_lng: 起点经度
            origin_lat: 起点纬度
            dest_lng: 终点经度
            dest_lat: 终点纬度
            city: 城市

        Returns:
            路线信息
        """
        cache_key = self._get_cache_key("route_transit", origin_lng, origin_lat, dest_lng, dest_lat, city)
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "key": self.api_key,
            "origin": f"{origin_lng},{origin_lat}",
            "destination": f"{dest_lng},{dest_lat}",
            "city": city,
            "output": "json"
        }

        result = self._make_request(f"{self.base_url}/v3/direction/transit/integrated", params=params)

        if result and result.get("status") == "1" and result.get("route"):
            route = result["route"]
            data = {
                "distance": route.get("distance", "0"),
                "duration": route.get("duration", "0"),
                "transits": self._parse_transit(route.get("transits", []))
            }
            self._set_cache(cache_key, data)
            return data

        return None

    def _parse_driving_steps(self, steps: List[Dict]) -> List[Dict]:
        """解析驾车步骤"""
        result = []
        for step in steps:
            result.append({
                "instruction": step.get("instruction", ""),
                "road": step.get("road", ""),
                "distance": step.get("distance", ""),
                "duration": step.get("duration", "")
            })
        return result

    def _parse_transit(self, transits: List[Dict]) -> List[Dict]:
        """解析公交方案"""
        result = []
        for transit in transits[:3]:  # 最多返回3个方案
            segments = transit.get("segments", [])
            route_parts = []
            for segment in segments:
                bus = segment.get("bus", {})
                if bus and bus.get("buslines"):
                    for busline in bus["buslines"]:
                        route_parts.append({
                            "type": "bus",
                            "name": busline.get("name", ""),
                            "departure_stop": busline.get("departure_stop", {}).get("name", ""),
                            "arrival_stop": busline.get("arrival_stop", {}).get("name", ""),
                            "distance": busline.get("distance", ""),
                            "duration": busline.get("duration", "")
                        })
                walking = segment.get("walking", {})
                if walking and walking.get("steps"):
                    route_parts.append({
                        "type": "walking",
                        "distance": walking.get("distance", ""),
                        "duration": walking.get("duration", "")
                    })

            result.append({
                "duration": transit.get("duration", ""),
                "walking_distance": transit.get("walking_distance", ""),
                "cost": transit.get("cost", ""),
                "parts": route_parts
            })

        return result

    def format_route(self, route: Dict, route_type: str = "driving") -> str:
        """格式化路线"""
        text = "## 路线规划\n\n"

        if route_type == "driving":
            text += f"**距离:** {route.get('distance', 'N/A')}\n"
            text += f"**预计时间:** {route.get('duration', 'N/A')}\n"
            text += f"**高速费用:** ¥{route.get('toll', '0')}\n\n"

            text += "**行驶步骤:**\n"
            for idx, step in enumerate(route.get('steps', [])[:5], 1):
                text += f"{idx}. {step.get('instruction', '')}\n"

        elif route_type == "transit":
            text += f"**总距离:** {route.get('distance', 'N/A')}\n"
            text += f"**预计时间:** {route.get('duration', 'N/A')}\n\n"

            for idx, transit in enumerate(route.get('transits', []), 1):
                text += f"**方案{idx}:** {transit.get('duration', 'N/A')} "
                text += f"(步行{transit.get('walking_distance', 'N/A')}, "
                text += f"费用¥{transit.get('cost', '0')})\n"

                for part in transit.get('parts', []):
                    if part.get('type') == 'bus':
                        text += f"  🚌 {part.get('name', '')}: "
                        text += f"{part.get('departure_stop', '')} → {part.get('arrival_stop', '')}\n"
                    elif part.get('type') == 'walking':
                        text += f"  🚶 步行: {part.get('distance', '')}\n"
                text += "\n"

        return text
