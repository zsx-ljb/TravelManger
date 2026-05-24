import streamlit as st
import sys
import os
import uuid

# 添加当前目录到path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from utils.session_manager import SessionManager
from utils.api_client import TravelAgentAPI
from components.chat_interface import ChatInterface
from components.travel_card import TravelCard

# 页面配置
st.set_page_config(
    page_title="旅行规划助手",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载自定义样式
try:
    with open("styles/main.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except (FileNotFoundError, UnicodeDecodeError):
    pass

# 初始化会话
SessionManager.init_session()

# 初始化对话列表
if "chat_list" not in st.session_state:
    st.session_state.chat_list = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "首页"

# ========== 页面内容函数 ==========

def render_home():
    st.title("✈️ 开始规划您的旅行")

    st.markdown("**快捷操作**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏖️ 海滩度假", use_container_width=True):
            st.session_state.quick_prompt = "我想去海边度假"
    with col2:
        if st.button("🏙️ 城市探索", use_container_width=True):
            st.session_state.quick_prompt = "我想探索一个大城市"
    with col3:
        if st.button("🏔️ 自然风光", use_container_width=True):
            st.session_state.quick_prompt = "我想去看自然风光"

    st.markdown("---")

    if "quick_prompt" in st.session_state:
        quick_prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
        st.session_state.messages.append({"role": "user", "content": quick_prompt})
        st.rerun()

    chat = ChatInterface()
    chat.render()


def render_history():
    st.title("📋 历史规划")

    api = TravelAgentAPI()
    user_id = st.session_state.get("user_id", "default_user")

    try:
        plans = api.get_travel_plans(user_id)
        if not plans:
            st.info("暂无历史规划记录")
            return
        for plan in plans:
            with st.expander(f"📍 {plan.get('destination', '未知')}"):
                st.json(plan.get("plan_data", {}))
    except Exception as e:
        st.error(f"获取失败: {e}")


def render_settings():
    st.title("⚙️ 用户设置")

    api = TravelAgentAPI()
    user_id = st.session_state.get("user_id", "default_user")

    st.subheader("基本信息")
    nickname = st.text_input("昵称", value="")
    home_city = st.text_input("常用出发城市", value="")

    st.subheader("旅行偏好")
    budget_max = st.number_input("预算上限", min_value=0, value=20000, step=1000)
    travel_style = st.multiselect("旅行风格", ["休闲度假", "文化探索", "美食之旅", "户外探险"])

    if st.button("保存设置"):
        st.success("设置已保存！")


# ========== 侧边栏 ==========

with st.sidebar:
    st.markdown("# ✈️ 旅行规划助手")
    st.markdown("---")
    st.markdown(f"**用户:** {st.session_state.get('user_id', 'default_user')}")

    st.markdown("### 导航")

    # 使用按钮切换页面，更稳定
    if st.button("🏠 首页", use_container_width=True,
                 type="primary" if st.session_state.current_page == "首页" else "secondary"):
        st.session_state.current_page = "首页"
        st.rerun()

    if st.button("📋 历史规划", use_container_width=True,
                 type="primary" if st.session_state.current_page == "历史规划" else "secondary"):
        st.session_state.current_page = "历史规划"
        st.rerun()

    if st.button("⚙️ 用户设置", use_container_width=True,
                 type="primary" if st.session_state.current_page == "用户设置" else "secondary"):
        st.session_state.current_page = "用户设置"
        st.rerun()

    st.markdown("---")
    st.markdown("### 对话管理")

    if st.button("🆕 开启新对话", use_container_width=True):
        if st.session_state.messages:
            title = "新对话"
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    title = msg["content"][:20] + ("..." if len(msg["content"]) > 20 else "")
                    break

            st.session_state.chat_list.append({
                "id": len(st.session_state.chat_list),
                "title": title,
                "messages": st.session_state.messages.copy(),
                "session_id": st.session_state.get("session_id", "")
            })

        # 生成新的session_id
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

    if st.session_state.chat_list:
        st.markdown("---")
        st.markdown("### 历史对话")
        for chat in reversed(st.session_state.chat_list):
            col1, col2 = st.columns([5, 1])
            with col1:
                short_title = chat["title"][:12] + ("..." if len(chat["title"]) > 12 else "")
                if st.button(short_title, key=f"chat_{chat['id']}", use_container_width=True):
                    st.session_state.messages = chat["messages"].copy()
                    st.session_state.session_id = chat.get("session_id", str(uuid.uuid4()))
                    st.session_state.current_chat_id = chat["id"]
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{chat['id']}"):
                    st.session_state.chat_list.remove(chat)
                    st.rerun()

    st.markdown("---")
    st.markdown("### 会话状态")
    info = SessionManager.get_session_info()
    st.markdown(f"- 消息数: {info['message_count']}")
    st.markdown(f"- 保存对话: {len(st.session_state.chat_list)}")


# ========== 页面路由 ==========

page = st.session_state.current_page

if page == "首页":
    render_home()
elif page == "历史规划":
    render_history()
elif page == "用户设置":
    render_settings()
