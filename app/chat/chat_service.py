from typing import Dict, List
from app.config import settings

class ChatService:
    def __init__(self):
        self.sessions: Dict[str, List[dict]] = {}
    
    def get_messages(self, session_id: str) -> List[dict]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})
    
    def build_prompt(self, session_id: str, user_message: str) -> List[dict]:
        messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]
        messages.extend(self.get_messages(session_id))
        messages.append({"role": "user", "content": user_message})
        return messages

chat_service = ChatService()
