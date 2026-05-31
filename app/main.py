from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from .chat import chat_manager
from .rag import rag_manager

app = FastAPI(title="AI Chat API", version="1.0.0")

# CORS middleware - 配置允许的前端域名
# 生产环境请替换为实际的前端域名
allowed_origins = [
    "http://localhost:5173",  # 本地开发
    "http://localhost:3000",  # 备用端口
    "https://*.edgeone.ai",   # EdgeOne Pages
    "https://*.vercel.app",   # Vercel
    "https://*.netlify.app",  # Netlify
]

# 从环境变量读取额外的允许域名
if frontend_url := os.getenv("FRONTEND_URL"):
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_rag: bool = True

class ChatResponse(BaseModel):
    session_id: str
    message: str

@app.on_event("startup")
async def startup_event():
    """Initialize RAG on startup"""
    try:
        rag_manager.initialize_vectorstore()
    except Exception as e:
        print(f"Warning: Failed to initialize vectorstore on startup: {e}")
        print("Vectorstore will be initialized on first use.")
        print("Note: RAG features will be disabled if embedding API is not available.")

@app.get("/")
async def root():
    return {"message": "AI Chat API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with streaming response"""
    session_id = request.session_id or str(uuid.uuid4())

    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Chat request - session_id: {session_id}, use_rag: {request.use_rag}, message: {request.message[:50]}")

    async def generate():
        try:
            async for chunk in chat_manager.chat(
                session_id=session_id,
                user_message=request.message,
                use_rag=request.use_rag
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Chat error: {type(e).__name__}: {e}", exc_info=True)
            yield f"Error: {str(e)}"

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"X-Session-ID": session_id}
    )

@app.post("/rebuild-index")
async def rebuild_index():
    """Rebuild the vector store index"""
    try:
        rag_manager.rebuild_index()
        return {"message": "Index rebuilt successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
