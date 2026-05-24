from typing import Dict, List, Any
from datetime import datetime


def format_currency(amount: float, currency: str = "CNY") -> str:
    """格式化货币"""
    symbols = {
        "CNY": "¥",
        "USD": "$",
        "EUR": "€",
        "JPY": "¥"
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.0f}"


def format_date(date_str: str, output_format: str = "%Y年%m月%d日") -> str:
    """格式化日期"""
    try:
        if "T" in date_str:
            date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return date_str


def format_duration(hours: int, minutes: int = 0) -> str:
    """格式化时长"""
    if hours > 0 and minutes > 0:
        return f"{hours}小时{minutes}分"
    elif hours > 0:
        return f"{hours}小时"
    else:
        return f"{minutes}分"


def format_rating(rating: float, max_rating: int = 5) -> str:
    """格式化评分"""
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = max_rating - full_stars - half_star

    stars = "⭐" * full_stars
    if half_star:
        stars += "✨"
    stars += "☆" * empty_stars

    return f"{stars} {rating:.1f}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_list(items: List[str], separator: str = "、") -> str:
    """格式化列表"""
    return separator.join(items)


def parse_budget_range(budget: str) -> tuple:
    """解析预算范围"""
    try:
        if "-" in budget:
            min_budget, max_budget = budget.split("-")
            return (int(min_budget), int(max_budget))
        else:
            return (0, int(budget))
    except (ValueError, TypeError):
        return (0, 0)
