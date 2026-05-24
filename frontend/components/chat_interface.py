import streamlit as st
import uuid
from utils.api_client import TravelAgentAPI


class ChatInterface:
    """对话界面组件"""

    def __init__(self):
        self.api = TravelAgentAPI()

        # 初始化session_id
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())

        # 初始化会话历史
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 如果是新对话（没有消息），从后端加载或显示欢迎语
        if not st.session_state.messages:
            self._load_or_init_messages()

    def _load_or_init_messages(self):
        """从后端加载历史或初始化欢迎语"""
        try:
            user_id = st.session_state.get("user_id", "default_user")
            session_id = st.session_state.session_id
            history = self.api.get_history(user_id, session_id=session_id)

            if history:
                # 从后端加载历史对话
                for item in history:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": item["message"]
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": item["response"]
                    })
            else:
                # 没有历史，显示欢迎语
                st.session_state.messages = [
                    {"role": "assistant", "content": "您好！我是旅行规划助手。请告诉我您的旅行计划，例如：\n\n- 我想下周去日本玩5天，预算2万\n- 帮我规划一个北京到上海的周末游\n- 推荐一些适合蜜月旅行的地方"}
                ]
        except Exception:
            # 加载失败，显示欢迎语
            st.session_state.messages = [
                {"role": "assistant", "content": "您好！我是旅行规划助手。请告诉我您的旅行计划，例如：\n\n- 我想下周去日本玩5天，预算2万\n- 帮我规划一个北京到上海的周末游\n- 推荐一些适合蜜月旅行的地方"}
            ]

    def new_session(self):
        """开启新对话"""
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []

    def render(self):
        """渲染对话界面"""
        # 显示历史消息
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 用户输入
        if prompt := st.chat_input("告诉我您的旅行计划..."):
            # 显示用户消息
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # 调用后端API
            with st.chat_message("assistant"):
                with st.spinner("正在为您规划..."):
                    try:
                        response = self.api.chat(
                            message=prompt,
                            user_id=st.session_state.get("user_id", "default_user"),
                            session_id=st.session_state.session_id,
                            history=st.session_state.messages[:-1]
                        )

                        st.markdown(response["message"])

                        # 保存助手回复
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response["message"]
                        })

                    except Exception as e:
                        error_msg = f"抱歉，出现了错误: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
