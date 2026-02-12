"""Chat service for managing conversations and agent interactions."""

import json
from typing import Any
from uuid import UUID

from agents import Runner
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.config import create_agent
from src.config import settings
from src.models.message import MessageRole
from src.repositories.conversation_repository import ConversationRepository


class ChatServiceError(Exception):
    """Error raised by chat service with user-friendly messages."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class ChatService:
    """Service for managing chat conversations and AI agent interactions."""

    def __init__(self, session: AsyncSession, user_id: UUID):
        """Initialize with database session and authenticated user ID."""
        self.session = session
        self.user_id = user_id
        self.conversation_repo = ConversationRepository(session)

    async def create_conversation(self) -> UUID:
        """Create a new conversation for the user."""
        conversation = await self.conversation_repo.create_conversation(self.user_id)
        return conversation.id

    async def get_or_create_conversation(self, conversation_id: UUID | None) -> UUID:
        """Get existing conversation or create a new one."""
        if conversation_id:
            conversation = await self.conversation_repo.get_conversation(
                conversation_id, self.user_id
            )
            if not conversation:
                raise ChatServiceError(
                    "conversation_not_found",
                    "Conversation not found or access denied",
                )
            return conversation.id
        return await self.create_conversation()

    async def _load_conversation_history(self, conversation_id: UUID) -> list[dict[str, str]]:
        """Load conversation history formatted for the agent."""
        messages = await self.conversation_repo.get_conversation_messages(
            conversation_id,
            self.user_id,
            limit=settings.max_conversation_messages,
        )

        return [{"role": msg.role.value, "content": msg.content} for msg in messages]

    async def _save_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> None:
        """Save a message to the conversation."""
        tool_calls_json = json.dumps(tool_calls) if tool_calls else None
        await self.conversation_repo.add_message(
            conversation_id=conversation_id,
            user_id=self.user_id,
            role=role,
            content=content,
            tool_calls=tool_calls_json,
        )

    async def process_message(
        self, message: str, conversation_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Process a user message and get agent response.

        Args:
            message: User's natural language message
            conversation_id: Optional existing conversation ID

        Returns:
            {conversation_id, response, tool_calls}
        """
        if not message or len(message.strip()) == 0:
            raise ChatServiceError("empty_message", "Message cannot be empty")

        if len(message) > 5000:
            raise ChatServiceError("message_too_long", "Message cannot exceed 5000 characters")

        # Get or create conversation
        conv_id = await self.get_or_create_conversation(conversation_id)

        # Load conversation history
        history = await self._load_conversation_history(conv_id)

        # Add current user message to history
        history.append({"role": "user", "content": message.strip()})

        # Save user message
        await self._save_message(conv_id, MessageRole.user, message.strip())

        # Create agent with user's session context
        agent = create_agent(self.session, self.user_id)

        # Run agent with conversation history
        try:
            result = await Runner.run(
                agent,
                input=history,
            )
        except Exception as e:
            # Handle OpenAI API errors gracefully
            error_message = str(e)
            if "rate_limit" in error_message.lower():
                raise ChatServiceError(
                    "rate_limit",
                    "Chat temporarily unavailable. Please try again in a moment.",
                ) from e
            if "api_key" in error_message.lower():
                raise ChatServiceError(
                    "api_error",
                    "Chat service configuration error. Please contact support.",
                ) from e
            raise ChatServiceError(
                "agent_error",
                "An error occurred processing your request. Please try again.",
            ) from e

        # Extract response and tool calls
        response_text = result.final_output if result.final_output else ""
        tool_calls = []

        # Collect tool calls from the run
        for item in result.new_items:
            if hasattr(item, "call") and hasattr(item, "output"):
                # This is a tool call result
                tool_calls.append(
                    {
                        "tool": item.call.name if hasattr(item.call, "name") else "unknown",
                        "parameters": item.call.arguments
                        if hasattr(item.call, "arguments")
                        else {},
                        "result": item.output if item.output else {},
                    }
                )

        # Save assistant response
        await self._save_message(
            conv_id,
            MessageRole.assistant,
            response_text,
            tool_calls if tool_calls else None,
        )

        return {
            "conversation_id": str(conv_id),
            "response": response_text,
            "tool_calls": tool_calls,
        }

    async def list_conversations(self, limit: int = 10) -> list[dict[str, Any]]:
        """List user's recent conversations."""
        conversations = await self.conversation_repo.list_user_conversations(self.user_id, limit)
        return [
            {
                "id": str(conv.id),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }
            for conv in conversations
        ]

    async def get_conversation_messages(
        self, conversation_id: UUID, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get messages from a conversation."""
        conversation = await self.conversation_repo.get_conversation(conversation_id, self.user_id)
        if not conversation:
            raise ChatServiceError(
                "conversation_not_found", "Conversation not found or access denied"
            )

        messages = await self.conversation_repo.get_conversation_messages(
            conversation_id, self.user_id, limit
        )

        return [
            {
                "id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "tool_calls": json.loads(msg.tool_calls) if msg.tool_calls else None,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]
