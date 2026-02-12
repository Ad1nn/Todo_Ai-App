"""Chat API endpoints for natural language task management."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.api.deps import CurrentUser, DbSession
from src.services.chat_service import ChatService, ChatServiceError

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(min_length=1, max_length=5000)
    conversation_id: UUID | None = None


class ToolCallResponse(BaseModel):
    """Tool call details in response."""

    tool: str
    parameters: dict[str, Any]
    result: dict[str, Any]


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    conversation_id: str
    response: str
    tool_calls: list[ToolCallResponse]


class ConversationResponse(BaseModel):
    """Conversation summary."""

    id: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    """Message details."""

    id: str
    role: str
    content: str
    tool_calls: list[dict[str, Any]] | None
    created_at: str


class ErrorResponse(BaseModel):
    """Error response body."""

    error: str
    detail: str | None = None


@router.post(
    "/{user_id}",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def send_chat_message(
    user_id: UUID,
    request: ChatRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> ChatResponse:
    """
    Send a natural language message to the AI assistant.

    The assistant will interpret the message, call appropriate tools
    (add_task, list_tasks, complete_task, delete_task, update_task),
    and return a conversational response.

    The endpoint is stateless - conversation history is loaded from
    the database on each request.
    """
    # Validate user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_id in path does not match authenticated user",
        )

    chat_service = ChatService(session, user_id)

    try:
        result = await chat_service.process_message(
            request.message,
            request.conversation_id,
        )
    except ChatServiceError as e:
        if e.code == "conversation_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message,
            ) from None
        if e.code in ("empty_message", "message_too_long"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            ) from None
        # API errors, rate limits, etc.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        ) from None

    return ChatResponse(
        conversation_id=result["conversation_id"],
        response=result["response"],
        tool_calls=[
            ToolCallResponse(
                tool=tc["tool"],
                parameters=tc["parameters"],
                result=tc["result"],
            )
            for tc in result["tool_calls"]
        ],
    )


@router.get(
    "/{user_id}/conversations",
    response_model=list[ConversationResponse],
)
async def list_conversations(
    user_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    limit: int = 10,
) -> list[ConversationResponse]:
    """List user's recent conversations."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_id in path does not match authenticated user",
        )

    chat_service = ChatService(session, user_id)
    conversations = await chat_service.list_conversations(limit)

    return [
        ConversationResponse(
            id=conv["id"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
        )
        for conv in conversations
    ]


@router.get(
    "/{user_id}/conversations/{conversation_id}",
    response_model=list[MessageResponse],
)
async def get_conversation_messages(
    user_id: UUID,
    conversation_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    limit: int = 50,
) -> list[MessageResponse]:
    """Get messages from a specific conversation."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_id in path does not match authenticated user",
        )

    chat_service = ChatService(session, user_id)

    try:
        messages = await chat_service.get_conversation_messages(conversation_id, limit)
    except ChatServiceError as e:
        if e.code == "conversation_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message,
            ) from None
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        ) from None

    return [
        MessageResponse(
            id=msg["id"],
            role=msg["role"],
            content=msg["content"],
            tool_calls=msg["tool_calls"],
            created_at=msg["created_at"],
        )
        for msg in messages
    ]
