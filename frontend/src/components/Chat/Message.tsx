/**
 * Message component with citation support
 */
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage, SourceReference } from '../../types';
import { SourcesModal } from './SourcesModal';

interface MessageProps {
  message: ChatMessage;
  onSeekVideo?: (timestamp: number) => void;
}

export const Message: React.FC<MessageProps> = ({ message, onSeekVideo }) => {
  const isUser = message.role === 'user';
  const [isSourcesModalOpen, setIsSourcesModalOpen] = useState(false);

  // Handle citation clicks
  const handleCitationClick = (index: number, sources?: SourceReference[]) => {
    if (!sources || index > sources.length) return;

    const source = sources[index - 1]; // Citations are 1-indexed
    if (!source) return;

    // If onSeekVideo callback provided (for video_summary), seek in embedded player
    if (onSeekVideo) {
      onSeekVideo(source.start_time);
    } else {
      // Otherwise, open YouTube URL with timestamp (for other modes)
      const url = `${source.video_url}&t=${source.start_time}s`;
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  // Helper function to process text and replace citations with clickable links
  const processTextWithCitations = (text: string, sources: SourceReference[]) => {
    const citationRegex = /\[(\d+)\]/g;
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let match;

    while ((match = citationRegex.exec(text)) !== null) {
      // Add text before citation
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }

      // Add clickable citation
      const citationIndex = parseInt(match[1]);
      parts.push(
        <button
          key={`citation-${match.index}`}
          className="text-blue-500 dark:text-blue-300 font-bold cursor-pointer hover:underline inline"
          onClick={() => handleCitationClick(citationIndex, sources)}
        >
          [{citationIndex}]
        </button>
      );

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts.length > 0 ? <>{parts}</> : text;
  };

  // Replace citations [1], [2], etc. with clickable links
  const renderContentWithCitations = (content: string, sources?: SourceReference[]) => {
    if (!sources || sources.length === 0) {
      return (
        <div className="markdown-content">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      );
    }

    // Custom text renderer to replace citations inline
    const components = {
      p: ({ children, ...props }: any) => {
        // Process text nodes within paragraphs
        const processedChildren = React.Children.map(children, (child) => {
          if (typeof child === 'string') {
            return processTextWithCitations(child, sources);
          }
          return child;
        });
        return <p {...props}>{processedChildren}</p>;
      },
      li: ({ children, ...props }: any) => {
        // Process text nodes within list items
        const processedChildren = React.Children.map(children, (child) => {
          if (typeof child === 'string') {
            return processTextWithCitations(child, sources);
          }
          return child;
        });
        return <li {...props}>{processedChildren}</li>;
      },
    };

    return (
      <div className="markdown-content">
        <ReactMarkdown components={components}>{content}</ReactMarkdown>
      </div>
    );
  };

  return (
    <>
      <div
        className={`flex items-start ${
          isUser ? 'justify-end' : 'justify-start'
        } w-full mb-4`}
      >
        <div
          className={`max-w-[75%] px-4 py-3 rounded-lg shadow-sm ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-black dark:text-white'
          }`}
        >
          <div className="space-y-2">
            {/* Message content */}
            <div>{renderContentWithCitations(message.content, message.sources)}</div>

            {/* Show sources button if available (only for assistant messages) */}
            {!isUser && message.sources && message.sources.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-1">
                <button
                  onClick={() => setIsSourcesModalOpen(true)}
                  className="bg-green-600 hover:bg-green-700 text-white text-xs h-[26px] px-3 rounded transition-all hover:-translate-y-px"
                >
                  {message.sources.length} nguồn
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sources Modal */}
      {message.sources && message.sources.length > 0 && (
        <SourcesModal
          isOpen={isSourcesModalOpen}
          onClose={() => setIsSourcesModalOpen(false)}
          sources={message.sources}
        />
      )}
    </>
  );
};
