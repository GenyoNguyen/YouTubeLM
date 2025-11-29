/**
 * SessionItem - Individual session in sidebar
 */
import React from 'react';
import { ChatSession } from '../../types';

interface SessionItemProps {
  session: ChatSession;
  isActive: boolean;
  colorScheme?: string;
  onClick: () => void;
  onDelete: (e: React.MouseEvent) => void;
}

const colorSchemes: Record<string, { bg: string; hover: string; text: string }> = {
  blue: { bg: 'bg-blue-50', hover: 'bg-blue-100', text: 'text-blue-700' },
  green: { bg: 'bg-green-50', hover: 'bg-green-100', text: 'text-green-700' },
  orange: { bg: 'bg-orange-50', hover: 'bg-orange-100', text: 'text-orange-700' },
  purple: { bg: 'bg-purple-50', hover: 'bg-purple-100', text: 'text-purple-700' },
};

export const SessionItem: React.FC<SessionItemProps> = ({
  session,
  isActive,
  colorScheme = 'blue',
  onClick,
  onDelete,
}) => {
  const colors = colorSchemes[colorScheme] || colorSchemes.blue;

  return (
    <div
      className={`px-3 py-2 cursor-pointer rounded-md flex items-center justify-between gap-2 transition-colors ${
        isActive ? colors.bg : 'bg-transparent'
      } ${isActive ? `hover:${colors.hover}` : 'hover:bg-gray-100 dark:hover:bg-gray-800'}`}
      onClick={onClick}
    >
      <div className="flex-1 overflow-hidden">
        <p
          className={`text-sm ${isActive ? 'font-bold' : 'font-medium'} line-clamp-2 ${
            isActive ? colors.text : 'text-gray-800 dark:text-gray-200'
          }`}
        >
          {session.title || 'Untitled Session'}
        </p>
      </div>

      <button
        onClick={onDelete}
        className="opacity-60 hover:opacity-100 transition-opacity p-1 text-red-600 hover:text-red-700"
        aria-label="Delete session"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  );
};
