from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "citizen"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Issue schemas
class IssueCreate(BaseModel):
    title: str
    description: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    reporter_name: str
    reporter_contact: Optional[str] = None
    category: Optional[str] = None  # Auto-predicted if not provided

class IssueUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    admin_notes: Optional[str] = None

class IssueResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    severity: str
    status: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    department: Optional[str] = None
    reporter_name: str
    reporter_contact: Optional[str] = None
    assigned_to: Optional[str] = None
    priority_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    admin_notes: Optional[str] = None
    
    class Config:
        from_attributes = True

# Analytics schemas
class AnalyticsResponse(BaseModel):
    total_issues: int
    pending: int
    in_progress: int
    resolved: int
    rejected: int
    by_category: dict
    by_severity: dict
    by_department: dict
    recent_issues: list
    resolution_time_avg: Optional[float] = None

class AutoSuggestionRequest(BaseModel):
    partial_text: str

class PredictionRequest(BaseModel):
    title: str
    description: str