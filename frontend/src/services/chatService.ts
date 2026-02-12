/**
 * Chat API service for interacting with the AI assistant.
 */

import { getToken } from '@/lib/auth';
import type {
  ChatRequest,
  ChatResponse,
  Conversation,
  Message,
} from '@/types/chat';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ChatApiError extends Error {
  constructor(
    public statusCode: number,
    public detail: string
  ) {
    super(detail);
    this.name = 'ChatApiError';
  }
}

async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();

  if (!token) {
    throw new ChatApiError(401, 'Authentication required');
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ChatApiError(
      response.status,
      errorData.detail || errorData.error || 'An error occurred'
    );
  }

  return response;
}

/**
 * Send a chat message to the AI assistant.
 */
export async function sendChatMessage(
  userId: string,
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const request: ChatRequest = {
    message,
    conversation_id: conversationId,
  };

  const response = await fetchWithAuth(
    `${API_BASE}/api/chat/${userId}`,
    {
      method: 'POST',
      body: JSON.stringify(request),
    }
  );

  return response.json();
}

/**
 * Get list of user's conversations.
 */
export async function getConversations(
  userId: string,
  limit: number = 10
): Promise<Conversation[]> {
  const response = await fetchWithAuth(
    `${API_BASE}/api/chat/${userId}/conversations?limit=${limit}`
  );

  return response.json();
}

/**
 * Get messages from a specific conversation.
 */
export async function getConversationMessages(
  userId: string,
  conversationId: string,
  limit: number = 50
): Promise<Message[]> {
  const response = await fetchWithAuth(
    `${API_BASE}/api/chat/${userId}/conversations/${conversationId}?limit=${limit}`
  );

  return response.json();
}

export { ChatApiError };
