from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(
        default="sqlite:///./ecommerce.db",
        description="Database connection URL"
    )

    # JWT Authentication
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT encoding"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )

    # Groq LLM
    groq_api_key: str = Field(
        default="",
        description="Groq API key for LLM inference"
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model to use"
    )
    groq_max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for LLM response"
    )

    # Pinecone Vector DB
    pinecone_api_key: str = Field(
        default="",
        description="Pinecone API key"
    )
    pinecone_index_name: str = Field(
        default="shop-ai-products",
        description="Pinecone index name"
    )
    pinecone_cloud: str = Field(
        default="aws",
        description="Pinecone cloud provider"
    )
    pinecone_region: str = Field(
        default="us-east-1",
        description="Pinecone region"
    )

    # Embedding Model
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )
    embedding_dimension: int = Field(
        default=384,
        description="Embedding vector dimension"
    )

    # Search Settings
    search_top_k: int = Field(
        default=10,
        description="Default number of search results"
    )
    search_min_score: float = Field(
        default=0.3,
        description="Minimum similarity score threshold"
    )

    # Email (Optional)
    smtp_server: str = Field(
        default="smtp.gmail.com",
        description="SMTP server address"
    )
    smtp_port: int = Field(
        default=587,
        description="SMTP server port"
    )
    email_user: str = Field(
        default="",
        description="Email username"
    )
    email_password: str = Field(
        default="",
        description="Email password"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
