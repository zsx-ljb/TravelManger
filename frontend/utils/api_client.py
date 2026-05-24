import requests
from typing import Dict, List, Optional


class TravelAgentAPI:
    """后端API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def chat(self, message: str, user_id: str = "default",
             session_id: str = "default", history: List[Dict] = None) -> Dict:
        """发送消息给Agent"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "message": message,
                "user_id": user_id,
                "session_id": session_id,
                "history": history or []
            }
        )
        response.raise_for_status()
        return response.json()

    def plan_trip(self, user_input: str, user_id: str = "default") -> Dict:
        """规划旅行"""
        response = requests.post(
            f"{self.base_url}/api/plan",
            json={
                "user_input": user_input,
                "user_id": user_id
            }
        )
        response.raise_for_status()
        return response.json()

    def get_travel_plans(self, user_id: str, limit: int = 10) -> List[Dict]:
        """获取用户历史规划"""
        response = requests.get(
            f"{self.base_url}/api/plans",
            params={"user_id": user_id, "limit": limit}
        )
        response.raise_for_status()
        return response.json()["plans"]

    def get_user_preferences(self, user_id: str) -> Dict:
        """获取用户偏好"""
        response = requests.get(
            f"{self.base_url}/api/user/preferences",
            params={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()["preferences"]

    def update_user_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """更新用户偏好"""
        response = requests.put(
            f"{self.base_url}/api/user/preferences",
            json={
                "user_id": user_id,
                "preferences": preferences
            }
        )
        response.raise_for_status()
        return response.json()

    def get_favorites(self, user_id: str, item_type: Optional[str] = None) -> List[Dict]:
        """获取收藏"""
        params = {"user_id": user_id}
        if item_type:
            params["item_type"] = item_type

        response = requests.get(
            f"{self.base_url}/api/favorites",
            params=params
        )
        response.raise_for_status()
        return response.json()["favorites"]

    def add_favorite(self, user_id: str, item_type: str,
                     item_id: str, item_data: Dict) -> bool:
        """添加收藏"""
        response = requests.post(
            f"{self.base_url}/api/favorites",
            json={
                "user_id": user_id,
                "item_type": item_type,
                "item_id": item_id,
                "item_data": item_data
            }
        )
        response.raise_for_status()
        return response.json()["success"]

    def delete_favorite(self, user_id: str, item_type: str, item_id: str) -> bool:
        """删除收藏"""
        response = requests.delete(
            f"{self.base_url}/api/favorites",
            params={
                "user_id": user_id,
                "item_type": item_type,
                "item_id": item_id
            }
        )
        response.raise_for_status()
        return response.json()["success"]

    def get_history(self, user_id: str, session_id: str = None, limit: int = 20) -> List[Dict]:
        """获取对话历史"""
        params = {"user_id": user_id, "limit": limit}
        if session_id:
            params["session_id"] = session_id
        response = requests.get(
            f"{self.base_url}/api/history",
            params=params
        )
        response.raise_for_status()
        return response.json()["history"]
