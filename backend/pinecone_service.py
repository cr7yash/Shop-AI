from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from config import get_settings
from models import Product
from schemas import ProductResponse


class ProductMetadata(BaseModel):
    """Metadata stored with product vectors in Pinecone."""
    product_id: int = Field(..., description="Product database ID")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    brand: str = Field(default="", description="Product brand")
    price: float = Field(..., description="Product price")
    stock_quantity: int = Field(..., description="Available stock")
    is_active: bool = Field(default=True, description="Product availability status")


class SearchResult(BaseModel):
    """Result from a semantic search query."""
    product: ProductResponse = Field(..., description="Product details")
    similarity: float = Field(..., ge=0, le=1, description="Similarity score")


class SearchQuery(BaseModel):
    """Parameters for a semantic search query."""
    query: str = Field(..., min_length=1, description="Search query string")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results")
    category_filter: Optional[str] = Field(default=None, description="Filter by category")
    min_price: Optional[float] = Field(default=None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(default=None, ge=0, description="Maximum price")
    min_score: float = Field(default=0.3, ge=0, le=1, description="Minimum similarity threshold")


class PineconeService:
    """Service for semantic product search using Pinecone vector database."""

    def __init__(self):
        settings = get_settings()
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY environment variable is not set")

        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self.model = SentenceTransformer(settings.embedding_model)
        self.dimension = settings.embedding_dimension
        self.cloud = settings.pinecone_cloud
        self.region = settings.pinecone_region
        self.default_min_score = settings.search_min_score

        self._initialize_index()
        self.index = self.pc.Index(self.index_name)

    def _initialize_index(self):
        """Create Pinecone index if it doesn't exist."""
        existing_indexes = [index.name for index in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=self.cloud,
                    region=self.region
                )
            )

    def _product_to_text(self, product: Product) -> str:
        """Convert product to searchable text representation."""
        parts = [
            product.name,
            product.description or "",
            product.category,
            product.brand or "",
            f"price ${product.price}"
        ]
        return " ".join(filter(None, parts))

    def _product_to_metadata(self, product: Product) -> ProductMetadata:
        """Convert product to Pydantic metadata model."""
        return ProductMetadata(
            product_id=product.id,
            name=product.name,
            category=product.category,
            brand=product.brand or "",
            price=float(product.price),
            stock_quantity=product.stock_quantity,
            is_active=product.is_active
        )

    async def index_product(self, product: Product) -> None:
        """Index a single product in Pinecone."""
        text = self._product_to_text(product)
        embedding = self.model.encode(text).tolist()
        metadata = self._product_to_metadata(product)

        self.index.upsert(
            vectors=[{
                "id": str(product.id),
                "values": embedding,
                "metadata": metadata.model_dump()
            }]
        )

    async def index_all_products(self, db: Session, batch_size: int = 100) -> int:
        """Index all active products from database to Pinecone."""
        products = db.query(Product).filter(Product.is_active == True).all()

        vectors = []
        for product in products:
            text = self._product_to_text(product)
            embedding = self.model.encode(text).tolist()
            metadata = self._product_to_metadata(product)

            vectors.append({
                "id": str(product.id),
                "values": embedding,
                "metadata": metadata.model_dump()
            })

            if len(vectors) >= batch_size:
                self.index.upsert(vectors=vectors)
                vectors = []

        if vectors:
            self.index.upsert(vectors=vectors)

        return len(products)

    async def delete_product(self, product_id: int) -> None:
        """Remove a product from Pinecone index."""
        self.index.delete(ids=[str(product_id)])

    def _build_filter(
        self,
        category_filter: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Build Pinecone metadata filter from search parameters."""
        filter_dict: Dict[str, Any] = {}

        if category_filter:
            filter_dict["category"] = {"$eq": category_filter}

        if min_price is not None and max_price is not None:
            filter_dict["price"] = {"$gte": min_price, "$lte": max_price}
        elif min_price is not None:
            filter_dict["price"] = {"$gte": min_price}
        elif max_price is not None:
            filter_dict["price"] = {"$lte": max_price}

        return filter_dict if filter_dict else None

    async def search(
        self,
        query: str,
        db: Session,
        top_k: int = 10,
        category_filter: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_score: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Semantic search for products using Pinecone.

        Args:
            query: Search query string
            db: Database session
            top_k: Number of results to return
            category_filter: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_score: Minimum similarity score threshold

        Returns:
            List of SearchResult objects with products and similarity scores
        """
        if min_score is None:
            min_score = self.default_min_score

        # Generate query embedding
        query_embedding = self.model.encode(query).tolist()

        # Build metadata filter
        filter_dict = self._build_filter(category_filter, min_price, max_price)

        # Query Pinecone
        query_params: Dict[str, Any] = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }

        if filter_dict:
            query_params["filter"] = filter_dict

        results = self.index.query(**query_params)

        # Format results with full product data from database
        search_results: List[SearchResult] = []
        for match in results.matches:
            if match.score >= min_score:
                product_id = int(match.id)
                product = db.query(Product).filter(Product.id == product_id).first()

                if product and product.is_active:
                    search_results.append(SearchResult(
                        product=ProductResponse.model_validate(product),
                        similarity=round(match.score, 4)
                    ))

        return search_results

    async def find_similar_products(
        self,
        product_id: int,
        db: Session,
        top_k: int = 5
    ) -> List[SearchResult]:
        """Find products similar to a given product."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return []

        text = self._product_to_text(product)
        results = await self.search(
            query=text,
            db=db,
            top_k=top_k + 1,
            min_score=0.2
        )

        # Filter out the original product
        return [r for r in results if r.product.id != product_id][:top_k]
