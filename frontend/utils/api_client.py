import requests
import json
from typing import Dict, List, Optional, Generator

try:
    import streamlit as st
    _has_st = True
except ImportError:
    _has_st = False


class TravelAgentAPI:
    """后端API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None

    def set_token(self, token: str):
        self.token = token

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        token = self.token
        if not token and _has_st:
            token = st.session_state.get("jwt_token")
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    def chat(self, message: str, user_id: str = "default",
             session_id: str = "default", history: List[Dict] = None) -> Dict:
        """发送消息给Agent"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "message": message,
                "session_id": session_id,
                "history": history or []
            },
            headers=self._headers()
        )
        if response.status_code == 401:
            return {"success": False, "error": "login_expired"}
        response.raise_for_status()
        return response.json()

    def chat_stream(self, message: str, user_id: str = "default",
                    session_id: str = "default", history: List[Dict] = None) -> Generator[str, None, None]:
        """流式发送消息给Agent"""
        response = requests.post(
            f"{self.base_url}/api/chat/stream",
            json={
                "message": message,
                "session_id": session_id,
                "history": history or []
            },
            headers=self._headers(),
            stream=True
        )
        if response.status_code == 401:
            raise Exception("登录已过期，请重新登录")
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if data.get('done'):
                        break
                    if 'content' in data and data['content']:
                        yield data['content']
                    if 'error' in data:
                        raise Exception(data['error'])

    def plan_trip(self, user_input: str, user_id: str = "default") -> Dict:
        """规划旅行"""
        response = requests.post(
            f"{self.base_url}/api/plan",
            json={"user_input": user_input},
            headers=self._headers()
        )
        if response.status_code == 401:
            return {"success": False, "error": "login_expired"}
        response.raise_for_status()
        return response.json()

    def get_travel_plans(self, user_id: str = None, limit: int = 10) -> List[Dict]:
        """获取用户历史规划"""
        response = requests.get(
            f"{self.base_url}/api/plans",
            params={"limit": limit},
            headers=self._headers()
        )
        if response.status_code == 401:
            return []
        response.raise_for_status()
        return response.json()["plans"]

    def get_user_preferences(self, user_id: str = None) -> Dict:
        """获取用户偏好"""
        response = requests.get(
            f"{self.base_url}/api/user/preferences",
            headers=self._headers()
        )
        if response.status_code == 401:
            return {}
        response.raise_for_status()
        return response.json()["preferences"]

    def update_user_preferences(self, preferences: Dict = None) -> Dict:
        """更新用户偏好"""
        response = requests.put(
            f"{self.base_url}/api/user/preferences",
            json={"user_id": "placeholder", "preferences": preferences or {}},
            headers=self._headers()
        )
        if response.status_code == 401:
            return {"success": False, "error": "login_expired"}
        response.raise_for_status()
        return response.json()

    def get_favorites(self, user_id: str = None, item_type: Optional[str] = None) -> List[Dict]:
        """获取收藏"""
        params = {}
        if item_type:
            params["item_type"] = item_type

        response = requests.get(
            f"{self.base_url}/api/favorites",
            params=params,
            headers=self._headers()
        )
        if response.status_code == 401:
            return []
        response.raise_for_status()
        return response.json()["favorites"]

    def add_favorite(self, user_id: str = None, item_type: str = None,
                     item_id: str = None, item_data: Dict = None) -> bool:
        """添加收藏"""
        response = requests.post(
            f"{self.base_url}/api/favorites",
            json={
                "user_id": "placeholder",
                "item_type": item_type,
                "item_id": item_id,
                "item_data": item_data or {}
            },
            headers=self._headers()
        )
        if response.status_code == 401:
            return False
        response.raise_for_status()
        return response.json()["success"]

    def delete_favorite(self, user_id: str = None, item_type: str = None,
                        item_id: str = None) -> bool:
        """删除收藏"""
        response = requests.delete(
            f"{self.base_url}/api/favorites",
            params={
                "item_type": item_type,
                "item_id": item_id
            },
            headers=self._headers()
        )
        if response.status_code == 401:
            return False
        response.raise_for_status()
        return response.json()["success"]

    def get_history(self, user_id: str = None, session_id: str = None,
                    limit: int = 20):
        """获取对话历史"""
        params = {"limit": limit}
        if session_id:
            params["session_id"] = session_id
        response = requests.get(
            f"{self.base_url}/api/history",
            params=params,
            headers=self._headers()
        )
        if response.status_code == 401:
            return None
        response.raise_for_status()
        return response.json()["history"]

    def register(self, username: str, password: str, nickname: str = None) -> Dict:
        """注册用户"""
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={"username": username, "password": password, "nickname": nickname}
        )
        if response.status_code == 400:
            return {"success": False, "error": "用户名已存在"}
        response.raise_for_status()
        return response.json()

    def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 401:
            return {"success": False, "error": "用户名或密码错误"}
        response.raise_for_status()
        return response.json()

    def get_user(self, user_id: int) -> Dict:
        """获取用户信息"""
        response = requests.get(
            f"{self.base_url}/api/auth/user/{user_id}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()["user"]
