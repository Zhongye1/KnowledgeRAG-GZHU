from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama.llms import OllamaLLM
#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from models.model_config import get_model_config


class RAGPipeline:
    def __init__(self, llm_model: str = None, vectorstore: FAISS = None):
        # 如果没有提供模型名称，则从统一配置中获取
        if llm_model is None:
            model_config = get_model_config()
            llm_model = model_config.llm_model
            print(f"==================Using default LLM model: {llm_model}")
            
        self.llm = OllamaLLM(model=llm_model)
        self.vectorstore = vectorstore
        self.qa_chain = self._create_qa_chain()

    def _create_qa_chain(self):
        """Create the retrieval QA chain with custom prompt"""
        prompt_template = """你是知识管理助手，专门回答基于文档的技术问题。

    规则：
    1. 基于提供的上下文回答
    2. 如果信息不足，说现有文档没有提及信息不足的这一块内容，然后给出自己知道的一些信息，说供参考
    3. 回答时引用相关文档片段
    4. 用户没有声明回答所用的语言时用中文回答，否则用所声明语言回答
    5. 快速而准确的回答是关键，且回答尽量完整
    6. 如果用户问题中包含代码片段，尽量提供相关代码示例
    7. 如果用户问题中包含公式，尽量提供相关公式示例
    8. 如果用户问题中包含表格，尽量提供相关表格示例
    9. 与上下文无关的提问，指出其与上下文无关，并提供从别处了解的相关信息

    上下文信息：
    {context}

    用户问题：{question}

    回答："""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # 创建检索器
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3, "fetch_k": 5}
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": PROMPT,
                "verbose": True
            }
        )


    def process_query(self, query: str) -> dict:
        """
        Process a query through the RAG pipeline
        
        Returns:
            dict: Contains response text and source documents
        """
        try:
            result = self.qa_chain({"query": query})
            return {
                "answer": result["result"],
                "sources": [doc.metadata for doc in result["source_documents"]]
            }
        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}") 