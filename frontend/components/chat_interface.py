import streamlit as st
import uuid
import time
import threading
import json
import requests
from utils.api_client import TravelAgentAPI

# 模块级：按 session_id 存储流式状态
_stream_state = {}


class ChatInterface:
    def __init__(self):
        self.api = TravelAgentAPI()
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "streaming" not in st.session_state:
            st.session_state.streaming = False
        if not st.session_state.messages:
            self._load_or_init_messages()

    def _load_or_init_messages(self):
        try:
            user_id = st.session_state.get("user_id", "default_user")
            session_id = st.session_state.session_id
            history = self.api.get_history(user_id, session_id=session_id)
            if history is None:
                # get_history 返回 None 表示 401
                st.session_state["token_expired_alert"] = True
                st.rerun()
            if history:
                for item in history:
                    st.session_state.messages.append({"role": "user", "content": item["message"]})
                    st.session_state.messages.append({"role": "assistant", "content": item["response"]})
            else:
                st.session_state.messages = [
                    {"role": "assistant", "content": "您好！我是旅行规划助手。请告诉我您的旅行计划，例如：\n\n- 我想下周去日本玩5天，预算2万\n- 帮我规划一个北京到上海的周末游\n- 推荐一些适合蜜月旅行的地方"}
                ]
        except Exception:
            st.session_state.messages = [
                {"role": "assistant", "content": "您好！我是旅行规划助手。请告诉我您的旅行计划，例如：\n\n- 我想下周去日本玩5天，预算2万\n- 帮我规划一个北京到上海的周末游\n- 推荐一些适合蜜月旅行的地方"}
            ]

    def new_session(self):
        old_sid = st.session_state.session_id
        _stream_state.pop(old_sid, None)
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.streaming = False

    def _get_state(self):
        return _stream_state.get(st.session_state.session_id)

    def _start_fetch(self, prompt, session_id):
        """启动后台线程，非阻塞"""
        import queue

        state = {
            "queue": queue.Queue(),
            "full_response": "",
            "done": False,
            "error": None,
            "http_session": requests.Session(),
        }
        _stream_state[session_id] = state

        user_id = st.session_state.get("user_id", "default_user")
        history = st.session_state.messages[:-1]

        def fetch():
            try:
                headers = {"Content-Type": "application/json"}
                token = st.session_state.get("jwt_token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                resp = state["http_session"].post(
                    f"{self.api.base_url}/api/chat/stream",
                    json={"message": prompt,
                          "session_id": session_id, "history": history},
                    headers=headers,
                    stream=True, timeout=(5, 300)
                )
                if resp.status_code == 401:
                    state["token_expired"] = True
                    return
                resp.raise_for_status()
                for line in resp.iter_lines(chunk_size=1024):
                    if line:
                        data = json.loads(line.decode("utf-8").removeprefix("data: "))
                        if data.get("done"):
                            break
                        if data.get("content"):
                            state["queue"].put(data["content"])
                            time.sleep(0.1)
                        if data.get("error"):
                            state["error"] = data["error"]
                            break
            except Exception as e:
                state["error"] = str(e)
            finally:
                try:
                    state["http_session"].close()
                except Exception:
                    pass
                state["queue"].put(None)
                state["done"] = True

        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()

    def _drain_queue(self, session_id):
        """非阻塞地从队列中读取所有可用 chunks"""
        state = _stream_state.get(session_id)
        if not state:
            return
        while True:
            try:
                chunk = state["queue"].get_nowait()
            except Exception:
                break
            if chunk is None:
                state["done"] = True
                break
            state["full_response"] += chunk

    def render(self):
        session_id = st.session_state.session_id

        # ---- 正在流式输出中 ----
        if st.session_state.streaming:
            state = self._get_state()
            if state:
                # 非阻塞读取 chunks
                self._drain_queue(session_id)

                # 检测 Token 过期
                if state.get("token_expired"):
                    st.session_state["token_expired_alert"] = True
                    st.session_state.streaming = False
                    _stream_state.pop(session_id, None)
                    st.rerun()

                # 隐藏输入框
                st.markdown("""
                <style>
                div[data-testid="stChatInput"] { display: none !important; }
                </style>
                """, unsafe_allow_html=True)

                # 显示历史消息
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # 显示当前流式内容
                with st.chat_message("assistant"):
                    if state["full_response"]:
                        st.markdown(state["full_response"])
                    elif state["done"] and state["error"]:
                        st.error(f"错误: {state["error"]}")
                    else:
                        st.markdown("**正在思考...**")

                # 停止按钮
                if st.button("⏹ 停止生成", key="stop_btn", use_container_width=True):
                    st.session_state.streaming = False
                    if state["full_response"]:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": state["full_response"]
                        })
                    _stream_state.pop(session_id, None)
                    st.rerun()

                # 流式完成：保存结果
                if state["done"] and not st.session_state.streaming:
                    return

                if state["done"]:
                    st.session_state.streaming = False
                    if state["error"]:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"抱歉，出现了错误: {state["error"]}"
                        })
                    elif state["full_response"]:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": state["full_response"]
                        })
                    _stream_state.pop(session_id, None)
                    st.rerun()
                else:
                    # 还在流式中，0.5秒后自动刷新
                    time.sleep(0.5)
                    st.rerun()

            return

        # ---- 非 streaming 状态 ----
        # 显示历史消息
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 输入框
        if prompt := st.chat_input("告诉我您的旅行计划..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.streaming = True
            self._start_fetch(prompt, session_id)
            st.rerun()
