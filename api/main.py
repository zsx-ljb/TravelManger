from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import re
import jwt
import logging
from datetime import datetime, timedelta

from agent.travel_agent import travel_agent
from memory.user_memory import UserMemory
from config.settings import settings
from config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

security = HTTPBearer()


def create_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET,
                           algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token已过期")
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    except jwt.InvalidTokenError as e:
        logger.warning(f"无效Token: {e}")
        raise HTTPException(status_code=401, detail="无效的认证凭证")

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
    user_id: str = "default"
    preferences: Dict[str, Any]


class FavoriteRequest(BaseModel):
    user_id: str
    item_type: str
    item_id: str
    item_data: Dict[str, Any]


class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


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


@app.on_event("startup")
async def startup_event():
    logger.info("API服务启动")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(verify_token)):
    """对话接口"""
    try:
        user_id = str(current_user["user_id"])
        result = travel_agent.chat(
            user_input=request.message,
            user_id=user_id,
            history=request.history
        )

        # 保存对话历史（带session_id）
        if result["success"]:
            memory.save_conversation(
                user_id=user_id,
                message=request.message,
                response=result["message"],
                session_id=request.session_id
            )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history(session_id: str = None, limit: int = 20,
                      current_user: dict = Depends(verify_token)):
    """获取对话历史"""
    try:
        user_id = str(current_user["user_id"])
        history = memory.get_conversation_history(user_id, limit=limit, session_id=session_id)
        return {"history": history}
    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest = Body(...),
                      current_user: dict = Depends(verify_token)):
    """流式对话接口"""
    user_id = str(current_user["user_id"])

    async def generate():
        full_response = ""
        client_disconnected = False
        try:
            for chunk in travel_agent.chat_stream(
                user_input=request.message,
                user_id=user_id,
                history=request.history
            ):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk, 'done': False}, ensure_ascii=False)}\n\n"

            # 保存完整对话历史
            if full_response:
                memory.save_conversation(
                    user_id=user_id,
                    message=request.message,
                    response=full_response,
                    session_id=request.session_id
                )
            yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"

        except GeneratorExit:
            # 客户端断开连接，保存已生成的部分回复
            client_disconnected = True
            if full_response:
                memory.save_conversation(
                    user_id=user_id,
                    message=request.message,
                    response=full_response,
                    session_id=request.session_id
                )
        except Exception as e:
            if not client_disconnected:
                yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/plan", response_model=TravelPlanResponse)
async def plan_trip(request: PlanRequest, current_user: dict = Depends(verify_token)):
    """规划旅行接口"""
    try:
        user_id = str(current_user["user_id"])
        result = travel_agent.plan_trip(
            user_input=request.user_input,
            user_id=user_id
        )

        # 保存规划
        if result["success"] and result.get("parsed_intent"):
            destination = result["parsed_intent"].get("destination", "未知")
            memory.save_travel_plan(
                user_id=user_id,
                destination=destination,
                plan_data=result.get("parsed_intent", {})
            )

        return TravelPlanResponse(**result)

    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans")
async def get_plans(limit: int = 10, current_user: dict = Depends(verify_token)):
    """获取用户旅行规划"""
    user_id = str(current_user["user_id"])
    plans = memory.get_travel_plans(user_id, limit)
    return {"plans": plans}


@app.get("/api/user/preferences")
async def get_preferences(current_user: dict = Depends(verify_token)):
    """获取用户偏好"""
    user_id = str(current_user["user_id"])
    preferences = memory.get_preferences(user_id)
    return {"preferences": preferences}


@app.put("/api/user/preferences")
async def update_preferences(request: PreferenceRequest,
                             current_user: dict = Depends(verify_token)):
    """更新用户偏好"""
    user_id = str(current_user["user_id"])
    for key, value in request.preferences.items():
        memory.save_preference(user_id, key, value)
    return {"success": True}


@app.post("/api/favorites")
async def add_favorite(request: FavoriteRequest,
                       current_user: dict = Depends(verify_token)):
    """添加收藏"""
    user_id = str(current_user["user_id"])
    success = memory.add_favorite(
        user_id,
        request.item_type,
        request.item_id,
        request.item_data
    )
    return {"success": success}


@app.get("/api/favorites")
async def get_favorites(item_type: Optional[str] = None,
                        current_user: dict = Depends(verify_token)):
    """获取收藏"""
    user_id = str(current_user["user_id"])
    favorites = memory.get_favorites(user_id, item_type)
    return {"favorites": favorites}


@app.delete("/api/favorites")
async def delete_favorite(item_type: str, item_id: str,
                          current_user: dict = Depends(verify_token)):
    """删除收藏"""
    user_id = str(current_user["user_id"])
    success = memory.delete_favorite(user_id, item_type, item_id)
    return {"success": success}


@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """注册用户"""
    if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]+$', request.password):
        raise HTTPException(status_code=400, detail="密码只能包含数字、大小写字母和特殊字符")
    user = memory.register_user(request.username, request.password, request.nickname)
    if user is None:
        logger.warning(f"注册失败，用户名已存在: {request.username}")
        raise HTTPException(status_code=400, detail="用户名已存在")
    logger.info(f"用户注册成功: {request.username}, id={user['id']}")
    token = create_token(user["id"], user["username"])
    return {"success": True, "user": user, "token": token}


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """用户登录"""
    user = memory.login_user(request.username, request.password)
    if user is None:
        logger.warning(f"登录失败: {request.username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    logger.info(f"用户登录成功: {request.username}, id={user['id']}")
    token = create_token(user["id"], user["username"])
    return {"success": True, "user": user, "token": token}


@app.get("/api/auth/user/{user_id}")
async def get_user(user_id: int):
    """获取用户信息"""
    user = memory.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"user": user}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
