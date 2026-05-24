import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings:
    # 项目根目录
    BASE_DIR = Path(__file__).parent.parent

    # Claude API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = "claude-sonnet-4-6"

    # 硅基流动 API (OpenAI兼容)
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
    SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    SILICONFLOW_MODEL = os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-72B-Instruct")

    # AI提供商选择: "claude" 或 "siliconflow"
    AI_PROVIDER = os.getenv("AI_PROVIDER", "siliconflow")

    # Amadeus API (机票、酒店)
    AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "")
    AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "")

    # 高德地图 API
    AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")

    # OpenWeatherMap API
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

    # 数据库配置
    DATABASE_PATH = BASE_DIR / "data" / "user_memory.db"

    # 应用配置
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # API限流配置
    API_RATE_LIMIT = 100  # 每分钟最大请求数
    API_CACHE_TTL = 3600  # 缓存有效期（秒）


settings = Settings()
