# ShopAI - Feature Overview

## Core Features Implemented

### Frontend Features

#### **Modern UI/UX**
- **Dark/Light Mode Toggle**: Seamless theme switching with system preference detection
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Smooth Animations**: Framer Motion animations throughout the app
- **Modern Components**: shadcn/ui components with Radix UI primitives
- **Accessibility**: WCAG compliant with keyboard navigation

#### **Navigation & Layout**
- **Header Component**: Logo, navigation, search, cart, user menu
- **Footer Component**: Links, contact info, social media
- **Layout System**: Consistent layout across all pages
- **Mobile Menu**: Collapsible navigation for mobile devices

#### **Product Discovery**
- **Product Cards**: Beautiful product cards with hover effects
- **Product Grid**: Responsive grid layout
- **Product Filtering**: Category, price, rating filters
- **Product Sorting**: Multiple sorting options
- **Search Functionality**: Real-time search with debouncing

#### **Shopping Experience**
- **Shopping Cart**: Persistent cart with local storage
- **Add to Cart**: One-click add to cart functionality
- **Cart Management**: Update quantities, remove items
- **Cart Page**: Full cart management interface
- **Checkout Process**: Simulated checkout flow

#### **AI-Powered Features**
- **Agentic AI Chat Assistant**: Multi-turn conversational shopping assistant with tool use
- **Semantic Search**: Pinecone vector database for production-grade search
- **Intent Classification**: Automatic detection of user intent (search, recommendations, orders, etc.)
- **Smart Recommendations**: AI-driven product suggestions based on similarity
- **Natural Language Processing**: Understand complex user queries with entity extraction

### Backend Features

#### **API Architecture**
- **RESTful API**: Clean, well-documented endpoints
- **FastAPI Framework**: High-performance async API
- **Pydantic Models**: Type-safe request/response models
- **CORS Support**: Cross-origin resource sharing
- **Error Handling**: Comprehensive error responses

#### **Authentication & Security**
- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt password hashing
- **User Registration**: User account creation
- **User Login**: Secure login with JWT tokens
- **Protected Routes**: Authentication middleware

#### **Database & Models**
- **SQLAlchemy ORM**: Database abstraction layer
- **User Model**: User accounts and profiles
- **Product Model**: Product catalog with categories
- **Order Model**: Order management system
- **Review Model**: Product reviews and ratings
- **Wishlist Model**: User wishlist functionality
- **Conversation Models**: Session and message storage for multi-turn chat

#### **AI Integration (Upgraded)**
- **Groq LLM Service**: Llama 3.3 70B Versatile model for high-performance inference
- **Pinecone Vector Search**: Production-ready semantic search with metadata filtering
- **Agentic Architecture**: ReAct-style agent with tool calling capabilities
- **Intent Classification**: JSON-mode structured output for accurate routing
- **Sentence Transformers**: all-MiniLM-L6-v2 for 384-dimensional embeddings
- **Conversation Management**: Persistent multi-turn conversation history

#### **Business Logic**
- **Product Service**: Product management operations
- **Order Service**: Order processing and management
- **Review Service**: Review creation and retrieval
- **Email Service**: Order confirmation notifications

### Advanced AI Features

#### **Agentic Shopping Assistant**
- **Tool-Based Architecture**: 5 specialized tools for product discovery
  - `search_products`: Semantic product search with filters
  - `get_product_details`: Detailed product information retrieval
  - `get_recommendations`: Similar product suggestions
  - `check_order_status`: Order tracking lookup
  - `get_user_orders`: User order history
- **Multi-Step Reasoning**: Iterative tool execution for complex queries
- **Context Awareness**: Maintains conversation history across turns
- **Session Management**: Persistent sessions with UUID-based tracking

#### **Intent Classification System**
- **10 Intent Types**:
  - `product_search` - Finding products
  - `product_recommendation` - Getting suggestions
  - `product_details` - Specific product info
  - `order_help` - Order assistance
  - `order_status` - Tracking orders
  - `general_question` - Store inquiries
  - `greeting` - Conversation starters
  - `farewell` - Conversation endings
  - `complaint` - Customer issues
  - `unknown` - Fallback handling
- **Entity Extraction**: Automatic extraction of product names, categories, brands, price ranges
- **Confidence Scoring**: Reliability indicator for classifications

