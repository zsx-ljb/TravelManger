"""高德地图API测试"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from tools.map import MapTool

def test_amap():
    """测试高德地图API"""
    print("=" * 50)
    print("高德地图API测试")
    print("=" * 50)

    map_tool = MapTool()

    # 检查API Key
    if not map_tool.api_key:
        print("[ERROR] 未配置AMAP_API_KEY")
        return

    print(f"[OK] API Key: {map_tool.api_key[:10]}...")

    # 测试1: 地理编码（地址转坐标）
    print("\n--- 测试1: 地理编码 ---")
    result = map_tool.geocode("天安门", "北京")
    if result:
        print(f"[OK] 地址: {result['address']}")
        print(f"  坐标: {result['lng']}, {result['lat']}")
    else:
        print("[FAIL] 地理编码失败")

    # 测试2: POI搜索（搜景点）
    print("\n--- 测试2: POI搜索 ---")
    pois = map_tool.search_poi("故宫", "北京")
    if pois:
        print(f"[OK] 找到 {len(pois)} 个结果:")
        for poi in pois[:3]:
            print(f"  - {poi['name']}: {poi['address']}")
    else:
        print("[FAIL] POI搜索失败")

    # 测试3: 逆地理编码（坐标转地址）
    print("\n--- 测试3: 逆地理编码 ---")
    if result:
        addr = map_tool.reverse_geocode(result['lng'], result['lat'])
        if addr:
            print(f"[OK] 逆地理编码: {addr['address']}")
        else:
            print("[FAIL] 逆地理编码失败")

    # 测试4: 驾车路线规划
    print("\n--- 测试4: 驾车路线规划 ---")
    # 天安门到故宫
    route = map_tool.get_route_driving(116.397428, 39.90923, 116.397026, 39.918058)
    if route:
        print(f"[OK] 距离: {route['distance']}米")
        print(f"  时间: {route['duration']}秒")
        print(f"  费用: {route['toll']}")
    else:
        print("[FAIL] 路线规划失败")

    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    test_amap()
