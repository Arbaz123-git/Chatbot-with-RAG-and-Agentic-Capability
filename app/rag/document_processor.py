from typing import List
import PyPDF2
from io import BytesIO
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        logger.info(f"Extracted {len(text)} characters from PDF with {len(pdf_reader.pages)} pages")
        return text
    
    def extract_text_from_txt(self, file_content: bytes) -> str:
        return file_content.decode('utf-8')
    
    def chunk_text(self, text: str) -> List[str]:
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start += self.chunk_size - self.chunk_overlap
        
        logger.info(f"Created {len(chunks)} chunks (size={self.chunk_size}, overlap={self.chunk_overlap})")
        for i, chunk in enumerate(chunks[:3]):
            logger.debug(f"Chunk {i} preview: {chunk[:100]}...")
        
        return chunks
    
    def process_document(self, filename: str, file_content: bytes) -> List[str]:
        if filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(file_content)
        elif filename.endswith('.txt'):
            text = self.extract_text_from_txt(file_content)
        else:
            raise ValueError("Unsupported file format. Only PDF and TXT files are supported.")
        
        return self.chunk_text(text)

document_processor = DocumentProcessor()
