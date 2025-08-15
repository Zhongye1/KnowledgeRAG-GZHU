import io
import json
import logging
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List


# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()

class DownloadChatRequest(BaseModel):
    chat_sessions: Dict[str, Any]  # 明确请求结构


class SaveSessionRequest(BaseModel):
    sessionId: str
    session: Dict[str, Any]


global_chat_history = {}  # 示例初始化
CHAT_DOCUMENT_DIR = "chat_units/chat_documents"  # 存储目录

"""
@router.post("/download-chat-json")
async def download_chat_json(request: DownloadChatRequest):
    try:
        chat_data = request.chat_sessions
        if not chat_data or not isinstance(chat_data, dict):
            raise ValueError("无效的聊天数据格式")

        # 创建存储目录（如果不存在）
        os.makedirs(CHAT_DOCUMENT_DIR, exist_ok=True)

        # 生成文件名（使用时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_session_{timestamp}.json"
        file_path = os.path.join(CHAT_DOCUMENT_DIR, filename)

        # 将数据保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)

        for session_id, session_data in chat_data.items():
            global_chat_history[session_id] = session_data

        # 创建下载响应
        json_data = json.dumps(chat_data, indent=2, ensure_ascii=False)
        file_stream = io.BytesIO(json_data.encode('utf-8'))
        response = StreamingResponse(
            content=file_stream,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )

        logger.info(f"成功生成并保存聊天文件: {file_path}")
        return response

    except Exception as e:
        logger.error(f"下载聊天数据失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"生成下载文件失败: {str(e)}"
        )
"""


# 新增API：获取所有已保存的对话文件
@router.get("/saved-chats")
async def get_saved_chats():
    try:
        saved_chats = []
        # 确保目录存在
        os.makedirs(CHAT_DOCUMENT_DIR, exist_ok=True)

        # 遍历所有JSON文件
        for filename in os.listdir(CHAT_DOCUMENT_DIR):
            if filename.endswith(".json"):
                file_path = os.path.join(CHAT_DOCUMENT_DIR, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        # 提取基本信息用于列表显示
                        session_id = next(iter(data["chat_sessions"].keys()))
                        session = data["chat_sessions"][session_id]
                        saved_chats.append({
                            "filename": filename,
                            "id": session_id,
                            "title": session.get("title", "无标题对话"),
                            "lastMessage": session.get("lastMessage", "无消息"),
                            "created_at": os.path.getctime(file_path)
                        })
                except Exception as e:
                    logger.error(f"解析文件 {filename} 失败: {str(e)}")

        # 按创建时间倒序排序
        saved_chats.sort(key=lambda x: x["created_at"], reverse=True)
        return JSONResponse(content=saved_chats)

    except Exception as e:
        logger.error(f"获取已保存对话失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取已保存对话失败: {str(e)}"
        )

# 新增API：加载特定对话文件
@router.get("/load-chat/{filename}")
async def load_chat(filename: str):
    try:
        # 防止路径遍历攻击
        if ".." in filename or "/" in filename:
            raise ValueError("无效文件名")

        file_path = os.path.join(CHAT_DOCUMENT_DIR, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError("文件不存在")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return JSONResponse(content=data)

    except Exception as e:
        logger.error(f"加载对话文件失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"加载对话失败: {str(e)}"
        )

# 在已有API端点后添加
@router.get("/all-chats")
async def get_all_chats():
    return JSONResponse(content=global_chat_history)




@router.post("/save-session")
async def save_session(request: SaveSessionRequest):
    """保存单个对话会话到本地文件"""
    try:
        session_id = request.sessionId
        session_data = request.session
        
        # 确保目录存在
        os.makedirs(CHAT_DOCUMENT_DIR, exist_ok=True)
        
        # 生成文件名：单个会话使用sessionId作为文件名
        filename = f"session_{session_id}.json"
        file_path = os.path.join(CHAT_DOCUMENT_DIR, filename)
        
        # 构造保存的数据结构（保持与现有格式一致）
        save_data = {
            "chat_sessions": {
                session_id: session_data
            }
        }
        
        # 检查文件是否已存在，如果存在则更新
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                # 更新现有会话数据
                existing_data["chat_sessions"][session_id] = session_data
                save_data = existing_data
            except Exception as e:
                logger.warning(f"读取现有文件失败，将创建新文件: {str(e)}")
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        # 同步更新全局内存缓存
        global_chat_history[session_id] = session_data
        
        logger.info(f"会话 {session_id} 保存成功到文件: {filename}")
        return JSONResponse(content={
            "status": "success",
            "message": f"会话 {session_id} 保存成功",
            "filename": filename
        })
        
    except Exception as e:
        logger.error(f"保存会话失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"保存会话失败: {str(e)}"
        )
