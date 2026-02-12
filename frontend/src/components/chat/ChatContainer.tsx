'use client';

/**
 * ChatKit container component - wraps OpenAI ChatKit.
 * Primary interface for conversational task management.
 */

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/useAuth';
import { EmptyState } from './EmptyState';
import { Spinner } from '@/components/ui/Spinner';

// ChatKit web component type declarations
interface ChatKitOptions {
  api: {
    url: string;
    domainKey?: string;
  };
  conversationId?: string;
  onConversationChange?: (conversationId: string) => void;
}

interface ChatKitElement extends HTMLElement {
  setOptions: (options: ChatKitOptions) => void;
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace JSX {
    interface IntrinsicElements {
      'openai-chatkit': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          class?: string;
        },
        HTMLElement
      >;
    }
  }
}

export interface ChatContainerProps {
  /** User ID for chat session */
  userId?: string;
  /** Conversation ID (optional, creates new if not provided) */
  conversationId?: string;
  /** Callback when conversation changes */
  onConversationChange?: (conversationId: string) => void;
  /** Additional CSS classes */
  className?: string;
}

export function ChatContainer({
  userId,
  conversationId,
  onConversationChange,
  className,
}: ChatContainerProps) {
  const { user, isLoading: authLoading } = useAuth();
  const [chatKitReady, setChatKitReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const effectiveUserId = userId || user?.id;

  // Check if ChatKit script is loaded
  useEffect(() => {
    const checkChatKit = () => {
      if (typeof window !== 'undefined' && 'customElements' in window) {
        const isDefined = customElements.get('openai-chatkit');
        if (isDefined) {
          setChatKitReady(true);
        } else {
          // Wait for custom element to be defined
          customElements.whenDefined('openai-chatkit').then(() => {
            setChatKitReady(true);
          }).catch(() => {
            setError('Failed to load ChatKit');
          });
        }
      }
    };

    // Check immediately and after a delay
    checkChatKit();
    const timeout = setTimeout(checkChatKit, 1000);
    return () => clearTimeout(timeout);
  }, []);

  // Initialize ChatKit with configuration
  useEffect(() => {
    if (!chatKitReady || !effectiveUserId) return;

    const chatkit = document.querySelector('openai-chatkit');
    if (chatkit && 'setOptions' in chatkit) {
      try {
        // Use the backend API URL from environment
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        (chatkit as ChatKitElement).setOptions({
          api: {
            url: `${apiBaseUrl}/api/chat/${effectiveUserId}`,
            // For local development, use domain key
            domainKey: process.env.NODE_ENV === 'development' ? 'local-dev' : undefined,
          },
          conversationId,
          onConversationChange,
        });
      } catch (err) {
        console.error('Failed to configure ChatKit:', err);
        setError('Failed to configure chat');
      }
    }
  }, [chatKitReady, effectiveUserId, conversationId, onConversationChange]);

  // Loading state
  if (authLoading) {
    return (
      <div className={cn('flex h-full items-center justify-center', className)}>
        <Spinner size="lg" label="Loading..." />
      </div>
    );
  }

  // Not authenticated
  if (!effectiveUserId) {
    return (
      <div className={cn('flex h-full items-center justify-center', className)}>
        <EmptyState
          title="Sign in to chat"
          description="Please sign in to start managing your tasks with AI"
        />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={cn('flex h-full items-center justify-center', className)}>
        <EmptyState
          title="Chat unavailable"
          description={error}
        />
      </div>
    );
  }

  // ChatKit not ready yet
  if (!chatKitReady) {
    return (
      <div className={cn('flex h-full items-center justify-center', className)}>
        <Spinner size="lg" label="Loading chat..." />
      </div>
    );
  }

  return (
    <div className={cn('flex h-full flex-col', className)}>
      {/* @ts-expect-error - openai-chatkit is a web component loaded via script tag */}
      <openai-chatkit class="flex-1" />
    </div>
  );
}
