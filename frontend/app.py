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

# 侧边栏按钮强制单行
st.markdown("""
<style>
section[data-testid="stSidebar"] button {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
""", unsafe_allow_html=True)

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

    try:
        plans = api.get_travel_plans()
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

    # 每次进入设置页面都从 API 加载当前用户的偏好
    try:
        prefs = api.get_user_preferences()
        st.session_state["settings_nickname"] = prefs.get("nickname", "")
        st.session_state["settings_home_city"] = prefs.get("home_city", "")
        st.session_state["settings_budget_max"] = prefs.get("budget_max", 20000)
        st.session_state["settings_travel_style"] = prefs.get("travel_style", [])
    except Exception:
        pass

    st.subheader("基本信息")
    nickname = st.text_input("昵称", key="settings_nickname")
    home_city = st.text_input("常用出发城市", key="settings_home_city")

    st.subheader("旅行偏好")
    budget_max = st.number_input("预算上限", min_value=0, key="settings_budget_max", step=1000)
    travel_style = st.multiselect("旅行风格", ["休闲度假", "文化探索", "美食之旅", "户外探险"],
                                   key="settings_travel_style")

    if st.button("保存设置", type="primary"):
        preferences = {
            "nickname": st.session_state.settings_nickname,
            "home_city": st.session_state.settings_home_city,
            "budget_max": st.session_state.settings_budget_max,
            "travel_style": st.session_state.settings_travel_style,
        }
        result = api.update_user_preferences(preferences)
        if result.get("success"):
            if st.session_state.settings_nickname:
                st.session_state["nickname"] = st.session_state.settings_nickname
            st.success("设置已保存！")
        else:
            st.error("保存失败，请重试")


# ========== 登录页面 ==========

def _mark_field_red(field_key: str):
    """用 JS 给指定输入框加红色边框"""
    import streamlit.components.v1 as components
    components.html(f"""
    <script>
    (function(){{
        var el = window.parent.document.querySelector('[data-testid="stTextInput"][data="{field_key}"] input');
        if(el){{ el.style.borderColor='#ef4444'; el.style.boxShadow='0 0 0 1px #ef4444'; }}
    }})();
    </script>
    """, height=0, scrolling=False)