#### **Semantic Search (Pinecone)**
- **Vector Embeddings**: 384-dimensional product representations
- **Metadata Filtering**: Filter by category, price range, availability
- **Similarity Scoring**: Cosine similarity with configurable threshold
- **Auto-Indexing**: Products indexed on creation
- **Bulk Indexing**: Admin endpoint for re-indexing all products

### User Experience

#### **Enhanced Chat Interface**
- **Intent Badges**: Visual indication of detected intent
- **Product Suggestions**: Clickable product badges in responses
- **Follow-Up Questions**: Quick action buttons for common queries
- **Tool Usage Display**: Transparency about AI actions
- **Session Continuity**: Conversations persist across messages
- **Loading States**: "Thinking..." indicator during processing

#### **Performance**
- **Lazy Service Loading**: AI services initialized on first use
- **Code Splitting**: Lazy loading of components
- **Image Optimization**: Next.js image optimization
- **Bundle Optimization**: Efficient JavaScript bundles
- **Caching**: API response caching

### Email & Notifications

#### **Email System**
- **SMTP Integration**: Email sending capability
- **Order Confirmations**: Automated order emails
- **HTML Templates**: Rich email formatting
- **Error Handling**: Email failure management

#### **Notification System**
- **Toast Notifications**: User feedback messages
- **Success Messages**: Operation confirmations
- **Error Messages**: Error notifications
- **Loading Indicators**: Progress feedback

### Design System

#### **Component Library**
- **Button Components**: Various button styles
- **Input Components**: Form input elements
- **Card Components**: Content containers
- **Modal Components**: Overlay dialogs
- **Badge Components**: Status indicators with intent icons

#### **Theme System**
- **CSS Variables**: Dynamic theme colors
- **Dark Mode**: Complete dark theme
- **Light Mode**: Clean light theme
- **System Theme**: OS preference detection

### Development Features

#### **Developer Experience**
- **TypeScript**: Full type safety
- **ESLint**: Code quality enforcement
- **Prettier**: Code formatting
- **Hot Reload**: Fast development iteration

#### **Testing & Quality**
- **Error Boundaries**: Component error handling
- **Input Validation**: Form validation
- **Type Checking**: Compile-time type checking
- **Code Splitting**: Performance optimization

## Technical Implementation

### **Frontend Stack**
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui + Radix UI
- **Animations**: Framer Motion
- **State**: React Context + useReducer
- **HTTP**: Axios with interceptors

### **Backend Stack**
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: SQLAlchemy ORM (SQLite/PostgreSQL)
- **Auth**: JWT with python-jose
- **AI**: Groq API + LangChain
- **Vector DB**: Pinecone (Serverless)
- **Email**: SMTP with python-multipart

### **AI/ML Stack**
- **LLM**: Groq Llama 3.3 70B Versatile
  - 131K context window
  - Tool/function calling support
  - JSON mode for structured output
  - ~280 tokens/second inference
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB**: Pinecone Serverless
  - Cosine similarity metric
  - Metadata filtering
  - Auto-scaling
- **Agent Framework**: Custom ReAct-style implementation
- **Search**: Semantic similarity with 0.3 threshold

## API Endpoints

### **AI Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Agentic chat with session support |
| `/chat/authenticated` | POST | Authenticated user chat |
| `/search` | POST | Semantic product search |
| `/products/{id}/recommendations` | GET | Similar product recommendations |
| `/conversations/{session_id}` | GET | Retrieve conversation history |
| `/admin/index-products` | POST | Re-index products to Pinecone |

### **Core Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | User authentication |
| `/products` | GET/POST | Product listing/creation |
| `/products/{id}` | GET | Product details |
| `/orders` | GET/POST | Order management |
| `/reviews` | POST | Create review |
| `/wishlist` | GET/POST/DELETE | Wishlist management |

## Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./ecommerce.db

# Authentication
SECRET_KEY=your-secret-key

# Groq (LLM)
GROQ_API_KEY=your_groq_api_key

# Pinecone (Vector DB)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=shop-ai-products

# Email (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email
EMAIL_PASSWORD=your-app-password
```

## Getting Started

1. **Clone the repository**
2. **Set up environment variables** (copy `backend/.env.example` to `backend/.env`)
3. **Install dependencies**:
   ```bash
   cd backend && pip install -r requirements.txt
   cd client && npm install
   ```
4. **Populate demo data**: `python backend/populate_demo_data.py`
5. **Start development servers**: `./start-dev.sh`
6. **Index products to Pinecone**: Call `POST /admin/index-products` after logging in
7. **Open http://localhost:3000**

The platform is ready for development, testing, and production deployment!
