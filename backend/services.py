from sqlalchemy.orm import Session
from typing import List, Optional
from models import Product, Order, OrderItem, Review, User, wishlist_association
from schemas import (
    ProductCreate, ProductResponse, OrderCreate, OrderResponse,
    ReviewCreate, ReviewResponse
)
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sentence_transformers import SentenceTransformer

load_dotenv()

class ProductService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_products(self, db: Session, skip: int = 0, limit: int = 100, category: str = None):
        """Get products with optional filtering."""
        query = db.query(Product).filter(Product.is_active == True)
        
        if category:
            query = query.filter(Product.category == category)
        
        products = query.offset(skip).limit(limit).all()
        return [ProductResponse.from_orm(product) for product in products]
    
    def get_product(self, db: Session, product_id: int):
        """Get a single product by ID."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            return ProductResponse.from_orm(product)
        return None
    
    def create_product(self, db: Session, product_data: ProductCreate):
        """Create a new product."""
        db_product = Product(**product_data.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return ProductResponse.from_orm(db_product)
    
    async def add_to_wishlist(self, db: Session, user_id: int, product_id: int):
        """Add a product to user's wishlist."""
        user = db.query(User).filter(User.id == user_id).first()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not user or not product:
            return False
        
        if product not in user.wishlist_products:
            user.wishlist_products.append(product)
            db.commit()
        
        return True
    
    async def remove_from_wishlist(self, db: Session, user_id: int, product_id: int):
        """Remove a product from user's wishlist."""
        user = db.query(User).filter(User.id == user_id).first()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not user or not product:
            return False
        
        if product in user.wishlist_products:
            user.wishlist_products.remove(product)
            db.commit()
        
        return True
    
    async def get_wishlist(self, db: Session, user_id: int):
        """Get user's wishlist."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        return [ProductResponse.from_orm(product) for product in user.wishlist_products]

class OrderService:
    def create_order(self, db: Session, order_data: OrderCreate, user_id: int):
        """Create a new order."""
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for item in order_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise ValueError(f"Product {item.product_id} not found")
            
            item_total = product.price * item.quantity
            total_amount += item_total
            
            order_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=product.price
            ))
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=order_data.shipping_address
        )
        db.add(order)
        db.flush()  # Get the order ID
        
        # Add order items
        for order_item in order_items:
            order_item.order_id = order.id
            db.add(order_item)
        
        db.commit()
        db.refresh(order)
        
        return OrderResponse.from_orm(order)
    
    def get_user_orders(self, db: Session, user_id: int):
        """Get all orders for a user."""
        orders = db.query(Order).filter(Order.user_id == user_id).all()
        return [OrderResponse.from_orm(order) for order in orders]

class ReviewService:
    def create_review(self, db: Session, review_data: ReviewCreate, user_id: int):
        """Create a new review."""
        # Check if user has already reviewed this product
        existing_review = db.query(Review).filter(
            Review.user_id == user_id,
            Review.product_id == review_data.product_id
        ).first()
        
        if existing_review:
            raise ValueError("You have already reviewed this product")
        
        review = Review(
            user_id=user_id,
            product_id=review_data.product_id,
            rating=review_data.rating,
            comment=review_data.comment
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        
        return ReviewResponse.from_orm(review)
    
    def get_product_reviews(self, db: Session, product_id: int):
        """Get all reviews for a product."""
        reviews = db.query(Review).filter(Review.product_id == product_id).all()
        return [ReviewResponse.from_orm(review) for review in reviews]

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASSWORD")
    
    async def send_order_confirmation(self, user_email: str, order: Order):
        """Send order confirmation email."""
        if not all([self.email, self.password]):
            print("Email configuration not set. Skipping email notification.")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = user_email
            msg['Subject'] = f"Order Confirmation #{order.id}"
            
            body = f"""
            Thank you for your order!
            
            Order ID: {order.id}
            Total Amount: ${order.total_amount}
            Status: {order.status}
            
            We'll send you another email when your order ships.
            
            Best regards,
            Your E-commerce Store
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, user_email, text)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
