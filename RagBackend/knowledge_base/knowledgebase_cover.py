from fastapi import UploadFile, File, APIRouter, HTTPException , Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import os
import uuid
from pydantic import BaseModel
from datetime import datetime
import aiofiles
from pathlib import Path


router = APIRouter()


"""
知识库封面图床

"""

UPLOAD_DIR = Path("local-KLB-files")  # 使用与其他上传相同的根目录

@router.post("/api/upload-cover")
async def upload_cover_image(image: UploadFile = File(...) , KLB_id = Form(...)):
    """
    上传知识库封面图片
    """
    try:
        # 创建保存图片的目录
        cover_upload_dir = os.path.join(UPLOAD_DIR, "covers")
        os.makedirs(cover_upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = os.path.splitext(image.filename)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"cover_{timestamp}_{uuid.uuid4().hex[:8]}{file_ext}"
        image_path = os.path.join(cover_upload_dir, unique_filename)
        
        # 保存上传的图片
        async with aiofiles.open(image_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        # 构建可访问的URL路径
        # 现在这个后端有一个静态文件服务配置，可以通过/static/covers/访问
        image_url = f"/static/covers/{unique_filename}"

        # 将图片路径保存到配置的json中
        base_url = "http://localhost:8000"
        alter_img_url = f"{base_url}/static/covers/{unique_filename}"
        
        # 将图片路径保存到配置的json中
        kb_dir = os.path.join(UPLOAD_DIR, KLB_id)
        json_file_path = os.path.join(kb_dir, 'knowledge_data.json')
        
        # 检查知识库目录和配置文件是否存在
        if not os.path.exists(json_file_path):
            raise HTTPException(status_code=404, detail=f"知识库 '{KLB_id}' 配置文件不存在")
        
        # 读取现有配置
        import json
        with open(json_file_path, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        # 更新封面图片URL
        kb_data['cover'] = alter_img_url
        
        # 保存更新后的配置
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, ensure_ascii=False, indent=4)
        
        return {
            "success": True,
            "message": "封面图片上传成功",
            "imageUrl": image_url
        }
    except Exception as e:
        print(f"封面图片上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"封面图片上传失败: {str(e)}")