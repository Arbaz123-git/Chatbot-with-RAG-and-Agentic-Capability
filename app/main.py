from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, UploadResponse, DebugSearchResponse, DebugSearchRequest
from app.chat.chat_service import chat_service
from app.utils.llm_client import llm_client
from app.rag.document_processor import document_processor
from app.rag.vector_store import vector_store

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

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    try:
        file_content = await file.read()
        chunks = document_processor.process_document(file.filename, file_content)
        chunk_count = vector_store.add_documents(file.filename, chunks)
        
        return UploadResponse(
            filename=file.filename,
            status="success",
            chunks=chunk_count,
            message=f"Document processed successfully. {chunk_count} chunks created."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/debug/search", response_model=DebugSearchResponse)
async def debug_search(request: DebugSearchRequest):
    results = vector_store.search(request.query, request.top_k)
    return DebugSearchResponse(
        query=request.query,
        top_k=request.top_k,
        results=results
    )

@app.post("/chat")
async def chat(request: ChatRequest):
    import logging
    logger = logging.getLogger(__name__)
    
    messages = chat_service.build_prompt(request.session_id, request.message, request.use_rag)
    
    logger.info(f"=== MESSAGES SENT TO LLM (use_rag={request.use_rag}) ===")
    for i, msg in enumerate(messages):
        content_preview = msg['content'][:300] if len(msg['content']) > 300 else msg['content']
        logger.info(f"Message {i} [{msg['role']}]: {content_preview}...")
    logger.info(f"=== END MESSAGES ===")
    
    async def generate():
        full_response = ""
        for content in llm_client.stream_chat(messages):
            full_response += content
            yield f"data: {content}\n\n"
        
        chat_service.add_message(request.session_id, "user", request.message)
        chat_service.add_message(request.session_id, "assistant", full_response)
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
