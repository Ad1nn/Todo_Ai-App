/**
 * React hook for managing chat state and interactions.
 */

import { useCallback, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import {
  ChatApiError,
  getConversationMessages,
  sendChatMessage,
} from '@/services/chatService';
import type { ChatState, Message } from '@/types/chat';

interface UseChatReturn extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  loadConversation: (conversationId: string) => Promise<void>;
  clearChat: () => void;
  startNewChat: () => void;
}

export function useChat(): UseChatReturn {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!user?.id) {
        setError('You must be logged in to chat');
        return;
      }

      if (!content.trim()) {
        return;
      }

      setIsLoading(true);
      setError(null);

      // Add user message optimistically
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content: content.trim(),
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await sendChatMessage(
          user.id,
          content.trim(),
          conversationId || undefined
        );

        // Update conversation ID if this is a new conversation
        if (!conversationId) {
          setConversationId(response.conversation_id);
        }

        // Add assistant response
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.response,
          tool_calls: response.tool_calls,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        // Remove optimistic user message on error
        setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));

        if (err instanceof ChatApiError) {
          setError(err.detail);
        } else {
          setError('Failed to send message. Please try again.');
        }
      } finally {
        setIsLoading(false);
      }
    },
    [user?.id, conversationId]
  );

  const loadConversation = useCallback(
    async (convId: string) => {
      if (!user?.id) {
        setError('You must be logged in to load conversation');
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const loadedMessages = await getConversationMessages(user.id, convId);
        setMessages(loadedMessages);
        setConversationId(convId);
      } catch (err) {
        if (err instanceof ChatApiError) {
          setError(err.detail);
        } else {
          setError('Failed to load conversation. Please try again.');
        }
      } finally {
        setIsLoading(false);
      }
    },
    [user?.id]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  const startNewChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    conversationId,
    isLoading,
    error,
    sendMessage,
    loadConversation,
    clearChat,
    startNewChat,
  };
}
