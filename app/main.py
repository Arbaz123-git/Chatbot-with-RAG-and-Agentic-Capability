from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest
from app.chat.chat_service import chat_service
from app.utils.llm_client import llm_client

app = FastAPI(title="AI Chatbot with RAG and Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "healthy", "message": "AI Chatbot API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    messages = chat_service.build_prompt(request.session_id, request.message)
    
    chat_service.add_message(request.session_id, "user", request.message)
    
    async def generate():
        full_response = ""
        for content in llm_client.stream_chat(messages):
            full_response += content
            yield f"data: {content}\n\n"
        
        chat_service.add_message(request.session_id, "assistant", full_response)
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
