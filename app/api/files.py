import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.file import File as FileModel, DocumentChunk
from app.schemas.file import FileUploadResponse, FileListResponse
from app.api.deps import get_current_active_user
from app.services.file_processor import file_processor

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Save file
    filename, file_type, file_size, mime_type = await file_processor.save_file(file, current_user.id)
    
    # Create file record
    db_file = FileModel(
        user_id=current_user.id,
        filename=filename,
        original_filename=file.filename,
        file_type=file_type,
        file_size=file_size,
        file_path=str(file_processor.upload_dir / filename),
        mime_type=mime_type
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    # Process file in background (extract text and create chunks)
    # This would typically be handled by a background task
    try:
        text_content = file_processor.extract_text(db_file.file_path, file_type)
        chunks = file_processor.chunk_text(text_content)
        
        # Save chunks
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                file_id=db_file.id,
                chunk_index=i,
                content=chunk_text
            )
            db.add(chunk)
        
        # Update file status
        db_file.is_processed = True
        db_file.processing_status = "completed"
        
    except Exception as e:
        db_file.processing_status = "failed"
        print(f"Error processing file {db_file.id}: {e}")
    
    db.commit()
    db.refresh(db_file)
    
    return db_file


@router.get("/", response_model=FileListResponse)
def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    files = db.query(FileModel).filter(
        FileModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    total = db.query(FileModel).filter(
        FileModel.user_id == current_user.id
    ).count()
    
    return FileListResponse(files=files, total=total)


@router.get("/{file_id}", response_model=FileUploadResponse)
def get_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file


@router.delete("/{file_id}")
def delete_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file from filesystem
    import os
    try:
        os.remove(file.file_path)
    except OSError:
        pass  # File might not exist
    
    # Delete from database (cascades to chunks)
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted successfully"}
