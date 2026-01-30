# ShopAI - AI-Powered E-commerce Platform

A modern, intelligent e-commerce platform built with Next.js, FastAPI, and AI technologies. Features include RAG-powered search, LLM chat assistance, dark/light mode, and smooth animations.

## 🚀 Features

### Frontend (Next.js + TypeScript)
- **Modern UI**: Built with shadcn/ui components and Tailwind CSS
- **Dark/Light Mode**: Seamless theme switching with system preference detection
- **Animations**: Smooth Framer Motion animations throughout the app
- **Responsive Design**: Mobile-first approach with responsive layouts
- **AI Chat**: Intelligent shopping assistant with real-time chat
- **Smart Search**: RAG-powered product search with semantic understanding
- **Shopping Cart**: Persistent cart with local storage
- **Product Discovery**: Advanced filtering and sorting capabilities

### Backend (FastAPI + Python)
- **RESTful API**: Clean, well-documented API endpoints
- **Authentication**: JWT-based authentication system with password change
- **Database**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **Vector Search**: Pinecone-powered semantic product search
- **LLM Integration**: Groq API integration for AI chat assistance
- **User Features**: Profile management, orders, wishlist tracking
- **Security**: Password hashing, CORS protection, input validation

### AI Features
- **Vector Search**: Semantic product search using Pinecone embeddings
- **LLM Chat**: Groq-powered shopping assistant with intelligent responses
- **Product Discovery**: AI-enhanced search and recommendations
- **Natural Language Processing**: Understand user queries in natural language

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui + Radix UI
- **Animations**: Framer Motion
- **State Management**: React Context + useReducer
- **HTTP Client**: Axios
- **Forms**: React Hook Form + Zod validation

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: SQLAlchemy ORM
- **Authentication**: JWT with python-jose
- **AI/ML**: Groq API, Pinecone, LangChain, Sentence Transformers
- **Security**: Passlib for password hashing
- **Task Management**: APScheduler for background tasks

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL (optional, SQLite works for development)
- Groq API Key (for AI features)
- Pinecone API Key (for vector storage)

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd client
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   Create a `.env.local` file in the `client` directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the `backend` directory:
   ```env
   # Database
   DATABASE_URL=sqlite:///./ecommerce.db
   
   # Authentication
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Groq API
   GROQ_API_KEY=your-groq-api-key-here
   
   # Pinecone Configuration
   PINECONE_API_KEY=your-pinecone-api-key-here
   PINECONE_ENV=your-pinecone-environment
   PINECONE_INDEX_NAME=shop-ai-index
   ```

5. **Run the backend server**:
   ```bash
   python main.py
   ```

The backend API will be available at `http://localhost:8000`

## 🚀 Getting Started

1. **Start the backend server**:
   ```bash
   cd backend
   python main.py
   ```

2. **In a new terminal, start the frontend**:
   ```bash
   cd client
   npm run dev
   ```

3. **Open your browser** and navigate to `http://localhost:3000`

4. **Explore the features**:
   - Browse products on the homepage
   - Try the AI search functionality
   - Chat with the AI shopping assistant
   - Add items to cart and checkout
   - Manage your profile and orders
   - Add items to wishlist
   - Switch between dark and light modes

## 🔧 Configuration

### Groq API Setup
1. Get an API key from [Groq](https://console.groq.com)
2. Add it to your backend `.env` file as `GROQ_API_KEY`

### Pinecone Configuration
1. Create an account at [Pinecone](https://www.pinecone.io/)
2. Create an index for embeddings
3. Add your API key and environment to backend `.env` file

### Database Configuration
- **Development**: SQLite (default, no setup required)
- **Production**: PostgreSQL (update `DATABASE_URL` in `.env`)

## 📁 Project Structure

```
├── client/                        # Next.js frontend
│   ├── src/
│   │   ├── app/                  # App router pages
│   │   ├── components/           # React components
│   │   ├── contexts/             # React contexts
│   │   └── lib/                  # Utilities and API client
│   └── public/                   # Static assets
├── backend/                       # FastAPI backend
│   ├── main.py                   # FastAPI application
│   ├── models.py                 # SQLAlchemy models
│   ├── schemas.py                # Pydantic schemas
│   ├── auth.py                   # Authentication logic
│   ├── services.py               # Business logic
│   ├── groq_service.py           # Groq AI integration
│   ├── pinecone_service.py       # Vector store integration
│   └── database.py               # Database configuration
├── start-dev.sh                  # Development startup script
├── FEATURES.md                   # Feature documentation
└── README.md                     # This file
```

## 🎨 Customization

### Adding New Features
1. **Frontend**: Add new components in `src/components/`
2. **Backend**: Add new endpoints in `main.py` and services in `services.py`
3. **Database**: Update models in `models.py` and run migrations

### Styling
- Modify Tailwind classes in components
- Update theme colors in `tailwind.config.js`
- Add custom CSS in `globals.css`

### AI Features
- Modify RAG search in `services.py` → `RAGService`
- Update LLM chat in `services.py` → `LLMService`
- Add new AI models by updating dependencies

## 🚀 Deployment

### Frontend (Vercel/Netlify)
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Backend (Railway/Heroku/DigitalOcean)
1. Create a new app
2. Set environment variables
3. Deploy from GitHub or Docker

### Database
- Use managed PostgreSQL (Supabase, PlanetScale, etc.)
- Update `DATABASE_URL` in production environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [shadcn/ui](https://ui.shadcn.com/) for beautiful components
- [Framer Motion](https://www.framer.com/motion/) for animations
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Groq](https://groq.com/) for fast LLM inference
- [Pinecone](https://www.pinecone.io/) for vector storage and search
- [LangChain](https://www.langchain.com/) for LLM integration
---