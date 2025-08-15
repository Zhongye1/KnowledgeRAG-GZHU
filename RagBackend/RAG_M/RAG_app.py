from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv
import json
import asyncio

from fastapi.responses import StreamingResponse
import io
import contextlib


# 导入RAG_M原有的核心组件
import sys
project_root = str(Path(__file__).parent)
sys.path.append(project_root)

from src.rag.rag_pipeline import RAGPipeline
from src.vectorstore.vector_store import VectorStoreManager

load_dotenv()

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    docs_dir: str = None  # 可选的文件夹路径

class IngestRequest(BaseModel):
    docs_dir: str
    



@contextlib.contextmanager
def capture_stdout():
    stdout_buffer = io.StringIO()
    original_stdout = sys.stdout
    
    # 创建一个双重输出的类
    class DualOutput:
        def __init__(self, original, buffer):
            self.original = original
            self.buffer = buffer
            
        def write(self, text):
            self.original.write(text)
            self.buffer.write(text)
            
        def flush(self):
            self.original.flush()
            self.buffer.flush()
    
    sys.stdout = DualOutput(original_stdout, stdout_buffer)
    try:
        yield stdout_buffer
    finally:
        sys.stdout = original_stdout



@lru_cache()
def get_rag_pipeline(vectorstore_path: str = None):
    """初始化RAG管道"""
    # 使用传入的路径或环境变量中的路径
    vectorstore_path = vectorstore_path or os.getenv("VECTORSTORE_PATH")
    if not vectorstore_path:
        raise ValueError("Vector store path not provided and VECTORSTORE_PATH not set in environment")
    
    vector_store_manager = VectorStoreManager()
    vectorstore = vector_store_manager.load_vectorstore(
        vectorstore_path,
        trust_source=True
    )
    print(f"初始化RAG管道，使用模型: {os.getenv('MODEL')}，向量存储路径: {vectorstore_path}")
    return RAGPipeline(os.getenv("MODEL"), vectorstore)



@router.post("/RAG_query")
async def process_query(query_body: QueryRequest):
    """RAG智能查询接口 - 支持指定文件夹路径进行查询，以流式方式返回结果"""
    
    async def generate():
        try:
            yield f"data: 开始处理查询: {query_body.query}\n\n"
            
            # 统一使用一个VectorStoreManager实例
            vector_store_manager = VectorStoreManager(docs_dir=query_body.docs_dir)
            
            # 确定向量存储路径
            if query_body.docs_dir:
                vectorstore_path = os.path.join(query_body.docs_dir, "vectorstore")
                yield f"data: 使用自定义向量存储路径: {vectorstore_path}\n\n"
                
                if not os.path.exists(vectorstore_path):
                    error_msg = f"向量存储路径不存在: {vectorstore_path}"
                    yield f"data: ERROR: {error_msg}\n\n"
                    raise HTTPException(status_code=404, detail=f"Vector store not found at {vectorstore_path}")
                
                yield "data: 正在加载向量存储...\n\n"
                vectorstore = vector_store_manager.load_vectorstore(
                    vectorstore_path,
                    trust_source=True
                )
                yield "data: 向量存储加载完成\n\n"
            else:
                yield "data: 使用默认向量存储\n\n"
                vectorstore_path = os.getenv("VECTORSTORE_PATH")
                vectorstore = vector_store_manager.load_vectorstore(
                    vectorstore_path,
                    trust_source=True
                )
                yield "data: 默认向量存储加载完成\n\n"
            
            # 初始化RAG管道
            yield "data: 初始化RAG管道...\n\n"
            rag = RAGPipeline(os.getenv("MODEL"), vectorstore)
            yield "data: RAG管道初始化完成\n\n"
            
            # 处理查询
            yield "data: 开始处理查询...\n\n"
            
            # 获取相关文档
            yield "data: 正在检索相关文档...\n\n"
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            docs = retriever.get_relevant_documents(query_body.query)
            yield f"data: 找到 {len(docs)} 个相关文档\n\n"
            
            # 处理查询并获取结果
            result = rag.process_query(query_body.query)
            
            # 分段返回回答内容
            # 假设我们要按段落分割
            paragraphs = result["answer"].split('\n\n')
            
            yield "data: 正在生成回答...\n\n"
            for paragraph in paragraphs:
                if paragraph.strip():
                    yield f"data: {paragraph.strip()}\n\n"
                    # 可选：添加短暂延迟以模拟流式输出效果
                    await asyncio.sleep(0.1)
            
            # 返回来源信息
            yield "data: 参考来源:\n\n"
            for i, source in enumerate(result["sources"], 1):
                # 修复: 检查键是否存在，或使用更安全的方式访问数据
                if 'source' in source:
                    yield f"data: {i}. {source['source']}\n\n"
                else:
                    # 如果没有source键，尝试使用其他可能的键或显示所有元数据
                    source_text = source.get('path', source.get('file_path', str(source)))
                    yield f"data: {i}. {source_text}\n\n"
            
            # 发送完整结果作为JSON以便客户端可以获取结构化数据
            final_result = {
                "answer": result["answer"],
                "sources": result["sources"],
                "vectorstore_path": vectorstore_path
            }
            yield f"data: COMPLETE: {json.dumps(final_result, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = f"查询处理失败: {str(e)}\n{error_trace}"
            yield f"data: ERROR: {error_msg}\n\n"
            print(f"[ERROR] {error_msg}")
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )



