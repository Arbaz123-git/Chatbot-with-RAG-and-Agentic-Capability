from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, UploadResponse, DebugSearchResponse, DebugSearchRequest
from app.chat.chat_service import chat_service
from app.utils.llm_client import llm_client
from app.utils.logger import step_logger
from app.rag.document_processor import document_processor
from app.rag.vector_store import vector_store
from app.agent.agent_service import agent_service

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
    # Reset step counter for new request
    step_logger.reset_steps()
    step_logger.step(f"Received chat request", "MAIN")
    step_logger.info(f"Session: {request.session_id}", "MAIN")
    step_logger.info(f"Message: {request.message[:50]}...", "MAIN")
    
    # Determine routing based on explicit flags (default to chat mode)
    use_agent = request.use_agent or False
    use_rag = request.use_rag or False
    step_logger.step(f"Routing: use_agent={use_agent}, use_rag={use_rag}", "MAIN")
    
    if use_agent:
        step_logger.step("Entering AGENT mode", "MAIN")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant with access to tools."},
            {"role": "user", "content": request.message}
        ]
        
        async def generate_agent():
            full_response = ""
            async for content in agent_service.process_with_tools_streaming(messages):
                full_response += content
                yield f"data: {content}\n\n"
            
            chat_service.add_message(request.session_id, "user", request.message)
            chat_service.add_message(request.session_id, "assistant", full_response)
            step_logger.step("Response sent to user", "MAIN")
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate_agent(), media_type="text/event-stream")
    
    else:
        mode = "RAG" if use_rag else "CHAT"
        step_logger.step(f"Entering {mode} mode", "MAIN")
        messages = chat_service.build_prompt(request.session_id, request.message, use_rag)
        
        async def generate():
            step_logger.step("Streaming LLM response", "MAIN")
            full_response = ""
            for content in llm_client.stream_chat(messages):
                full_response += content
                yield f"data: {content}\n\n"
            
            chat_service.add_message(request.session_id, "user", request.message)
            chat_service.add_message(request.session_id, "assistant", full_response)
            step_logger.step("Response sent to user", "MAIN")
            step_logger.result(full_response)
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
