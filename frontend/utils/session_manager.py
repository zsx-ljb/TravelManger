import streamlit as st
from typing import Dict, Optional


class SessionManager:
    """会话管理器"""

    @staticmethod
    def init_session():
        """初始化会话状态"""
        defaults = {
            "user_id": "default_user",
            "username": None,
            "nickname": None,
            "logged_in": False,
            "messages": [],
            "recommendations": [],
            "selected_plan": None,
            "favorites": [],
            "current_step": "idle"
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def clear_session():
        """清除会话"""
        keys_to_clear = ["messages", "recommendations", "selected_plan", "history_loaded"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

    @staticmethod
    def get_session_info() -> Dict:
        """获取会话信息"""
        return {
            "user_id": st.session_state.get("user_id"),
            "message_count": len(st.session_state.get("messages", [])),
            "has_recommendations": bool(st.session_state.get("recommendations")),
            "has_selection": st.session_state.get("selected_plan") is not None
        }

    @staticmethod
    def add_message(role: str, content: str):
        """添加消息"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({"role": role, "content": content})

    @staticmethod
    def get_messages() -> list:
        """获取消息列表"""
        return st.session_state.get("messages", [])

    @staticmethod
    def set_current_step(step: str):
        """设置当前步骤"""
        st.session_state.current_step = step

    @staticmethod
    def get_current_step() -> str:
        """获取当前步骤"""
        return st.session_state.get("current_step", "idle")

    @staticmethod
    def login(user_id: int, username: str, nickname: str = None, token: str = None):
        """登录用户"""
        import time
        st.session_state.user_id = str(user_id)
        st.session_state.username = username
        st.session_state.nickname = nickname or username
        st.session_state.logged_in = True
        st.session_state.jwt_token = token
        st.session_state["login_time"] = time.time()

    @staticmethod
    def logout():
        """退出登录"""
        st.session_state.user_id = "default_user"
        st.session_state.username = None
        st.session_state.nickname = None
        st.session_state.logged_in = False
        st.session_state.jwt_token = None
        st.session_state.messages = []
        st.session_state.chat_list = []
        st.session_state.session_id = None
        st.session_state.login_time = 0
        # 清除所有设置相关缓存
        keys_to_remove = [k for k in st.session_state if k.startswith("settings_")]
        for key in keys_to_remove:
            del st.session_state[key]

    @staticmethod
    def get_token() -> str:
        return st.session_state.get("jwt_token")

    @staticmethod
    def is_logged_in() -> bool:
        """是否已登录"""
        return st.session_state.get("logged_in", False)
