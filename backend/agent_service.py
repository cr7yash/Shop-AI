from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import uuid

from models import Product, Order, ConversationSession, ConversationMessage
from schemas import (
    ProductResponse, Intent, ExtractedEntities,
    AgentChatResponse, ToolResult
)
from groq_service import GroqLLMService
from pinecone_service import PineconeService, SearchResult


class ToolDefinition(BaseModel):
    """Definition of an agent tool."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")
    required: List[str] = Field(default_factory=list, description="Required parameters")


class ToolExecutionResult(BaseModel):
    """Result of executing a tool."""
    tool_name: str = Field(..., description="Name of the executed tool")
    success: bool = Field(..., description="Whether execution succeeded")
    result: Optional[Any] = Field(default=None, description="Tool result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class ConversationContext(BaseModel):
    """Context for the current conversation."""
    session_id: str = Field(..., description="Session ID")
    user_id: Optional[int] = Field(default=None, description="User ID if authenticated")
    history: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history")


class AgentToolkit:
    """Define tools available to the shopping agent."""

    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "search_products",
                "description": "Search for products using semantic search. Use this when the user wants to find or browse products.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query describing what products to find"
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category to filter by (e.g., 'electronics', 'clothing')"
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Optional minimum price filter"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Optional maximum price filter"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results to return (default 5, max 10)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_product_details",
                "description": "Get detailed information about a specific product by ID or name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "The product ID"
                        },
                        "product_name": {
                            "type": "string",
                            "description": "The product name to search for"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_recommendations",
                "description": "Get product recommendations based on a product, category, or user preferences.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "Product ID to find similar products for"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category to get recommendations from"
                        },
                        "preferences": {
                            "type": "string",
                            "description": "Description of user preferences"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of recommendations (default 5)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_order_status",
                "description": "Check the status of an order by order ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "integer",
                            "description": "The order ID to check"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_orders",
                "description": "Get all orders for the current authenticated user.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]


class ShopAgent:
    """
    Agentic AI chatbot with multi-step reasoning and tool use.
    Implements a ReAct-style agent loop for conversational product discovery.
    """

    SYSTEM_PROMPT = """You are an intelligent e-commerce shopping assistant for our online store.

Your capabilities:
1. Help customers search and discover products using semantic search
2. Provide detailed product information and comparisons
3. Give personalized recommendations based on preferences
4. Help with order-related queries
5. Answer general questions about the store

Guidelines:
- Be friendly, helpful, and concise
- When searching for products, use the search_products tool
- When users ask about specific products, get the details first
- Provide relevant suggestions and follow-up questions
- If you're unsure, ask clarifying questions
- Always format prices with $ and two decimal places
- When showing products, mention key details: name, price, and relevant features

