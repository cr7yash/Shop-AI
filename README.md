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
- **Authentication**: JWT-based authentication system
- **Database**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **RAG Search**: Vector-based product search using ChromaDB
- **LLM Integration**: OpenAI GPT integration for chat assistance
- **Email Notifications**: Order confirmation emails
- **Security**: Password hashing, CORS protection, input validation

### AI Features
- **RAG Search**: Semantic product search using sentence transformers
- **LLM Chat**: GPT-powered shopping assistant
- **Product Recommendations**: AI-driven product suggestions
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
- **AI/ML**: OpenAI API, LangChain, ChromaDB, Sentence Transformers
- **Email**: SMTP with python-multipart
- **Security**: Passlib for password hashing

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL (optional, SQLite works for development)

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd ecommerce-app
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   Create a `.env.local` file in the `ecommerce-app` directory:
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
   
   # OpenAI API
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Email Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```

5. **Run the backend server**:
   ```bash
   python main.py
   ```

The backend API will be available at `http://localhost:8000`

## 🚀 Getting Started

1. **Start both servers**:
   - Backend: `cd backend && python main.py`
   - Frontend: `cd ecommerce-app && npm run dev`

2. **Open your browser** and navigate to `http://localhost:3000`

3. **Explore the features**:
   - Browse products on the homepage
   - Try the AI search functionality
   - Chat with the AI assistant
   - Add items to cart and checkout
   - Switch between dark and light modes

## 🔧 Configuration

### OpenAI API Setup
1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Add it to your backend `.env` file as `OPENAI_API_KEY`

### Email Configuration
For email notifications, configure SMTP settings in the backend `.env` file:
- Gmail: Use app passwords for authentication
- Other providers: Update SMTP server and port accordingly

### Database Configuration
- **Development**: SQLite (default, no setup required)
- **Production**: PostgreSQL (update `DATABASE_URL` in `.env`)

## 📁 Project Structure

```
├── ecommerce-app/                 # Next.js frontend
│   ├── src/
│   │   ├── app/                  # App router pages
│   │   ├── components/           # React components
│   │   ├── contexts/            # React contexts
│   │   └── lib/                 # Utilities and API client
│   └── public/                  # Static assets
├── backend/                      # FastAPI backend
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Database models
│   ├── schemas.py               # Pydantic schemas
│   ├── auth.py                  # Authentication logic
│   ├── services.py              # Business logic
│   └── database.py              # Database configuration
└── README.md                    # This file
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
- [OpenAI](https://openai.com/) for AI capabilities
- [ChromaDB](https://www.trychroma.com/) for vector storage

## 📞 Support

If you encounter any issues or have questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

---