def render_login():
    import streamlit.components.v1 as components

    st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    button[data-testid="stSidebarExpandButton"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .field-error { color: #ef4444; font-size: 13px; margin-top: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # ---------- 从 localStorage 恢复上次记住的用户名 ----------
    if "login_inited" not in st.session_state:
        st.session_state.login_inited = True
        components.html("""
        <script>
        (function(){
          var saved = localStorage.getItem('travel_remember_user');
          if(saved){
            var url = new URL(window.location.href);
            url.searchParams.set('rm_user', saved);
            window.parent.location.href = url.toString();
          }
        })();
        </script>
        """, height=0, scrolling=False)

    qp = st.query_params
    saved_user = qp.get("rm_user", "")
    if saved_user:
        st.session_state.login_user = saved_user
        st.query_params.clear()

    # 初始化字段错误状态
    if "field_errors" not in st.session_state:
        st.session_state.field_errors = {}

    # Token 过期红色提醒（显示在标题上方）
    if st.session_state.pop("token_expired_alert", False):
        st.error("⚠️ 登录已过期，请重新登录")

    st.markdown("<h1 style='text-align:center;'>✈️ 旅行规划助手</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#888;'>请登录或注册以开始使用</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab = st.radio("用户认证", ["登录", "注册"], horizontal=True, label_visibility="collapsed")
        api = TravelAgentAPI()

        # 切换 tab 时清除错误
        if st.session_state.get("last_auth_tab") != auth_tab:
            st.session_state.field_errors = {}
        st.session_state.last_auth_tab = auth_tab

        errors = st.session_state.field_errors

        # ====== 登录 ======
        if auth_tab == "登录":
            login_user = st.text_input("用户名", key="login_user")
            if "login_user" in errors:
                st.markdown(f'<p class="field-error">✗ {errors["login_user"]}</p>', unsafe_allow_html=True)
                _mark_field_red("login_user")

            login_pass = st.text_input("密码", type="password", key="login_pass")
            if "login_pass" in errors:
                st.markdown(f'<p class="field-error">✗ {errors["login_pass"]}</p>', unsafe_allow_html=True)
                _mark_field_red("login_pass")

            remember = st.checkbox("记住我")

            if st.button("登 录", use_container_width=True, type="primary"):
                st.session_state.field_errors = {}
                if not login_user:
                    st.session_state.field_errors["login_user"] = "用户名不能为空"
                    st.rerun()
                if not login_pass:
                    st.session_state.field_errors["login_pass"] = "密码不能为空"
                    st.rerun()

                result = api.login(login_user, login_pass)
                if result.get("success"):
                    user = result["user"]
                    token = result.get("token")
                    if remember:
                        components.html(
                            f'<script>localStorage.setItem("travel_remember_user","{user["username"]}")</script>',
                            height=0, scrolling=False
                        )
                    else:
                        components.html(
                            '<script>localStorage.removeItem("travel_remember_user")</script>',
                            height=0, scrolling=False
                        )
                    SessionManager.login(user["id"], user["username"], user.get("nickname"), token)
                    st.rerun()
                else:
                    st.session_state.field_errors["login_user"] = "账号或密码错误，请检查后重试"
                    st.rerun()

        # ====== 注册 ======
        else:
            import re as _re
            reg_user = st.text_input("用户名", key="reg_user")
            if "reg_user" in errors:
                st.markdown(f'<p class="field-error">✗ {errors["reg_user"]}</p>', unsafe_allow_html=True)
                _mark_field_red("reg_user")

            reg_nick = st.text_input("昵称（可选）", key="reg_nick")

            reg_pass = st.text_input("密码", type="password", key="reg_pass",
                                     help="密码只能包含数字、大小写字母和特殊字符")
            if "reg_pass" in errors:
                st.markdown(f'<p class="field-error">✗ {errors["reg_pass"]}</p>', unsafe_allow_html=True)
                _mark_field_red("reg_pass")

            reg_pass2 = st.text_input("确认密码", type="password", key="reg_pass2")
            if "reg_pass2" in errors:
                st.markdown(f'<p class="field-error">✗ {errors["reg_pass2"]}</p>', unsafe_allow_html=True)
                _mark_field_red("reg_pass2")

            if st.button("注 册", use_container_width=True, type="primary"):
                st.session_state.field_errors = {}
                if not reg_user:
                    st.session_state.field_errors["reg_user"] = "用户名不能为空"
                    st.rerun()
                if not reg_pass:
                    st.session_state.field_errors["reg_pass"] = "密码不能为空"
                    st.rerun()
                if reg_pass != reg_pass2:
                    st.session_state.field_errors["reg_pass2"] = "两次密码不一致，请重新输入"
                    st.rerun()
                if not _re.match(r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]+$', reg_pass):
                    st.session_state.field_errors["reg_pass"] = "密码只能包含数字、大小写字母和特殊字符"
                    st.rerun()

                result = api.register(reg_user, reg_pass, reg_nick or reg_user)
                if result.get("success"):
                    user = result["user"]
                    token = result.get("token")
                    SessionManager.login(user["id"], user["username"], user.get("nickname"), token)
                    st.rerun()
                else:
                    st.session_state.field_errors["reg_user"] = "用户名已存在，请更换"
                    st.rerun()


# ========== 侧边栏 ==========

with st.sidebar:
    st.markdown("# ✈️ 旅行规划助手")
    st.markdown("---")

    # 已登录：显示用户信息 + 退出按钮
    if SessionManager.is_logged_in():
        nickname = st.session_state.get("nickname", st.session_state.get("username", "用户"))
        st.markdown(f"**👤 {nickname}**")
        if st.button("退出登录", use_container_width=True):
            SessionManager.logout()
            st.rerun()

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
        from components.chat_interface import _stream_state
        old_sid = st.session_state.get("session_id")
        if old_sid:
            _stream_state.pop(old_sid, None)

        if st.session_state.messages:
            title = "新对话"
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    title = msg["content"][:10] + ("..." if len(msg["content"]) > 10 else "")
                    break

            st.session_state.chat_list.append({
                "id": len(st.session_state.chat_list),
                "title": title,
                "messages": st.session_state.messages.copy(),
                "session_id": old_sid or ""
            })

        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.streaming = False
        st.session_state.current_chat_id = None
        st.rerun()

    if st.session_state.chat_list:
        st.markdown("---")
        st.markdown("### 历史对话")
        for chat in reversed(st.session_state.chat_list):
            col1, col2 = st.columns([5, 1])
            with col1:
                short_title = chat["title"][:8] + ("..." if len(chat["title"]) > 8 else "")
                if st.button(short_title, key=f"chat_{chat['id']}", use_container_width=True):
                    from components.chat_interface import _stream_state
                    old_sid = st.session_state.get("session_id")
                    if old_sid:
                        _stream_state.pop(old_sid, None)
                    st.session_state.messages = chat["messages"].copy()
                    st.session_state.session_id = chat.get("session_id", str(uuid.uuid4()))
                    st.session_state.streaming = False
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

if not SessionManager.is_logged_in():
    render_login()
else:
    import time as _time
    login_time = st.session_state.get("login_time", 0)
    if login_time and _time.time() - login_time >= 3600:
        st.session_state["token_expired_alert"] = True
        SessionManager.logout()
        st.rerun()

    page = st.session_state.current_page

    if page == "首页":
        render_home()
    elif page == "历史规划":
        render_history()
    elif page == "用户设置":
        render_settings()
