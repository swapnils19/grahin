from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class FileBase(BaseModel):
    original_filename: str
    file_type: str


class FileUploadResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    upload_date: datetime
    processing_status: str

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    files: List[FileUploadResponse]
    total: int


class DocumentChunkResponse(BaseModel):
    id: UUID
    chunk_index: int
    content: str
    embedding_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
