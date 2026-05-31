from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .config import settings
from .rag import rag_manager

class ChatManager:
    def __init__(self):
        # 构建 LLM 配置
        llm_config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
            "temperature": 0.7,
            "streaming": True
        }

        # 如果配置了自定义 base_url，则添加
        if settings.openai_api_base:
            base_url = settings.openai_api_base
            # 确保 base_url 以 /v1 结尾
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'
            llm_config["base_url"] = base_url

        self.llm = ChatOpenAI(**llm_config)
        self.conversation_history: Dict[str, List] = {}
    
    def get_history(self, session_id: str) -> List:
        """Get conversation history for a session"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        return self.conversation_history[session_id]
    
    def add_to_history(self, session_id: str, role: str, content: str):
        """Add message to conversation history with sliding window"""
        history = self.get_history(session_id)
        
        if role == "user":
            history.append(HumanMessage(content=content))
        elif role == "assistant":
            history.append(AIMessage(content=content))
        
        # Sliding window: keep only last N messages
        if len(history) > settings.max_history_length:
            self.conversation_history[session_id] = history[-settings.max_history_length:]
    
    async def chat(self, session_id: str, user_message: str, use_rag: bool = True):
        """Generate chat response with optional RAG"""
        # Retrieve relevant documents if RAG is enabled
        context = ""
        if use_rag:
            try:
                relevant_docs = rag_manager.search(user_message, k=3)
                if relevant_docs:
                    context = "\n\n".join([doc.page_content for doc in relevant_docs])
            except Exception as e:
                print(f"Warning: RAG search failed: {e}")
                print("Continuing without RAG context.")
        
        # Build messages
        messages = []
        
        # System message with context
        system_content = "你是一个智能助手，能够基于提供的知识库回答问题。"
        if context:
            system_content += f"\n\n相关知识库内容：\n{context}"
        messages.append(SystemMessage(content=system_content))
        
        # Add conversation history
        history = self.get_history(session_id)
        messages.extend(history)
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Stream response
        full_response = ""
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content
        
        # Save to history
        self.add_to_history(session_id, "user", user_message)
        self.add_to_history(session_id, "assistant", full_response)

# Global instance
chat_manager = ChatManager()
