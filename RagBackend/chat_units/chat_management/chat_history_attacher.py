import os
import json
import logging
from fastapi import FastAPI, HTTPException, APIRouter
from pathlib import Path

# 创建路由
router = APIRouter()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHAT_DOCUMENT_DIR = "chat_units/chat_documents"  # 统一存储目录

# 获取所有对话历史文件
@router.get("/chat-documents")
async def get_chat_documents():
    """获取所有保存的对话会话列表"""
    try:
        chat_dir = Path(CHAT_DOCUMENT_DIR)
        logger.info(f"扫描对话目录: {chat_dir.absolute()}")
        
        if not chat_dir.exists():
            logger.warning(f"对话目录不存在: {chat_dir}")
            return []
        
        documents = []
        for file_path in chat_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions = data.get("chat_sessions", {})
                    
                    for session_id, session_data in sessions.items():
                        documents.append({
                            "id": session_id,
                            "title": session_data.get("title", "未命名对话"),
                            "lastMessage": session_data.get("lastMessage", ""),
                            "history": session_data.get("history", []),
                            "filename": file_path.name,
                            "created_at": os.path.getctime(file_path)  # 添加创建时间
                        })
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败 {file_path}: {str(e)}")
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {str(e)}")
        
        # 按创建时间倒序排序
        documents.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return documents
        
    except Exception as e:
        logger.error(f"获取对话历史失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取对话历史失败: {str(e)}"
        )

# 获取单个对话历史
@router.get("/chat-document/{session_id}")
async def get_chat_document(session_id: str):
    """根据会话ID获取单个对话详情"""
    try:
        chat_dir = Path(CHAT_DOCUMENT_DIR)  # 🔧 修复：使用统一目录
        
        if not chat_dir.exists():
            raise HTTPException(status_code=404, detail="对话目录不存在")
            
        for file_path in chat_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if session_id in data.get("chat_sessions", {}):
                        logger.info(f"找到会话 {session_id} 在文件: {file_path.name}")
                        return data["chat_sessions"][session_id]
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败 {file_path}: {str(e)}")
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {str(e)}")
        
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 未找到")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取对话详情失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取对话详情失败: {str(e)}"
        )

"""更新指定会话的对话数据
# 更新对话历史
@router.post("/update-chat-document")
async def update_chat_document(data: dict):
    
    try:
        session_id = data.get("id")
        if not session_id:
            raise HTTPException(status_code=400, detail="缺少会话ID")
        
        chat_dir = Path(CHAT_DOCUMENT_DIR)  # 🔧 修复：使用统一目录
        
        if not chat_dir.exists():
            raise HTTPException(status_code=404, detail="对话目录不存在")
            
        for file_path in chat_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    document = json.load(f)
                    
                if session_id in document.get("chat_sessions", {}):
                    # 更新会话数据
                    document["chat_sessions"][session_id] = data
                    
                    # 写回文件
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(document, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"成功更新会话 {session_id} 在文件: {file_path.name}")
                    return {"status": "success", "message": f"会话 {session_id} 更新成功"}
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败 {file_path}: {str(e)}")
            except Exception as e:
                logger.error(f"更新文件失败 {file_path}: {str(e)}")
        
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 未找到")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新对话历史失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"更新对话历史失败: {str(e)}"
        )

        
"""