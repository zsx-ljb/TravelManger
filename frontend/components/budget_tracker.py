import streamlit as st
from typing import Dict, List


class BudgetTracker:
    """预算追踪组件"""

    def __init__(self, budget: float = 0, expenses: Dict = None):
        """
        初始化预算追踪器

        Args:
            budget: 总预算
            expenses: 支出明细 {"category": amount}
        """
        self.budget = budget
        self.expenses = expenses or {}

    def render(self):
        """渲染预算追踪界面"""
        st.subheader("💰 预算追踪")

        # 总预算输入
        col1, col2 = st.columns(2)
        with col1:
            self.budget = st.number_input(
                "总预算",
                min_value=0.0,
                value=self.budget,
                step=1000.0,
                format="%.0f"
            )
        with col2:
            total_expense = sum(self.expenses.values())
            remaining = self.budget - total_expense

            st.metric("已支出", f"¥{total_expense:,.0f}")
            st.metric("剩余预算", f"¥{remaining:,.0f}")

        # 预算进度条
        if self.budget > 0:
            progress = min(total_expense / self.budget, 1.0)
            st.progress(progress)
            st.caption(f"已使用 {progress*100:.1f}%")

        # 支出明细
        st.markdown("**支出明细**")

        categories = {
            "flight": "✈️ 机票",
            "hotel": "🏨 住宿",
            "food": "🍜 餐饮",
            "transport": "🚗 交通",
            "activity": "🎯 活动",
            "shopping": "🛍️ 购物",
            "other": "📦 其他"
        }

        for cat_key, cat_name in categories.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                self.expenses[cat_key] = st.number_input(
                    cat_name,
                    min_value=0.0,
                    value=self.expenses.get(cat_key, 0.0),
                    step=100.0,
                    format="%.0f",
                    key=f"expense_{cat_key}",
                    label_visibility="collapsed"
                )
            with col2:
                st.text_input(
                    "",
                    value=f"¥{self.expenses.get(cat_key, 0):,.0f}",
                    disabled=True,
                    key=f"expense_display_{cat_key}",
                    label_visibility="collapsed"
                )

        # 返回汇总
        return {
            "budget": self.budget,
            "expenses": self.expenses,
            "total": sum(self.expenses.values()),
            "remaining": self.budget - sum(self.expenses.values())
        }

    def render_summary(self):
        """渲染预算摘要"""
        total_expense = sum(self.expenses.values())
        remaining = self.budget - total_expense

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总预算", f"¥{self.budget:,.0f}")
        with col2:
            st.metric("已支出", f"¥{total_expense:,.0f}")
        with col3:
            st.metric("剩余", f"¥{remaining:,.0f}")
