import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from .config import settings

class RAGManager:
    def __init__(self, documents_path: str = "../data/documents"):
        self.documents_path = documents_path
        
        # 构建 Embeddings 配置
        embeddings_config = {
            "api_key": settings.openai_api_key,
            "model": settings.embedding_model
        }

        # 如果配置了自定义 base_url，则添加
        if settings.openai_api_base:
            base_url = settings.openai_api_base
            # 确保 base_url 以 /v1 结尾
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'
            embeddings_config["base_url"] = base_url

        self.embeddings = OpenAIEmbeddings(**embeddings_config)
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def load_documents(self) -> List[Document]:
        """Load documents from the documents directory"""
        docs_path = Path(self.documents_path)
        if not docs_path.exists():
            return []
        
        loader = DirectoryLoader(
            str(docs_path),
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def initialize_vectorstore(self):
        """Initialize or load the vector store"""
        faiss_index_path = Path("./faiss_index")
        
        if faiss_index_path.exists():
            # Load existing index
            self.vectorstore = FAISS.load_local(
                str(faiss_index_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            # Create new index
            documents = self.load_documents()
            if documents:
                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
                self.vectorstore.save_local(str(faiss_index_path))
            else:
                # Create empty vectorstore
                self.vectorstore = FAISS.from_texts([""], self.embeddings)
    
    def search(self, query: str, k: int = 3) -> List[Document]:
        """Search for relevant documents"""
        if not self.vectorstore:
            self.initialize_vectorstore()
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def rebuild_index(self):
        """Rebuild the vector store from documents"""
        documents = self.load_documents()
        if documents:
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
            self.vectorstore.save_local("./faiss_index")

# Global instance
rag_manager = RAGManager()
