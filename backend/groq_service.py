from groq import Groq
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json

from config import get_settings
from schemas import Intent, ExtractedEntities, IntentClassificationResult


class ChatMessage(BaseModel):
    """Represents a chat message for LLM context."""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class LLMResponse(BaseModel):
    """Response from the LLM service."""
    content: str = Field(..., description="Generated response content")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Tool calls requested by the LLM"
    )


class ToolCallRequest(BaseModel):
    """Represents a tool call request from the LLM."""
    call_id: str = Field(..., description="Unique identifier for the tool call")
    tool_name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments to pass to the tool"
    )


class GroqLLMService:
    """Service for LLM operations using Groq with Llama 3.3 70B."""

    def __init__(self):
        settings = get_settings()
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")

        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.max_tokens = settings.groq_max_tokens

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        tool_context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Build messages list for LLM API call."""
        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        if tool_context:
            messages.append({"role": "system", "content": tool_context})

        messages.append({"role": "user", "content": user_message})
        return messages

    async def classify_intent(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> IntentClassificationResult:
        """
        Classify user intent and extract entities from message.
        Uses JSON mode for structured output.
        """
        system_prompt = """You are an intent classification system for an e-commerce shopping platform.

Analyze the user message and respond with a JSON object containing:
1. "intent": One of these exact values:
   - "product_search" - User wants to find/search for products
   - "product_recommendation" - User wants suggestions/recommendations
   - "product_details" - User asks about a specific product
   - "order_help" - User needs help with orders
   - "order_status" - User wants to check order status
   - "general_question" - General questions about the store
   - "greeting" - Hello, hi, etc.
   - "farewell" - Goodbye, thanks, etc.
   - "complaint" - User is unhappy or complaining
   - "unknown" - Cannot determine intent

2. "confidence": A float between 0.0 and 1.0 indicating how confident you are

3. "entities": An object that may contain:
   - "product_names": Array of product names mentioned
   - "categories": Array of categories (e.g., "electronics", "clothing", "shoes")
   - "brands": Array of brand names mentioned
   - "price_min": Minimum price if mentioned (number)
   - "price_max": Maximum price if mentioned (number)
   - "order_id": Order ID if mentioned (number)
   - "quantity": Quantity if mentioned (number)
   - "attributes": Object with other attributes (color, size, etc.)

4. "requires_clarification": Boolean, true if the intent is unclear

5. "clarification_question": If requires_clarification is true, suggest a question to ask

Respond ONLY with valid JSON, no other text."""

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": f"Classify this message: {message}"})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Parse intent safely
            intent_str = result.get("intent", "unknown")
            try:
                intent = Intent(intent_str)
            except ValueError:
                intent = Intent.UNKNOWN

            # Parse entities using Pydantic model
            entities_data = result.get("entities", {})
            entities = ExtractedEntities.model_validate(entities_data)

            return IntentClassificationResult(
                intent=intent,
                confidence=float(result.get("confidence", 0.5)),
                entities=entities,
                requires_clarification=result.get("requires_clarification", False),
                clarification_question=result.get("clarification_question")
            )

        except Exception:
            return IntentClassificationResult(
                intent=Intent.UNKNOWN,
                confidence=0.0,
                entities=ExtractedEntities(),
                requires_clarification=True,
                clarification_question="I'm not sure I understood that. Could you please rephrase?"
            )

    async def generate_response(
        self,
        message: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        tool_results: Optional[List[Dict]] = None
    ) -> str:
        """Generate a conversational response using Groq LLM."""
        tool_context = None
        if tool_results:
            tool_context = "Here are the results from the tools I used to help answer your question:\n\n"
            for result in tool_results:
                tool_context += f"**{result['tool_name']}**:\n```json\n{json.dumps(result['result'], indent=2, default=str)}\n```\n\n"

        messages = self._build_messages(
            system_prompt=system_prompt,
            user_message=message,
            conversation_history=conversation_history,
            tool_context=tool_context
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content

        except Exception:
            return "I apologize, but I encountered an error processing your request. Please try again."

    async def call_with_tools(
        self,
        message: str,
        tools: List[Dict],
        system_prompt: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> LLMResponse:
        """
        Call Groq with function/tool calling capability.

        Returns LLMResponse with either tool_calls or content.
        """
        messages = self._build_messages(
            system_prompt=system_prompt,
            user_message=message,
            conversation_history=conversation_history
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=self.max_tokens
            )

            response_message = response.choices[0].message

            if response_message.tool_calls:
                tool_calls = []
                for tool_call in response_message.tool_calls:
                    tool_call_request = ToolCallRequest(
                        call_id=tool_call.id,
                        tool_name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments)
                    )
                    tool_calls.append(tool_call_request.model_dump())

                return LLMResponse(content="", tool_calls=tool_calls)
            else:
                return LLMResponse(
                    content=response_message.content or "",
                    tool_calls=None
                )

        except Exception as e:
            return LLMResponse(
                content=f"I encountered an error: {str(e)}",
                tool_calls=None
            )
