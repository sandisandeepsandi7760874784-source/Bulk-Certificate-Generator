from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .models import StatusEnum

# --- INCOMING DATA VALIDATION (Requests) ---

class RecipientCreate(BaseModel):
    name: str
    email: EmailStr # Automatically validates that this is a proper email address

class BulkRequestCreate(BaseModel):
    title: str
    recipients: List[RecipientCreate]


# --- OUTGOING DATA FORMATTING (Responses) ---

class RecipientResponse(BaseModel):
    id: int
    name: str
    email: str
    status: StatusEnum
    file_path: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True # Allows Pydantic to read data directly from SQLAlchemy models

class BulkRequestResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    status: StatusEnum
    recipients: List[RecipientResponse]

    class Config:
        from_attributes = True
