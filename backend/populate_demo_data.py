#!/usr/bin/env python3
"""
Demo data population script for ShopAI e-commerce platform.
This script creates sample products, users, and reviews for demonstration purposes.
"""

import sys
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Product, Review
from auth import get_password_hash
from datetime import datetime, timedelta
import random

# Create all tables
Base.metadata.create_all(bind=engine)

def create_demo_data():
    """Create demo data for the e-commerce platform."""
    db = SessionLocal()
    
    try:
        print("🚀 Creating demo data for ShopAI...")
        
        # Create demo users
        print("👥 Creating demo users...")
        demo_users = [
            {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "password": "password123"
            },
            {
                "email": "jane.smith@example.com", 
                "full_name": "Jane Smith",
                "password": "password123"
            },
            {
                "email": "mike.wilson@example.com",
                "full_name": "Mike Wilson", 
                "password": "password123"
            }
        ]
        
        users = []
        for user_data in demo_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=get_password_hash(user_data["password"]),
                    is_active=True
                )
                db.add(user)
                users.append(user)
            else:
                users.append(existing_user)
        
        db.commit()
        print(f"✅ Created {len(users)} users")
        
        # Create demo products
        print("🛍️ Creating demo products...")
        demo_products = [
            {
                "name": "Wireless Bluetooth Headphones",
                "description": "Premium wireless headphones with active noise cancellation, 30-hour battery life, and crystal-clear sound quality.",
                "price": 199.99,
                "category": "Electronics",
                "brand": "TechSound",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 50
            },
            {
                "name": "Smart Fitness Watch",
                "description": "Advanced fitness tracking with heart rate monitoring, GPS, sleep tracking, and 7-day battery life.",
                "price": 299.99,
                "category": "Wearables",
                "brand": "FitTech",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 30
            },
            {
                "name": "Mechanical Gaming Keyboard",
                "description": "RGB mechanical keyboard with tactile switches, programmable keys, and durable construction for gaming.",
                "price": 149.99,
                "category": "Gaming",
                "brand": "GamePro",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 25
            },
            {
                "name": "Portable Bluetooth Speaker",
                "description": "Waterproof portable speaker with 360-degree sound, 12-hour battery, and wireless connectivity.",
                "price": 79.99,
                "category": "Audio",
                "brand": "SoundWave",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 40
            },
            {
                "name": "Wireless Charging Pad",
                "description": "Fast wireless charging pad compatible with all Qi-enabled devices, sleek design with LED indicator.",
                "price": 49.99,
                "category": "Accessories",
                "brand": "ChargeTech",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 60
            },
            {
                "name": "Smart Home Hub",
                "description": "Central control hub for smart home devices with voice assistant integration and app control.",
                "price": 129.99,
                "category": "Smart Home",
                "brand": "HomeAI",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 20
            },
            {
                "name": "Gaming Mouse",
                "description": "High-precision gaming mouse with customizable RGB lighting, programmable buttons, and ergonomic design.",
                "price": 89.99,
                "category": "Gaming",
                "brand": "GamePro",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 35
            },
            {
                "name": "USB-C Hub",
                "description": "Multi-port USB-C hub with HDMI, USB 3.0, SD card reader, and power delivery for laptops.",
                "price": 69.99,
                "category": "Accessories",
                "brand": "ConnectPro",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 45
            },
            {
                "name": "Smart Light Bulbs (4-Pack)",
                "description": "WiFi-enabled smart LED bulbs with color changing, dimming, and voice control compatibility.",
                "price": 39.99,
                "category": "Smart Home",
                "brand": "HomeAI",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 100
            },
            {
                "name": "Laptop Stand",
                "description": "Adjustable aluminum laptop stand with ergonomic design, foldable for portability, and heat dissipation.",
                "price": 59.99,
                "category": "Accessories",
                "brand": "ErgoTech",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 30
            },
            {
                "name": "Noise-Canceling Earbuds",
                "description": "True wireless earbuds with active noise cancellation, 8-hour battery life, and premium sound quality.",
                "price": 179.99,
                "category": "Audio",
                "brand": "SoundWave",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 55
            },
            {
                "name": "Gaming Monitor",
                "description": "27-inch 4K gaming monitor with 144Hz refresh rate, 1ms response time, and HDR support.",
                "price": 399.99,
                "category": "Gaming",
                "brand": "GamePro",
                "image_url": "/placeholder-product.jpg",
                "stock_quantity": 15
            }
        ]
        
        products = []
        for product_data in demo_products:
            existing_product = db.query(Product).filter(Product.name == product_data["name"]).first()
            if not existing_product:
                product = Product(**product_data)
                db.add(product)
                products.append(product)
            else:
                products.append(existing_product)
        
        db.commit()
        print(f"✅ Created {len(products)} products")
        
        # Create demo reviews
        print("⭐ Creating demo reviews...")
        review_texts = [
            "Excellent product, highly recommended!",
            "Great quality and fast shipping.",
            "Perfect for my needs, works exactly as described.",
            "Amazing value for money, very satisfied.",
            "Good product but could be better.",
            "Outstanding quality and customer service.",
            "Works great, no complaints at all.",
            "Very happy with this purchase!",
            "Good product, meets expectations.",
            "Fantastic quality, exceeded my expectations."
        ]
        
        reviews_created = 0
        for product in products:
            # Create 2-5 reviews per product
            num_reviews = random.randint(2, 5)
            for _ in range(num_reviews):
                user = random.choice(users)
                review = Review(
                    user_id=user.id,
                    product_id=product.id,
                    rating=random.randint(3, 5),  # Mostly positive reviews
                    comment=random.choice(review_texts),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.add(review)
                reviews_created += 1
        
        db.commit()
        print(f"✅ Created {reviews_created} reviews")
        
        print("\n🎉 Demo data creation completed successfully!")
        print("\n📊 Summary:")
        print(f"   👥 Users: {len(users)}")
        print(f"   🛍️ Products: {len(products)}")
        print(f"   ⭐ Reviews: {reviews_created}")
        print("\n🔑 Demo User Credentials:")
        print("   Email: john.doe@example.com")
        print("   Password: password123")
        print("\n🌐 You can now start the development servers and explore the platform!")
        
    except Exception as e:
        print(f"❌ Error creating demo data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
