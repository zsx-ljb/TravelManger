"""硅基流动API测试"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings

def test_siliconflow():
    """测试硅基流动API"""
    print("=" * 50)
    print("硅基流动API测试")
    print("=" * 50)

    # 检查配置
    print(f"[INFO] AI提供商: {settings.AI_PROVIDER}")
    print(f"[INFO] 模型: {settings.SILICONFLOW_MODEL}")
    print(f"[INFO] API地址: {settings.SILICONFLOW_BASE_URL}")

    if not settings.SILICONFLOW_API_KEY:
        print("[ERROR] 未配置SILICONFLOW_API_KEY")
        return

    print(f"[OK] API Key: {settings.SILICONFLOW_API_KEY[:10]}...")

    # 测试LLM调用
    print("\n--- 测试LLM调用 ---")
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage

        llm = ChatOpenAI(
            model=settings.SILICONFLOW_MODEL,
            api_key=settings.SILICONFLOW_API_KEY,
            base_url=settings.SILICONFLOW_BASE_URL,
            temperature=0.7
        )

        response = llm.invoke([HumanMessage(content="你好，请用中文简单介绍一下自己")])

        print(f"[OK] LLM响应:")
        print(f"  {response.content[:200]}...")

    except Exception as e:
        print(f"[ERROR] LLM调用失败: {e}")
        return

    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    test_siliconflow()
