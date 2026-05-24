from typing import List, Dict

# 地图相关依赖（可选）
try:
    import folium
    from streamlit_folium import st_folium
    HAS_MAP = True
except ImportError:
    HAS_MAP = False


class MapView:
    """地图展示组件"""

    def __init__(self, locations: List[Dict]):
        """
        初始化地图组件

        Args:
            locations: 位置列表，每个元素包含name, lat, lon, description
        """
        self.locations = locations

    def render(self, width: int = 800, height: int = 500):
        """渲染地图"""
        if not HAS_MAP:
            return self._render_fallback()

        if not self.locations:
            return self._render_empty()

        # 计算中心点
        center_lat = sum(loc.get("lat", 0) for loc in self.locations) / len(self.locations)
        center_lon = sum(loc.get("lon", 0) for loc in self.locations) / len(self.locations)

        # 创建地图
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

        # 添加标记点
        for idx, loc in enumerate(self.locations):
            popup_html = f"""
            <b>{loc.get('name', f'地点{idx+1}')}</b><br>
            {loc.get('description', '')}
            """
            folium.Marker(
                [loc.get("lat", 0), loc.get("lon", 0)],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=loc.get("name", f"地点{idx+1}"),
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

        # 添加路线
        if len(self.locations) > 1:
            coordinates = [[loc.get("lat", 0), loc.get("lon", 0)] for loc in self.locations]
            folium.PolyLine(
                coordinates,
                weight=2,
                color="blue",
                opacity=0.7
            ).add_to(m)

        # 显示地图
        st_folium(m, width=width, height=height)

    def _render_fallback(self):
        """当地图库不可用时的备用显示"""
        st.warning("地图功能需要安装 folium 和 streamlit-folium")
        st.markdown("**地点列表:**")
        for idx, loc in enumerate(self.locations):
            st.markdown(f"{idx+1}. {loc.get('name', '未知')} ({loc.get('lat', 0)}, {loc.get('lon', 0)})")

    def _render_empty(self):
        """空位置列表时的显示"""
        st.info("暂无位置信息")
