/**
 * SourcesModal - Popup showing all sources with video names and clickable timestamps
 */
import React from 'react';
import { SourceReference } from '../../types';

interface SourcesModalProps {
  isOpen: boolean;
  onClose: () => void;
  sources: SourceReference[];
}

export const SourcesModal: React.FC<SourcesModalProps> = ({
  isOpen,
  onClose,
  sources,
}) => {
  if (!isOpen) return null;

  const handleSourceClick = (source: SourceReference) => {
    const url = `${source.video_url}&t=${source.start_time}s`;
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Nguồn tham khảo ({sources.length} video)
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-4 overflow-y-auto flex-1">
          <div className="space-y-3">
            {sources.map((source, idx) => (
              <div
                key={idx}
                className="p-4 border border-gray-200 dark:border-gray-700 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-blue-300 transition-all"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm font-medium px-2 py-1 rounded">
                    [{source.index}]
                  </span>
                  <span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs font-medium px-2 py-1 rounded">
                    {source.chapter}
                  </span>
                </div>

                <p className="font-semibold text-sm mb-2 text-gray-900 dark:text-white line-clamp-2">
                  {source.video_title}
                </p>

                <button
                  onClick={() => handleSourceClick(source)}
                  className="text-blue-500 dark:text-blue-400 font-medium text-sm cursor-pointer hover:underline flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                  Xem tại {formatTime(source.start_time)} - {formatTime(source.end_time)}
                </button>

                {source.text && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 italic line-clamp-2">
                    "{source.text.slice(0, 150)}..."
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
