import streamlit as st
from typing import Dict


class TravelCard:
    """旅行卡片组件"""

    def __init__(self, plan_data: Dict):
        self.plan = plan_data

    def render(self):
        """渲染旅行卡片"""
        with st.container():
            # 卡片样式
            st.markdown("""
            <style>
            .travel-card {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            </style>
            """, unsafe_allow_html=True)

            # 目的地名称
            st.subheader(f"📍 {self.plan.get('destination', '未知目的地')}")

            # 简要信息
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"**天数:** {self.plan.get('duration', 'N/A')}天")
            with cols[1]:
                st.markdown(f"**预算:** ¥{self.plan.get('budget', 'N/A')}")
            with cols[2]:
                rating = self.plan.get('rating', 5)
                st.markdown(f"**评分:** {'⭐' * rating}")

            # 简介
            if "highlights" in self.plan:
                st.markdown(f"**亮点:** {self.plan['highlights']}")

            if "description" in self.plan:
                st.markdown(f"**简介:** {self.plan['description']}")

            # 操作按钮
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("查看详情", key=f"detail_{self.plan.get('id', 'unknown')}"):
                    st.session_state.selected_plan = self.plan
                    st.rerun()
            with col2:
                if st.button("加入收藏", key=f"fav_{self.plan.get('id', 'unknown')}"):
                    self._add_to_favorites()
            with col3:
                if st.button("开始规划", key=f"plan_{self.plan.get('id', 'unknown')}"):
                    st.session_state.quick_plan = self.plan.get('destination', '')

    def _add_to_favorites(self):
        """添加到收藏"""
        if "favorites" not in st.session_state:
            st.session_state.favorites = []

        if self.plan not in st.session_state.favorites:
            st.session_state.favorites.append(self.plan)
            st.success("已添加到收藏！")
        else:
            st.info("已在收藏中")
