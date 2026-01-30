from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order schemas
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: str

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductResponse
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    shipping_address: str
    created_at: datetime
    order_items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

# Review schemas
class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True

# Authentication schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Search schemas
class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    results: List[ProductResponse]
    total: int

# Chat schemas (legacy - kept for backwards compatibility)
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[ProductResponse]] = None


# Intent Classification
class Intent(str, Enum):
    PRODUCT_SEARCH = "product_search"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    PRODUCT_DETAILS = "product_details"
    ORDER_HELP = "order_help"
    ORDER_STATUS = "order_status"
    GENERAL_QUESTION = "general_question"
    GREETING = "greeting"
    FAREWELL = "farewell"
    COMPLAINT = "complaint"
    UNKNOWN = "unknown"


class ExtractedEntities(BaseModel):
    product_names: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    order_id: Optional[int] = None
    quantity: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None


class IntentClassificationResult(BaseModel):
    intent: Intent
    confidence: float
    entities: ExtractedEntities
    requires_clarification: bool = False
    clarification_question: Optional[str] = None


# Agent Tool Definitions
class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str


class ToolResult(BaseModel):
    call_id: str
    tool_name: str
    result: Any
    success: bool
    error_message: Optional[str] = None


# Conversation Management
class ConversationMessageCreate(BaseModel):
    role: str
    content: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None


class ConversationMessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSessionResponse(BaseModel):
    id: str
    user_id: Optional[int] = None
    created_at: datetime
    is_active: bool
    messages: List[ConversationMessageResponse] = []

    class Config:
        from_attributes = True


# Enhanced Agent Chat Request/Response
class AgentChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[int] = None


class AgentChatResponse(BaseModel):
    response: str
    session_id: str
    intent: Intent
    entities: ExtractedEntities
    suggestions: Optional[List[ProductResponse]] = None
    tool_calls_made: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None
