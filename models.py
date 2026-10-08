from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
import datetime
from .database import Base

# Enum defining the possible statuses for our requests and certificates
class StatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# Represents a single bulk request that groups multiple certificate generation jobs
class BulkRequest(Base):
    __tablename__ = "bulk_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True) # e.g., "Python Bootcamp 2023"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING)
    
    # Relationship to easily access all recipients belonging to this bulk request
    recipients = relationship("Recipient", back_populates="bulk_request")

# Represents an individual recipient who will receive a certificate
class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    bulk_request_id = Column(Integer, ForeignKey("bulk_requests.id"))
    name = Column(String, index=True)
    email = Column(String, index=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING)
    
    # Where the final PDF is stored on the server
    file_path = Column(String, nullable=True) 
    # To track any errors during generation
    error_message = Column(String, nullable=True)

    # Back-reference to the parent bulk request
    bulk_request = relationship("BulkRequest", back_populates="recipients")
