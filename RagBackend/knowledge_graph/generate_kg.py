# generate_kg.py
import logging
import os
import requests
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import re
from langchain_community.document_loaders import PyPDFLoader
from docx import Document

router = APIRouter()

# 修改导入语句，使用正确的绝对导入
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.model_config import get_model_config


# Constants
OLLAMA_API_URL = "http://localhost:11434/api/generate"
model_config = get_model_config()
OLLAMA_MODEL = model_config.kg_model
CHUNK_SIZE = 5000
PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, "test")


class ProcessFileRequest(BaseModel):
    filename: str

class ProcessFilesResponse(BaseModel):
    message: str
    graph_data: dict

# Split text into chunks
def split_text_into_chunks(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Extract text from PDF
def extract_pdf_text(file_path):
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text = "\n".join([doc.page_content for doc in documents])
        return text
    except Exception as e:
        print(f"Unable to extract PDF file {file_path}: {e}")
        return ""

# Extract text from DOC/DOCX
def extract_doc_text(file_path):
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Unable to extract DOC file {file_path}: {e}")
        return ""

# Extract text from text files
def extract_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Unable to read file {file_path}: {e}")
        return ""

# Extract text based on file type
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_pdf_text(file_path)
    elif ext in ['.doc', '.docx']:
        return extract_doc_text(file_path)
    elif ext in ['.txt', '.md']:
        return extract_text_file(file_path)
    else:
        print(f"Unsupported file type: {ext}")
        return ""

# Extract graph data using Ollama API
def extract_graph_data(chunk):
    prompt = f"""
你是一个知识图谱构建专家，请从以下文本中提取实体和关系，并以指定的JSON格式输出。

任务要求：
1. 提取文本中的实体（如人物、地点、组织、事件等）作为节点
2. 提取实体之间的关系作为边
3. 所有输出内容必须使用中文
4. 输出尽可能快速，详细和复杂，确保每个实体和关系都被正确识别
5. 要求关系之间互相联系，形成一个图

输出格式要求：
请严格按照以下JSON格式输出，包含"nodes"和"edges"两个字段：
- nodes: 包含对象的数组，每个对象有"id"（唯一标识符）和"label"（实体名称）
- edges: 包含对象的数组，每个对象有"source"（源节点id）、"target"（目标节点id）和"label"（关系描述）

示例输出格式：
{{
  "nodes": [{{"id": "entity1", "label": "实体1"}}, {{"id": "entity2", "label": "实体2"}}],
  "edges": [{{"source": "entity1", "target": "entity2", "label": "提及"}}]
}}

请处理以下文本：
{chunk}
"""
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False  # Ensure full response is returned
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=data, timeout=300)
        print(f"API request status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            print(f"API response: {generated_text[:100]}...")  # Print first 100 characters

            # Attempt to extract JSON from the response using regex
            json_pattern = r'(\{.*\})'
            match = re.search(json_pattern, generated_text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                try:
                    parsed_json = json.loads(json_str)
                    if "nodes" in parsed_json and "edges" in parsed_json:
                        return parsed_json
                    else:
                        print("Warning: JSON does not contain 'nodes' and 'edges' keys.")
                        return {"nodes": [], "edges": []}
                except json.JSONDecodeError:
                    print(f"Failed to parse extracted JSON: {json_str[:50]}...")
                    return {"nodes": [], "edges": []}
            else:
                print("No JSON object found in the response.")
                return {"nodes": [], "edges": []}
        else:
            print(f"API request failed, status code: {response.status_code}")
            return {"nodes": [], "edges": []}
    except Exception as e:
        print(f"API call error: {str(e)}")
        return {"nodes": [], "edges": []}

@router.post("/process-file", response_model=ProcessFilesResponse)
async def process_single_file(request: ProcessFileRequest):
    """
    处理单个文件并生成知识图谱数据
    """
    file_path = os.path.join(KNOWLEDGE_BASE_PATH, request.filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {request.filename} not found")
    
    # Extract text
    content = extract_text(file_path)
    if not content:
        raise HTTPException(status_code=400, detail=f"Unable to extract content from {request.filename}")
    
    # Split into chunks
    chunks = split_text_into_chunks(content, CHUNK_SIZE)
    
    # Extract graph data
    graph_data = {"nodes": [], "edges": []}
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}")
        result = extract_graph_data(chunk)
        if result and "nodes" in result and "edges" in result:
            graph_data["nodes"].extend(result["nodes"])
            graph_data["edges"].extend(result["edges"])
        else:
            print(f"Failed to extract valid graph data for chunk {i+1}")
    
    return ProcessFilesResponse(
        message=f"Successfully processed {request.filename}",
        graph_data=graph_data
    )


@router.post("/process-all-files", response_model=List[ProcessFilesResponse])
async def process_all_files():
    """
    处理所有文件并生成知识图谱数据
    """
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        raise HTTPException(status_code=404, detail=f"Directory {KNOWLEDGE_BASE_PATH} does not exist")
    
    files = [f for f in os.listdir(KNOWLEDGE_BASE_PATH) if os.path.isfile(os.path.join(KNOWLEDGE_BASE_PATH, f))]
    
    results = []
    for file in files:
        try:
            file_path = os.path.join(KNOWLEDGE_BASE_PATH, file)
            print(f"Processing file: {file}")
            
            # Extract text
            content = extract_text(file_path)
            if not content:
                print(f"Skipping file {file}, unable to extract content")
                continue
            
            # Split into chunks
            chunks = split_text_into_chunks(content, CHUNK_SIZE)
            
            # Extract graph data
            graph_data = {"nodes": [], "edges": []}
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                result = extract_graph_data(chunk)
                if result and "nodes" in result and "edges" in result:
                    graph_data["nodes"].extend(result["nodes"])
                    graph_data["edges"].extend(result["edges"])
                else:
                    print(f"Failed to extract valid graph data for chunk {i+1}")
            
            results.append(ProcessFilesResponse(
                message=f"Successfully processed {file}",
                graph_data=graph_data
            ))
            
            # Save cumulative graph data
            output_file = os.path.join(KNOWLEDGE_BASE_PATH, f"{os.path.splitext(file)[0]}_graph.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=4, ensure_ascii=False)
            print(f"Graph data saved to {output_file}")
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
            results.append(ProcessFilesResponse(
                message=f"Error processing {file}: {str(e)}",
                graph_data={"nodes": [], "edges": []}
            ))
    
    return results

@router.get("/get-graph-data/{filename}")
async def get_graph_data(filename: str):
    """
    获取特定文件的知识图谱数据
    """
    # Remove extension if present in filename
    name_without_ext = os.path.splitext(filename)[0]
    graph_filename = f"{name_without_ext}_graph.json"
    file_path = os.path.join(KNOWLEDGE_BASE_PATH, graph_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Graph data for {filename} not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading graph data: {str(e)}")
    



######################################################################
#新增，处理知识库文件夹生成图谱


class ProcessFolderRequest(BaseModel):
    folder_path: str


@router.post("/process-knowledge-base", response_model=List[ProcessFilesResponse])
async def process_knowledge_base(request: ProcessFolderRequest):
    """
    处理指定知识库ID下的所有文档文件并生成知识图谱数据
    """
    # 构建知识库文件夹路径 - 使用与系统其他部分一致的路径
    kb_folder_path = os.path.join("local-KLB-files", request.folder_path)
    
    if not os.path.exists(kb_folder_path):
        raise HTTPException(status_code=404, detail=f"Knowledge base directory {request.folder_path} does not exist")
    
    if not os.path.isdir(kb_folder_path):
        raise HTTPException(status_code=400, detail=f"{kb_folder_path} is not a directory")
    
    # 获取文件夹中所有支持的文件类型
    supported_extensions = ['.pdf', '.doc', '.docx', '.txt', '.md']
    files = [f for f in os.listdir(kb_folder_path) 
             if os.path.isfile(os.path.join(kb_folder_path, f)) 
             and os.path.splitext(f)[1].lower() in supported_extensions]
    
    if not files:
        return JSONResponse(
            content={"message": f"No supported files found in knowledge base {request.folder_path}"},
            status_code=200
        )
    
    results = []
    for file in files:
        try:
            file_path = os.path.join(kb_folder_path, file)
            print(f"Processing file: {file}")
            
            # 提取文本
            content = extract_text(file_path)
            if not content:
                print(f"Skipping file {file}, unable to extract content")
                continue
            
            # 分块处理
            chunks = split_text_into_chunks(content, CHUNK_SIZE)
            
            # 提取图谱数据
            graph_data = {"nodes": [], "edges": []}
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                result = extract_graph_data(chunk)
                if result and "nodes" in result and "edges" in result:
                    graph_data["nodes"].extend(result["nodes"])
                    graph_data["edges"].extend(result["edges"])
                else:
                    print(f"Failed to extract valid graph data for chunk {i+1}")
            
            # 添加到结果列表
            results.append(ProcessFilesResponse(
                message=f"Successfully processed {file}",
                graph_data=graph_data
            ))
            
            # 保存生成的知识图谱数据
            output_file = os.path.join(kb_folder_path, f"{os.path.splitext(file)[0]}_graph.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=4, ensure_ascii=False)
            print(f"Graph data saved to {output_file}")
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
            results.append(ProcessFilesResponse(
                message=f"Error processing {file}: {str(e)}",
                graph_data={"nodes": [], "edges": []}
            ))
    
    return results





@router.get("/get-kb-graph-data/{kb_id}/{filename}")
async def get_kb_graph_data(kb_id: str, filename: str):
    """
    获取特定知识库中特定文件的知识图谱数据
    """
    # 构建知识库文件夹路径
    kb_folder_path = os.path.join("local-KLB-files", kb_id)
    
    if not os.path.exists(kb_folder_path):
        raise HTTPException(status_code=404, detail=f"Knowledge base directory {kb_id} not found")
    
    # 移除文件名中的扩展名（如果存在）
    name_without_ext = os.path.splitext(filename)[0]
    graph_filename = f"{name_without_ext}_graph.json"
    file_path = os.path.join(kb_folder_path, graph_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Graph data for {filename} in knowledge base {kb_id} not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading graph data: {str(e)}")
