from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
import os
from typing import Optional

from database import get_db, engine, Base
from models import User, Product, Order, OrderItem, Review, ConversationSession, ConversationMessage
from schemas import (
    UserCreate, UserResponse, ProductCreate, ProductResponse,
    OrderCreate, OrderResponse, ReviewCreate, ReviewResponse,
    LoginRequest, TokenResponse, AgentChatRequest, AgentChatResponse,
    ChangePasswordRequest
)
from auth import create_access_token, verify_token, get_password_hash, verify_password
from services import ProductService, OrderService, ReviewService, EmailService
from pinecone_service import PineconeService
from agent_service import ShopAgent

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Initialize services
product_service = ProductService()
order_service = OrderService()
review_service = ReviewService()
email_service = EmailService()

# Initialize AI services (lazy loading to handle missing API keys gracefully)
pinecone_service = None
shop_agent = None

def get_pinecone_service():
    global pinecone_service
    if pinecone_service is None:
        pinecone_service = PineconeService()
    return pinecone_service

def get_shop_agent():
    global shop_agent
    if shop_agent is None:
        shop_agent = ShopAgent(pinecone_service=get_pinecone_service())
    return shop_agent

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active
    )

@app.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )

@app.put("/auth/update-profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information."""
    # Check if email is already taken by another user
    if user_data.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Update user information
    current_user.email = user_data.email
    current_user.full_name = user_data.full_name

    # Update password if provided
    if user_data.password:
        current_user.hashed_password = get_password_hash(user_data.password)

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )

@app.put("/auth/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

# Product endpoints
@app.get("/products", response_model=list[ProductResponse])
async def get_products(
    skip: int = 0, 
    limit: int = 100, 
    category: str = None,
    db: Session = Depends(get_db)
):
    return product_service.get_products(db, skip=skip, limit=limit, category=category)

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = product_service.create_product(db, product_data)
    # Index new product to Pinecone
    try:
        db_product = db.query(Product).filter(Product.id == product.id).first()
        if db_product:
            service = get_pinecone_service()
            await service.index_product(db_product)
    except Exception:
        pass  # Don't fail product creation if indexing fails
    return product

# Semantic Search endpoint (Pinecone)
@app.post("/search")
async def search_products(
    query: str,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """Semantic product search using Pinecone vector database."""
    try:
        service = get_pinecone_service()
        results = await service.search(
            query=query,
            db=db,
            top_k=limit,
            category_filter=category,
            min_price=min_price,
            max_price=max_price
        )
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


# Agent Chat endpoint
@app.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with the AI shopping agent.
    Supports multi-turn conversations with session management.
    """
    try:
        agent = get_shop_agent()
        response = await agent.process_message(
            message=request.message,
            db=db,
            session_id=request.session_id,
            user_id=request.user_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# Authenticated chat endpoint
@app.post("/chat/authenticated", response_model=AgentChatResponse)
async def authenticated_chat(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chat with agent as authenticated user."""
    try:
        agent = get_shop_agent()
        response = await agent.process_message(
            message=request.message,
            db=db,
            session_id=request.session_id,
            user_id=current_user.id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# Product recommendations endpoint
@app.get("/products/{product_id}/recommendations")
async def get_product_recommendations(
    product_id: int,
    limit: int = Query(default=5, le=20),
    db: Session = Depends(get_db)
):
    """Get similar product recommendations."""
    try:
        service = get_pinecone_service()
        results = await service.find_similar_products(
            product_id=product_id,
            db=db,
            top_k=limit
        )
        return {"recommendations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


# Conversation history endpoint
@app.get("/conversations/{session_id}")
async def get_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation history for a session."""
    session = db.query(ConversationSession).filter(
        ConversationSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).order_by(ConversationMessage.created_at).all()

    return {
        "session_id": session.id,
        "created_at": session.created_at,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "intent": m.intent,
                "created_at": m.created_at
            }
            for m in messages
        ]
    }


# Admin: Index products to Pinecone
@app.post("/admin/index-products")
async def index_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Re-index all products to Pinecone vector database."""
    try:
        service = get_pinecone_service()
        count = await service.index_all_products(db)
        return {"message": f"Successfully indexed {count} products"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing error: {str(e)}")

# Order endpoints
@app.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = order_service.create_order(db, order_data, current_user.id)
    
    # Send email notification
    await email_service.send_order_confirmation(current_user.email, order)
    
    return order

@app.get("/orders", response_model=list[OrderResponse])
async def get_user_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.get_user_orders(db, current_user.id)

# Review endpoints
@app.post("/reviews", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return review_service.create_review(db, review_data, current_user.id)

@app.get("/products/{product_id}/reviews", response_model=list[ReviewResponse])
async def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    return review_service.get_product_reviews(db, product_id)

# Wishlist endpoints
@app.post("/wishlist/{product_id}")
async def add_to_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await product_service.add_to_wishlist(db, current_user.id, product_id)

@app.delete("/wishlist/{product_id}")
async def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await product_service.remove_from_wishlist(db, current_user.id, product_id)

@app.get("/wishlist", response_model=list[ProductResponse])
async def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await product_service.get_wishlist(db, current_user.id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
