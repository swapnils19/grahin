import os
import uuid
import magic
from typing import List, Tuple
from pathlib import Path
from PIL import Image
import PyPDF2
from docx import Document
from fastapi import UploadFile, HTTPException

from app.core.config import settings


class FileProcessor:
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Allowed file types
        self.allowed_extensions = {
            'text': ['.txt', '.md'],
            'pdf': ['.pdf'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'document': ['.docx', '.doc']
        }
        
        # Maximum file size (50MB default)
        self.max_file_size = self._parse_file_size(settings.max_file_size)
    
    def _parse_file_size(self, size_str: str) -> int:
        """Parse file size string like '50MB' to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from extension"""
        ext = Path(filename).suffix.lower()
        
        for file_type, extensions in self.allowed_extensions.items():
            if ext in extensions:
                return file_type
        
        return 'unknown'
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate file size and type"""
        # Check file size
        if hasattr(file, 'size') and file.size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_file_size}"
            )
        
        # Check file extension
        file_type = self._get_file_type(file.filename)
        if file_type == 'unknown':
            raise HTTPException(
                status_code=400,
                detail="File type not supported"
            )
    
    async def save_file(self, file: UploadFile, user_id: uuid.UUID) -> Tuple[str, str, int]:
        """Save uploaded file and return (filename, file_type, file_size)"""
        self._validate_file(file)
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = self.upload_dir / unique_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Get file info
        file_type = self._get_file_type(file.filename)
        mime_type = magic.from_buffer(content[:1024], mime=True)
        file_size = len(content)
        
        return unique_filename, file_type, file_size, mime_type
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text content from file"""
        file_path = Path(file_path)
        
        try:
            if file_type == 'text':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_type == 'pdf':
                return self._extract_pdf_text(file_path)
            
            elif file_type == 'document':
                return self._extract_docx_text(file_path)
            
            elif file_type == 'image':
                return f"[Image: {file_path.name}]"
            
            else:
                return ""
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error extracting text from file: {str(e)}"
            )
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks for processing"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at word boundary
            while end > start and text[end] not in '.!?\n ':
                end -= 1
            
            if end == start:
                end = start + chunk_size
            
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks


file_processor = FileProcessor()