You have access to tools - use them when needed to provide accurate, up-to-date information."""

    def __init__(self, pinecone_service: Optional[PineconeService] = None):
        self.llm_service = GroqLLMService()
        self.pinecone_service = pinecone_service or PineconeService()
        self.toolkit = AgentToolkit()

    def _search_result_to_dict(self, result: SearchResult) -> Dict[str, Any]:
        """Convert SearchResult to serializable dictionary."""
        product_dict = result.product.model_dump()
        product_dict["similarity"] = result.similarity
        return product_dict

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        db: Session,
        user_id: Optional[int] = None
    ) -> ToolResult:
        """Execute a tool and return the result."""
        call_id = str(uuid.uuid4())[:8]

        try:
            if tool_name == "search_products":
                results = await self.pinecone_service.search(
                    query=arguments.get("query", ""),
                    db=db,
                    top_k=min(arguments.get("limit", 5), 10),
                    category_filter=arguments.get("category"),
                    min_price=arguments.get("min_price"),
                    max_price=arguments.get("max_price")
                )
                serializable_results = [self._search_result_to_dict(r) for r in results]

                return ToolResult(
                    call_id=call_id,
                    tool_name=tool_name,
                    result=serializable_results,
                    success=True
                )

            elif tool_name == "get_product_details":
                product = None
                if arguments.get("product_id"):
                    product = db.query(Product).filter(
                        Product.id == arguments["product_id"],
                        Product.is_active == True
                    ).first()
                elif arguments.get("product_name"):
                    results = await self.pinecone_service.search(
                        query=arguments["product_name"],
                        db=db,
                        top_k=1
                    )
                    if results:
                        product = db.query(Product).filter(
                            Product.id == results[0].product.id
                        ).first()

                if product:
                    return ToolResult(
                        call_id=call_id,
                        tool_name=tool_name,
                        result=ProductResponse.model_validate(product).model_dump(),
                        success=True
                    )
                else:
                    return ToolResult(
                        call_id=call_id,
                        tool_name=tool_name,
                        result=None,
                        success=False,
                        error_message="Product not found"
                    )

            elif tool_name == "get_recommendations":
                results: List[SearchResult] = []
                if arguments.get("product_id"):
                    results = await self.pinecone_service.find_similar_products(
                        product_id=arguments["product_id"],
                        db=db,
                        top_k=arguments.get("limit", 5)
                    )
                elif arguments.get("preferences") or arguments.get("category"):
                    query = arguments.get("preferences", arguments.get("category", ""))
                    results = await self.pinecone_service.search(
                        query=query,
                        db=db,
                        top_k=arguments.get("limit", 5),
                        category_filter=arguments.get("category")
                    )
                else:
                    products = db.query(Product).filter(
                        Product.is_active == True
                    ).limit(5).all()
                    results = [
                        SearchResult(
                            product=ProductResponse.model_validate(p),
                            similarity=1.0
                        )
                        for p in products
                    ]

                serializable_results = [self._search_result_to_dict(r) for r in results]

                return ToolResult(
                    call_id=call_id,
                    tool_name=tool_name,
                    result=serializable_results,
                    success=True
                )

            elif tool_name == "check_order_status":
                order = db.query(Order).filter(
                    Order.id == arguments["order_id"]
                ).first()

                if order:
                    return ToolResult(
                        call_id=call_id,
                        tool_name=tool_name,
                        result={
                            "order_id": order.id,
                            "status": order.status,
                            "total_amount": float(order.total_amount),
                            "created_at": order.created_at.isoformat(),
                            "shipping_address": order.shipping_address
                        },
                        success=True
                    )
                else:
                    return ToolResult(
                        call_id=call_id,
                        tool_name=tool_name,
                        result=None,
                        success=False,
                        error_message="Order not found"
                    )

            elif tool_name == "get_user_orders":
                if not user_id:
                    return ToolResult(
                        call_id=call_id,
                        tool_name=tool_name,
                        result=None,
                        success=False,
                        error_message="Please log in to view your orders"
                    )

                orders = db.query(Order).filter(Order.user_id == user_id).all()
                return ToolResult(
                    call_id=call_id,
                    tool_name=tool_name,
                    result=[{
                        "order_id": o.id,
                        "status": o.status,
                        "total_amount": float(o.total_amount),
                        "created_at": o.created_at.isoformat()
                    } for o in orders],
                    success=True
                )

            else:
                return ToolResult(
                    call_id=call_id,
                    tool_name=tool_name,
                    result=None,
                    success=False,
                    error_message=f"Unknown tool: {tool_name}"
                )

        except Exception as e:
            return ToolResult(
                call_id=call_id,
                tool_name=tool_name,
                result=None,
                success=False,
                error_message=str(e)
            )

    async def _get_or_create_session(
        self,
        db: Session,
        session_id: Optional[str],
        user_id: Optional[int]
    ) -> ConversationSession:
        """Get existing session or create a new one."""
        if session_id:
            session = db.query(ConversationSession).filter(
                ConversationSession.id == session_id,
                ConversationSession.is_active == True
            ).first()
            if session:
                return session

        session = ConversationSession(
            user_id=user_id,
            is_active=True
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    async def _save_message(
        self,
        db: Session,
        session_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[str]] = None,
        tool_results: Optional[List[Dict[str, Any]]] = None
    ) -> ConversationMessage:
        """Save a message to conversation history."""
        message = ConversationMessage(
            session_id=session_id,
            role=role,
            content=content,
            intent=intent,
            entities=json.dumps(entities) if entities else None,
            tool_calls=json.dumps(tool_calls) if tool_calls else None,
            tool_results=json.dumps(tool_results) if tool_results else None
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    async def _get_conversation_history(
        self,
        db: Session,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """Get conversation history for context."""
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.created_at.desc()).limit(limit).all()

        messages = list(reversed(messages))
        return [{"role": m.role, "content": m.content} for m in messages]

    def _get_follow_up_questions(self, intent: Intent) -> Optional[List[str]]:
        """Get contextual follow-up questions based on intent."""
        follow_up_map = {
            Intent.PRODUCT_SEARCH: [
                "Would you like me to filter by price range?",
                "Should I show more options?",
                "Want details about any of these products?"
            ],
            Intent.PRODUCT_RECOMMENDATION: [
                "Would you like me to filter by price range?",
                "Should I show more options?",
                "Want details about any of these products?"
            ],
            Intent.PRODUCT_DETAILS: [
                "Would you like to see similar products?",
                "Any questions about this product?"
            ]
        }
        return follow_up_map.get(intent)

    async def process_message(
        self,
        message: str,
        db: Session,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        max_tool_iterations: int = 3
    ) -> AgentChatResponse:
        """
        Process a user message with full agent capabilities.

        Implements a ReAct-style agent loop:
        1. Classify intent
        2. Determine if tools are needed
        3. Execute tools iteratively
        4. Generate final response with context
        """
        session = await self._get_or_create_session(db, session_id, user_id)
        history = await self._get_conversation_history(db, session.id)
        intent_result = await self.llm_service.classify_intent(message, history)

        await self._save_message(
            db=db,
            session_id=session.id,
            role="user",
            content=message,
            intent=intent_result.intent.value,
            entities=intent_result.entities.model_dump() if intent_result.entities else None
        )

        tool_calls_made: List[str] = []
        tool_results: List[Dict[str, Any]] = []
        suggestions: List[ProductResponse] = []
        accumulated_results: List[Dict[str, Any]] = []
        response = ""

        if intent_result.intent in [Intent.GREETING, Intent.FAREWELL]:
            response = await self.llm_service.generate_response(
                message=message,
                system_prompt=self.SYSTEM_PROMPT,
                conversation_history=history
            )

        elif intent_result.intent in [
            Intent.PRODUCT_SEARCH,
            Intent.PRODUCT_RECOMMENDATION,
            Intent.PRODUCT_DETAILS
        ]:
            iteration = 0
            llm_response = None

            while iteration < max_tool_iterations:
                context_history = history.copy()
                if accumulated_results:
                    context_history.append({
                        "role": "assistant",
                        "content": f"Tool results so far: {json.dumps(accumulated_results, default=str)}"
                    })

                llm_response = await self.llm_service.call_with_tools(
                    message=message,
                    tools=self.toolkit.TOOLS,
                    system_prompt=self.SYSTEM_PROMPT,
                    conversation_history=context_history
                )

                if llm_response.tool_calls:
                    for tool_call in llm_response.tool_calls:
                        result = await self.execute_tool(
                            tool_name=tool_call["tool_name"],
                            arguments=tool_call["arguments"],
                            db=db,
                            user_id=user_id
                        )
                        tool_results.append(result.model_dump())
                        tool_calls_made.append(tool_call["tool_name"])
                        accumulated_results.append({
                            "tool": tool_call["tool_name"],
                            "result": result.result
                        })

                        if result.success and result.result and isinstance(result.result, list):
                            for item in result.result[:5]:
                                if isinstance(item, dict) and "id" in item:
                                    product = db.query(Product).filter(
                                        Product.id == item["id"]
                                    ).first()
                                    if product:
                                        suggestions.append(
                                            ProductResponse.model_validate(product)
                                        )

                    iteration += 1
                else:
                    if llm_response.content:
                        response = llm_response.content
                    break

            if not response:
                response = await self.llm_service.generate_response(
                    message=message,
                    system_prompt=self.SYSTEM_PROMPT,
                    conversation_history=history,
                    tool_results=accumulated_results
                )

        elif intent_result.intent in [Intent.ORDER_HELP, Intent.ORDER_STATUS]:
            if intent_result.entities.order_id:
                result = await self.execute_tool(
                    tool_name="check_order_status",
                    arguments={"order_id": intent_result.entities.order_id},
                    db=db,
                    user_id=user_id
                )
                tool_results.append(result.model_dump())
                tool_calls_made.append("check_order_status")
                accumulated_results.append({
                    "tool": "check_order_status",
                    "result": result.result
                })
            elif user_id:
                result = await self.execute_tool(
                    tool_name="get_user_orders",
                    arguments={},
                    db=db,
                    user_id=user_id
                )
                tool_results.append(result.model_dump())
                tool_calls_made.append("get_user_orders")
                accumulated_results.append({
                    "tool": "get_user_orders",
                    "result": result.result
                })

            response = await self.llm_service.generate_response(
                message=message,
                system_prompt=self.SYSTEM_PROMPT,
                conversation_history=history,
                tool_results=accumulated_results
            )

        else:
            response = await self.llm_service.generate_response(
                message=message,
                system_prompt=self.SYSTEM_PROMPT,
                conversation_history=history
            )

        await self._save_message(
            db=db,
            session_id=session.id,
            role="assistant",
            content=response,
            tool_calls=tool_calls_made if tool_calls_made else None,
            tool_results=tool_results if tool_results else None
        )

        follow_up_questions = self._get_follow_up_questions(intent_result.intent)

        return AgentChatResponse(
            response=response,
            session_id=session.id,
            intent=intent_result.intent,
            entities=intent_result.entities,
            suggestions=suggestions[:5] if suggestions else None,
            tool_calls_made=tool_calls_made if tool_calls_made else None,
            follow_up_questions=follow_up_questions
        )
