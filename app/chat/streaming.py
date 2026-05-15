from typing import AsyncGenerator

async def stream_response(content_generator) -> AsyncGenerator[str, None]:
    full_response = ""
    
    for content in content_generator:
        full_response += content
        yield f"data: {content}\n\n"
    
    yield f"data: [DONE]\n\n"
    
    return full_response
