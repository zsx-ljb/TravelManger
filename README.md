# 旅行规划助手 Agent

基于 AI 的智能旅行规划助手，帮助用户规划个性化旅行行程。

## ✨ 功能特点

- 🤖 **智能对话**: 使用 Claude AI 理解用户需求
- ✈️ **机票查询**: 搜索航班信息和价格
- 🏨 **酒店推荐**: 根据预算推荐住宿
- 🎯 **景点推荐**: 基于兴趣推荐景点
- 🌤️ **天气查询**: 获取目的地天气预报
- 💾 **记忆系统**: 保存用户偏好和历史规划
- 📊 **预算追踪**: 实时跟踪旅行预算

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
ANTHROPIC_API_KEY=your_claude_api_key
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret
```

### 3. 启动应用

**方式一：使用启动脚本**

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

**方式二：手动启动**

```bash
# 启动Web界面
cd frontend
streamlit run app.py

# 启动API服务
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问应用

- Web界面: http://localhost:8501
- API文档: http://localhost:8000/docs

## 📁 项目结构

```
travel_agent/
├── agent/                    # Agent核心引擎
│   ├── travel_agent.py      # 主Agent逻辑
│   ├── state.py             # 状态定义
│   └── prompts.py           # Prompt模板
├── tools/                    # API工具集
│   ├── flight.py            # 机票查询
│   ├── hotel.py             # 酒店查询
│   ├── attraction.py        # 景点推荐
│   └── weather.py           # 天气查询
├── memory/                   # 记忆系统
│   └── user_memory.py       # 用户偏好管理
├── api/                      # FastAPI服务
│   └── main.py              # API接口
├── frontend/                 # Streamlit前端
│   ├── app.py               # 主应用
│   ├── pages/               # 页面组件
│   └── components/          # UI组件
├── config/                   # 配置管理
│   └── settings.py          # 配置文件
├── tests/                    # 测试文件
├── requirements.txt          # 依赖列表
└── .env.example              # 环境变量模板
```

## 🔧 技术栈

- **后端**: Python, FastAPI, LangChain, LangGraph
- **AI**: Claude API (claude-sonnet-4-6)
- **前端**: Streamlit
- **数据库**: SQLite, ChromaDB
- **API集成**: Amadeus, OpenWeatherMap

## 📝 使用示例

```
用户: 我想下周去日本玩5天，预算2万，喜欢动漫和美食

助手: 好的！我来帮您规划日本动漫美食之旅...

[生成详细的行程安排，包括机票、酒店、每日行程等]
```

## 🎯 开发计划

- [x] 基础对话Agent
- [x] API工具集成
- [x] 记忆系统
- [x] Web界面
- [ ] 多语言支持
- [ ] 图像生成
- [ ] 实时价格监控
- [ ] 社交分享

## 📄 License

MIT License
# TravelManger
