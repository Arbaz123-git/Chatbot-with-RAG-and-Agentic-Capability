from typing import List
import PyPDF2
from io import BytesIO
from app.config import settings
import logging
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.separators = ["\n\n", "\n", ". ", " ", ""]
    
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
    
    def _split_text_with_separator(self, text: str, separator: str) -> List[str]:
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)
        return [s for s in splits if s]
    
    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        chunks = []
        current_chunk = []
        current_length = 0
        
        for split in splits:
            split_length = len(split)
            
            if current_length + split_length + len(separator) > self.chunk_size and current_chunk:
                chunk_text = separator.join(current_chunk)
                if chunk_text.strip():
                    chunks.append(chunk_text.strip())
                
                overlap_chunks = []
                overlap_length = 0
                for i in range(len(current_chunk) - 1, -1, -1):
                    overlap_length += len(current_chunk[i]) + len(separator)
                    if overlap_length > self.chunk_overlap:
                        break
                    overlap_chunks.insert(0, current_chunk[i])
                
                current_chunk = overlap_chunks
                current_length = sum(len(c) for c in current_chunk) + len(separator) * (len(current_chunk) - 1)
            
            current_chunk.append(split)
            current_length += split_length + len(separator)
        
        if current_chunk:
            chunk_text = separator.join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
        
        return chunks
    
    def chunk_text(self, text: str) -> List[str]:
        final_chunks = []
        chunks = [text]
        
        for separator in self.separators:
            new_chunks = []
            for chunk in chunks:
                if len(chunk) <= self.chunk_size:
                    new_chunks.append(chunk)
                else:
                    splits = self._split_text_with_separator(chunk, separator)
                    merged = self._merge_splits(splits, separator)
                    new_chunks.extend(merged)
            chunks = new_chunks
        
        final_chunks = [c for c in chunks if c.strip()]
        
        logger.info(f"Created {len(final_chunks)} chunks using recursive character text splitter (size={self.chunk_size}, overlap={self.chunk_overlap})")
        for i, chunk in enumerate(final_chunks[:3]):
            logger.debug(f"Chunk {i} preview: {chunk[:100]}...")
        
        return final_chunks
    
    def process_document(self, filename: str, file_content: bytes) -> List[str]:
        if filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(file_content)
        elif filename.endswith('.txt'):
            text = self.extract_text_from_txt(file_content)
        else:
            raise ValueError("Unsupported file format. Only PDF and TXT files are supported.")
        
        return self.chunk_text(text)

document_processor = DocumentProcessor()
