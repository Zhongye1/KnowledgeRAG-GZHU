# start_project.py
import subprocess
import os
import signal
import sys
from threading import Thread
import time


def start_backend():
    """启动后端服务"""
    backend_path = os.path.join(os.path.dirname(__file__), "RagBackend")
    os.chdir(backend_path)

    # 使用 uvicorn 启动后端
    process = subprocess.Popen(
        [
            "python",
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
        ]
    )
    return process


def start_frontend():
    """启动前端服务"""
    frontend_path = os.path.join(os.path.dirname(__file__), "RagFrontend")
    os.chdir(frontend_path)

    # 确保已安装依赖
    subprocess.run(["pnpm", "install"], cwd=frontend_path, shell=True)

    # 启动前端开发服务器
    process = subprocess.Popen(["pnpm", "run", "dev"], cwd=frontend_path, shell=True)
    return process


def start_database():
    """启动数据库服务（使用Docker）"""
    root_path = os.path.dirname(__file__)
    os.chdir(root_path)

    # 启动MySQL服务
    process = subprocess.Popen(["docker", "compose", "up", "-d", "db"], cwd=root_path)
    return process


def main():
    print("=== KnowledgeRAG 项目启动 ===")

    # 检查必要组件
    try:
        subprocess.check_output(["docker", "version"], stderr=subprocess.STDOUT)
        print("[✓] Docker 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[✗] Docker 未安装或未启动，请先安装并启动 Docker")
        return

    try:
        subprocess.check_output(["python", "--version"], stderr=subprocess.STDOUT)
        print("[✓] Python 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[✗] Python 未安装，请先安装 Python")
        return

    try:
        # 改进 pnpm 检测方式，使用 shell=True 以支持 Windows 系统
        result = subprocess.run(["pnpm", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode == 0:
            print(f"[✓] pnpm 已安装 (版本 {result.stdout.strip()})")
        else:
            print("[✗] pnpm 未安装，请先安装 Node.js 和 pnpm")
            return
    except FileNotFoundError:
        print("[✗] pnpm 未安装，请先安装 Node.js 和 pnpm")
        return

    print("\n[1/3] 启动数据库服务...")
    db_process = start_database()

    print("[2/3] 启动后端服务...")
    backend_process = start_backend()

    print("[3/3] 启动前端服务...")
    frontend_process = start_frontend()

    print("\n=== 所有服务已启动 ===")
    print("后端 API: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("前端界面: http://localhost:5173 或 http://localhost:5174")
    print("\n按 Ctrl+C 停止所有服务")

    try:
        # 等待中断信号
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")

        # 终止进程
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        if db_process:
            db_process.terminate()

        print("服务已停止")


if __name__ == "__main__":
    main()
