// API 配置文件，集中管理所有 API 端点
// 避免硬编码 URL，便于统一管理和修改

// 基础 URL 后端服务的api
const BASE_URL = 'http://localhost:8000';

// API 端点配置
export const API_ENDPOINTS = {
  // 基础 URL
  BASE_URL,

  // 用户相关
  USER: {
    AVATAR: (avatarPath: string) => `${BASE_URL}${avatarPath}`
  },

  // 文件管理相关
  FILES: {
    ALL_DOCUMENTS: `${BASE_URL}/api/files/api/all-documents/`,
    DOCUMENT_PREVIEW: (filePath: string) => `${BASE_URL}/api/files/api/document/preview/?file_path=${encodeURIComponent(filePath)}`,
    DELETE_DOCUMENT: (filePath: string) => `${BASE_URL}/api/files/api/document/?file_path=${encodeURIComponent(filePath)}`
  },

  // 知识库相关
  KNOWLEDGE: {
    GET_ITEM: (id: string) => `${BASE_URL}/api/get-knowledge-item/${id}/`,
    DOCUMENTS_LIST: (id: string) => `${BASE_URL}/api/documents-list/${id}/`,
    INGEST: `${BASE_URL}/api/RAG/ingest`,
    QUERY: `${BASE_URL}/api/RAG/RAG_query`
  },

  // 知识图谱相关
  KNOWLEDGE_GRAPH: {
    PROCESS_ALL_FILES: `${BASE_URL}/api/kg/process-all-files`,
    PROCESS_KNOWLEDGE_BASE: `${BASE_URL}/api/kg/process-knowledge-base`
  },

  // Ollama 模型相关
  OLLAMA: {
    MODELS: `${BASE_URL}/api/ollama-models`,
    BASE: 'http://localhost:11434', // 默认Ollama服务器地址
    TAGS: '/api/tags',
    DELETE: '/api/delete',
    PULL: '/api/pull',
    COPY: '/api/copy'
  },

  // 聊天相关
  CHAT: {
    BASE: `${BASE_URL}/api/chat`,
    SEND_MESSAGE: `${BASE_URL}/api/chat/send-message`,
    SESSIONS: `${BASE_URL}/api/chat/chat-documents`,
    SAVE_SESSION: `${BASE_URL}/api/chat/save-session`,
    DELETE_SESSION: `${BASE_URL}/api/chat/delete-session`,
    DOWNLOAD_CHAT: `${BASE_URL}/api/chat/download-chat-json`

  },

};

export default API_ENDPOINTS;


