from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from agent.travel_agent import travel_agent
from memory.user_memory import UserMemory

app = FastAPI(
    title="旅行规划助手API",
    description="基于AI的旅行规划助手后端服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化记忆系统
memory = UserMemory()


# 请求模型
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"
    session_id: str = "default"
    history: List[Dict[str, Any]] = []


class PlanRequest(BaseModel):
    user_id: str = "default"
    user_input: str


class PreferenceRequest(BaseModel):
    user_id: str
    preferences: Dict[str, Any]


class FavoriteRequest(BaseModel):
    user_id: str
    item_type: str
    item_id: str
    item_data: Dict[str, Any]


# 响应模型
class ChatResponse(BaseModel):
    message: str
    success: bool
    error: Optional[str] = None


class TravelPlanResponse(BaseModel):
    message: str
    success: bool
    parsed_intent: Optional[Dict] = None
    query_results: Optional[Dict] = None
    error: Optional[str] = None


# API路由
@app.get("/")
async def root():
    return {"message": "旅行规划助手API服务运行中"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口"""
    try:
        result = travel_agent.chat(
            user_input=request.message,
            user_id=request.user_id,
            history=request.history
        )

        # 保存对话历史（带session_id）
        if result["success"]:
            memory.save_conversation(
                user_id=request.user_id,
                message=request.message,
                response=result["message"],
                session_id=request.session_id
            )

        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history(user_id: str, session_id: str = None):
    """获取对话历史"""
    try:
        history = memory.get_conversation_history(user_id, session_id=session_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plan", response_model=TravelPlanResponse)
async def plan_trip(request: PlanRequest):
    """规划旅行接口"""
    try:
        result = travel_agent.plan_trip(
            user_input=request.user_input,
            user_id=request.user_id
        )

        # 保存规划
        if result["success"] and result.get("parsed_intent"):
            destination = result["parsed_intent"].get("destination", "未知")
            memory.save_travel_plan(
                user_id=request.user_id,
                destination=destination,
                plan_data=result.get("parsed_intent", {})
            )

        return TravelPlanResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans")
async def get_plans(user_id: str, limit: int = 10):
    """获取用户旅行规划"""
    plans = memory.get_travel_plans(user_id, limit)
    return {"plans": plans}


@app.get("/api/user/preferences")
async def get_preferences(user_id: str):
    """获取用户偏好"""
    preferences = memory.get_preferences(user_id)
    return {"preferences": preferences}


@app.put("/api/user/preferences")
async def update_preferences(request: PreferenceRequest):
    """更新用户偏好"""
    for key, value in request.preferences.items():
        memory.save_preference(request.user_id, key, value)
    return {"success": True}


@app.post("/api/favorites")
async def add_favorite(request: FavoriteRequest):
    """添加收藏"""
    success = memory.add_favorite(
        request.user_id,
        request.item_type,
        request.item_id,
        request.item_data
    )
    return {"success": success}


@app.get("/api/favorites")
async def get_favorites(user_id: str, item_type: Optional[str] = None):
    """获取收藏"""
    favorites = memory.get_favorites(user_id, item_type)
    return {"favorites": favorites}


@app.delete("/api/favorites")
async def delete_favorite(user_id: str, item_type: str, item_id: str):
    """删除收藏"""
    success = memory.delete_favorite(user_id, item_type, item_id)
    return {"success": success}


@app.get("/api/history")
async def get_history(user_id: str, limit: int = 20):
    """获取对话历史"""
    history = memory.get_conversation_history(user_id, limit)
    return {"history": history}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
