
from fastapi import APIRouter, HTTPException, Form

import pymysql
import jwt
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置 - 从环境变量中读取
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '172.22.121.2'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Www028820'),
    'database': os.getenv('DB_NAME', 'mysql'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

def get_db_connection():
    """
    获取数据库连接
    """
    return pymysql.connect(**DB_CONFIG)


@router.get("/api/GetUserData")
async def get_user_data(token: str = Depends(oauth2_scheme)):
    """
    获取用户数据
    """
    print("token:", token)
    try:
        # 验证JWT
        decoded_token = jwt.decode(token, "secret", algorithms=["HS256"])
        email = decoded_token["sub"]
        # 获取用户数据
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询用户ID
        cursor.execute("SELECT id FROM user WHERE email=%s", (email,))
        user_result = cursor.fetchone()
        if not user_result:
            return {"status": "error", "message": "用户不存在"}
        
        user_id = user_result[0]
        
        # 查询用户资料
        cursor.execute("SELECT user_id, name, signature, avatar FROM user_profile WHERE user_id=%s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return {"status": "success", "data": user_data}
        else:
            return {"status": "error", "message": "用户资料不存在"}
    except Exception as e:
        print(f"获取用户数据出错: {e}")
        raise HTTPException(
            status_code=401,
            detail="错误"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@router.post("/api/UpdateUserData")
async def update_user_data(token: str = Depends(oauth2_scheme),name: str = Form(...), signatur: str = Form(...), avatar: str = Form(...)):
    """
    更新用户数据
    """
    try:
        # 验证JWT
        decoded_token = jwt.decode(token, "secret", algorithms=["HS256"])
        email = decoded_token["sub"]
        # 更新用户数据
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user_profile SET name=%s, signature=%s, avatar=%s WHERE user_id=(SELECT id FROM user WHERE email=%s)", (name, signatur, avatar, email))
        conn.commit()
        if cursor.rowcount > 0:
            return {"status": "success", "message": "更新成功"}
        else:
            return {"status": "error", "message": "用户不存在或更新失败"}
    except Exception as e:
        print(f"更新用户数据出错: {e}")
        raise HTTPException(
            status_code=401,
            detail="更新失败"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.delete("/api/DeleteUserData")
async def delete_user_data(token: str = Depends(oauth2_scheme)):
    try:
        # 验证JWT
        decoded_token = jwt.decode(token, "secret", algorithms=["HS256"])
        email = decoded_token["sub"]
        conn = get_db_connection()
        cursor = conn.cursor()

        # 删除用户（会自动级联删除用户资料）
        cursor.execute("DELETE FROM user WHERE email=%s", (email,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"用户 {email} 及其资料已删除")
            return {"status": "success", "message": "用户删除成功"}
        else:
            print(f"用户 {email} 不存在")
            return {"status": "error", "message": "用户不存在"}
    except Exception as e:
        print(f"删除失败: {e}")
        raise HTTPException(
            status_code=401,
            detail="删除失败"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 拿到user.db所有的数据
@router.get("/api/GetUserAllData")
async def get_user_all_data():
    """
    获取所有用户数据
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, created_at FROM user")
    user_data = cursor.fetchall()
    cursor.close()
    conn.close()
    if not user_data:
        raise HTTPException(
            status_code=400,
            detail="数据为空"
        )
    print("用户数据为：", user_data)
    return {"status": "success", "data": user_data}