@router.post("/ingest")
async def ingest_documents(ingest_body: IngestRequest):
    """文档导入接口 - 替代原来的ingest_documents.py功能"""
    def generate():
        with capture_stdout() as stdout_buffer:
            print(f"Starting document ingestion from directory: {ingest_body.docs_dir}")
            try:
                from src.ingestion.document_loader import DocumentLoader
                from src.vectorstore.vector_store import VectorStoreManager
                
                # 使用知识库目录中的配置
                vector_store_manager = VectorStoreManager(docs_dir=ingest_body.docs_dir)
                documents = []

                # 动态确定向量存储路径
                vectorstore_path = ingest_body.docs_dir + "/vectorstore"
                print(f"Using vector store path: {vectorstore_path}")
                yield f"data: Using vector store path: {vectorstore_path}\n\n"
                
                # 检查目录是否存在
                if not os.path.exists(ingest_body.docs_dir):
                    print(f"Directory does not exist: {ingest_body.docs_dir}")
                    yield f"data: Directory does not exist: {ingest_body.docs_dir}\n\n"
                    raise ValueError(f"Directory does not exist: {ingest_body.docs_dir}")
                
                # 初始化加载器和向量存储管理器
                print("Initializing DocumentLoader")
                yield "data: Initializing DocumentLoader\n\n"
                #loader = DocumentLoader()
                loader = DocumentLoader(docs_dir=ingest_body.docs_dir)
                #vector_store_manager = VectorStoreManager() #删除默认项
                documents = []
                
                # 统计信息
                processed_count = 0
                skipped_count = 0
                error_count = 0
                
                # 首先遍历并处理所有文件
                print("Walking through directory to process files")
                yield "data: Walking through directory to process files\n\n"
                
                for root, dirs, files in os.walk(ingest_body.docs_dir):
                    
                    # 🔧 新增：在遍历前过滤掉需要忽略的目录
                    dirs[:] = [d for d in dirs if d not in loader.IGNORED_DIRECTORIES]
                    
                    # 跳过已经是vectorstore目录的情况
                    if 'vectorstore' in os.path.basename(root):
                        print(f"Skipping vectorstore directory: {root}")
                        yield f"data: Skipping vectorstore directory: {root}\n\n"
                        continue
                    
                    
                    
                    print(f"Found {len(files)} files in {root}")
                    yield f"data: Found {len(files)} files in {root}\n\n"
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        try:
                            # 🔧 新增：检查是否应该跳过文件
                            should_skip, skip_reason = loader.should_skip_file(file_path)
                            if should_skip:
                                print(f"Skipping file: {file} ({skip_reason})")
                                yield f"data: Skipping file: {file} ({skip_reason})\n\n"
                                skipped_count += 1
                                continue
                            
                            print(f"Processing file: {file_path}")
                            yield f"data: Processing file: {file_path}\n\n"
                            
                            docs = loader.load_document(file_path)
                            print(f"Successfully loaded {len(docs)} document chunks from {file_path}")
                            yield f"data: Successfully loaded {len(docs)} document chunks from {file_path}\n\n"
                            documents.extend(docs)
                            processed_count += 1
                            
                        except ValueError as ve:
                            # 处理跳过文件的情况（由load_document内部抛出）
                            if "Skipped file" in str(ve):
                                print(f"Skipping file: {file} ({str(ve)})")
                                yield f"data: Skipping file: {file} ({str(ve)})\n\n"
                                skipped_count += 1
                            else:
                                print(f"Unsupported file type {file_path}: {str(ve)}")
                                yield f"data: Unsupported file type {file_path}: {str(ve)}\n\n"
                                error_count += 1
                            continue
                        except Exception as e:
                            print(f"Error processing {file_path}: {str(e)}")
                            yield f"data: Error processing {file_path}: {str(e)}\n\n"
                            error_count += 1
                            continue
                
                # 🔧 新增：输出处理统计
                print(f"Processing summary: {processed_count} processed, {skipped_count} skipped, {error_count} errors")
                yield f"data: Processing summary: {processed_count} processed, {skipped_count} skipped, {error_count} errors\n\n"
                
                # 检查是否有文档被成功处理
                if not documents:
                    print("No documents were processed successfully")
                    yield "data: No documents were processed successfully\n\n"
                    raise ValueError("No documents were processed successfully")
                
                # 所有文档处理完成后，创建向量存储
                print(f"Creating vector store with {len(documents)} document chunks")
                yield f"data: Creating vector store with {len(documents)} document chunks\n\n"
                vector_store_manager.create_vectorstore(
                    documents,
                    vectorstore_path
                )
                print(f"Vector store successfully created and saved to {vectorstore_path}")
                yield f"data: Vector store successfully created and saved to {vectorstore_path}\n\n"
                
                # 发送最终结果
                result = {
                    "message": f"Successfully ingested {len(documents)} document chunks",
                    "documents_count": len(documents),
                    "vectorstore_path": vectorstore_path,
                    "stats": {
                        "processed": processed_count,
                        "skipped": skipped_count,
                        "errors": error_count
                    }
                }
                print(f"Successfully ingested {len(documents)} document chunks")
                yield f"data: {json.dumps(result)}\n\n"
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                error_msg = f"Document ingestion failed: {str(e)}\n{error_trace}"
                print(f"ERROR: {error_msg}")
                yield f"data: ERROR: {error_msg}\n\n"
                raise HTTPException(status_code=500, detail=error_msg)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )





@router.post("/init")
async def init_project():
    """项目初始化接口 - 替代原来的setup.py功能"""
    try:
        # 导入初始化逻辑
        from src.scripts.init_project import init_project as init_func
        
        init_func()
        return {"message": "Project initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project initialization failed: {str(e)}")

@router.get("/health")
async def rag_health_check():
    """RAG服务健康检查"""
    try:
        # 简单检查关键组件是否可用
        model = os.getenv("MODEL")
        vectorstore_path = os.getenv("VECTORSTORE_PATH")
        
        return {
            "status": "healthy", 
            "service": "RAG Query Service",
            "model": model,
            "vectorstore_path": vectorstore_path,
            "vectorstore_exists": os.path.exists(vectorstore_path) if vectorstore_path else False
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
