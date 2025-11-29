/**
 * VideoSummaryDisplay component - displays video summary spanning full width
 */
import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage, SourceReference } from '../../types';
import { SourcesModal } from './SourcesModal';

interface VideoSummaryDisplayProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;
  onSeekVideo?: (timestamp: number) => void;
}

export const VideoSummaryDisplay: React.FC<VideoSummaryDisplayProps> = ({
  messages,
  isStreaming,
  streamingContent,
  onSeekVideo,
}) => {
  const contentEndRef = useRef<HTMLDivElement>(null);
  const [isSourcesModalOpen, setIsSourcesModalOpen] = React.useState(false);

  // Auto-scroll to bottom when content changes
  useEffect(() => {
    contentEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  // Handle citation clicks
  const handleCitationClick = (index: number, sources?: SourceReference[]) => {
    if (!sources || index > sources.length) return;

    const source = sources[index - 1]; // Citations are 1-indexed
    if (!source) return;

    // Seek in embedded player
    if (onSeekVideo) {
      onSeekVideo(source.start_time);
    } else {
      // Otherwise, open YouTube URL with timestamp
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

  // Render content with citations
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
        const processedChildren = React.Children.map(children, (child) => {
          if (typeof child === 'string') {
            return processTextWithCitations(child, sources);
          }
          return child;
        });
        return <p {...props}>{processedChildren}</p>;
      },
      li: ({ children, ...props }: any) => {
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

  // Get the latest summary message (last assistant message)
  const summaryMessage =
    messages.length > 0 ? messages[messages.length - 1] : null;

  return (
    <>
      <div className="flex-1 w-full h-full overflow-y-auto overflow-x-hidden p-6 bg-white dark:bg-gray-800 text-gray-800 dark:text-white">
        <div className="space-y-4 flex flex-col w-full">
          {/* Display completed summary */}
          {summaryMessage && summaryMessage.role === 'assistant' && (
            <>
              {renderContentWithCitations(
                summaryMessage.content,
                summaryMessage.sources
              )}

              {/* Show sources button if available */}
              {summaryMessage.sources && summaryMessage.sources.length > 0 && (
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => setIsSourcesModalOpen(true)}
                    className="bg-green-600 hover:bg-green-700 text-white text-xs h-7 px-4 rounded transition-colors"
                  >
                    {summaryMessage.sources.length} nguồn
                  </button>
                </div>
              )}
            </>
          )}

          {/* Show loading indicator when streaming starts (before first token) */}
          {isStreaming && !streamingContent && (
            <div className="flex items-center gap-2">
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
                Generating summary...
              </span>
            </div>
          )}

          {/* Show streaming content */}
          {isStreaming && streamingContent && (
            <div>
              <div className="whitespace-pre-wrap markdown-content">
                {streamingContent}
              </div>
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
          <div ref={contentEndRef} />
        </div>
      </div>

      {/* Sources Modal */}
      {summaryMessage?.sources && summaryMessage.sources.length > 0 && (
        <SourcesModal
          isOpen={isSourcesModalOpen}
          onClose={() => setIsSourcesModalOpen(false)}
          sources={summaryMessage.sources}
        />
      )}
    </>
  );
};
