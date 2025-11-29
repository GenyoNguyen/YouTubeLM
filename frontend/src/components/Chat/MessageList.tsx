/**
 * MessageList component - scrollable list of messages
 */
import React, { useEffect, useRef } from 'react';
import { Message } from './Message';
import { ChatMessage } from '../../types';

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;
  onSeekVideo?: (timestamp: number) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isStreaming,
  streamingContent,
  onSeekVideo,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div className="flex-1 w-full h-full overflow-y-auto overflow-x-hidden p-4">
      <div className="space-y-0 flex flex-col w-full">
        {/* Render all messages */}
        {messages.map((message) => (
          <Message key={message.id} message={message} onSeekVideo={onSeekVideo} />
        ))}

        {/* Show loading indicator when streaming starts (before first token) */}
        {isStreaming && !streamingContent && (
          <div className="max-w-[75%] bg-gray-100 dark:bg-gray-700 px-4 py-3 rounded-lg shadow-sm mb-4 flex items-center gap-2">
            <svg
              className="animate-spin h-4 w-4 text-blue-500"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span className="text-sm text-gray-600 dark:text-gray-300">
              Generating response...
            </span>
          </div>
        )}

        {/* Show streaming message */}
        {isStreaming && streamingContent && (
          <div className="max-w-[75%] bg-gray-100 dark:bg-gray-700 text-black dark:text-white px-4 py-3 rounded-lg shadow-sm mb-4">
            <div className="whitespace-pre-wrap">{streamingContent}</div>
            <svg
              className="animate-spin h-4 w-4 text-blue-500 mt-2"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
