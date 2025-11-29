/**
 * Sidebar - Chat history sidebar (ChatGPT-style)
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { SessionItem } from './SessionItem';
import { sessionsAPI, quizAPI, QuizHistory } from '../../services/api';
import { ChatSession, TaskType } from '../../types';

interface SidebarProps {
  currentSessionId: string | null;
  taskType?: TaskType; // Filter sessions by task type
  colorScheme?: string; // Theme color for the task
  onNewChat: () => void;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
}

const colorSchemes: Record<string, { bg: string; hover: string }> = {
  blue: { bg: 'bg-blue-600', hover: 'hover:bg-blue-700' },
  green: { bg: 'bg-green-600', hover: 'hover:bg-green-700' },
  orange: { bg: 'bg-orange-600', hover: 'hover:bg-orange-700' },
  purple: { bg: 'bg-purple-600', hover: 'hover:bg-purple-700' },
};

export const Sidebar: React.FC<SidebarProps> = ({
  currentSessionId,
  taskType,
  colorScheme = 'blue',
  onNewChat,
  onSelectSession,
  onDeleteSession,
}) => {
  // Fetch sessions or quiz history based on task type
  const { data: sessions = [], isLoading, refetch } = useQuery({
    queryKey: ['sessions', taskType],
    queryFn: async () => {
      let fetchedSessions: ChatSession[] = [];
      
      if (taskType === 'quiz') {
        // Fetch quiz history and convert to session format
        const quizzes = await quizAPI.getQuizHistory();
        fetchedSessions = quizzes.map((quiz: QuizHistory) => ({
          id: quiz.id,
          title: quiz.topic || `Quiz ${quiz.num_questions} câu (${quiz.question_type})`,
          created_at: quiz.created_at,
          updated_at: quiz.created_at,
        })) as ChatSession[];
      } else {
        // Fetch chat sessions - get all sessions without limit
        fetchedSessions = await sessionsAPI.getSessions('default_user', taskType);
      }
      
      // Sort sessions by updated_at (newest first) to show recent chats at the top
      return fetchedSessions.sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at).getTime();
        const dateB = new Date(b.updated_at || b.created_at).getTime();
        return dateB - dateA; // Descending order (newest first)
      });
    },
    refetchInterval: 30000, // Refetch every 30s
  });

  const handleDelete = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (window.confirm('Delete this conversation?')) {
      onDeleteSession(sessionId);
      refetch(); // Refresh list after delete
    }
  };

  // Get button text based on task type
  const getNewButtonText = () => {
    switch (taskType) {
      case 'quiz':
        return 'New Quiz';
      case 'video_summary':
        return 'New Video';
      default:
        return 'New Chat';
    }
  };

  // Group sessions by date and sort within each group
  const groupedSessions = React.useMemo(() => {
    const groups: {
      today: ChatSession[];
      yesterday: ChatSession[];
      older: ChatSession[];
    } = {
      today: [],
      yesterday: [],
      older: [],
    };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    sessions.forEach((session) => {
      const sessionDate = new Date(session.created_at);
      const sessionDay = new Date(
        sessionDate.getFullYear(),
        sessionDate.getMonth(),
        sessionDate.getDate()
      );

      if (sessionDay.getTime() === today.getTime()) {
        groups.today.push(session);
      } else if (sessionDay.getTime() === yesterday.getTime()) {
        groups.yesterday.push(session);
      } else {
        groups.older.push(session);
      }
    });

    // Sort each group by updated_at (newest first) to ensure proper ordering
    const sortByDate = (a: ChatSession, b: ChatSession) => {
      const dateA = new Date(a.updated_at || a.created_at).getTime();
      const dateB = new Date(b.updated_at || b.created_at).getTime();
      return dateB - dateA; // Descending order (newest first)
    };

    groups.today.sort(sortByDate);
    groups.yesterday.sort(sortByDate);
    groups.older.sort(sortByDate);

    return groups;
  }, [sessions]);

  const buttonColors = colorSchemes[colorScheme] || colorSchemes.blue;

  return (
    <div className="w-[280px] h-screen bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-gray-200 dark:border-gray-700">
        <button
          className={`${buttonColors.bg} ${buttonColors.hover} text-white text-sm w-full py-2 px-4 rounded-md flex items-center justify-center gap-2 transition-colors`}
          onClick={onNewChat}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          {getNewButtonText()}
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-2">
        {isLoading ? (
          <div className="h-[200px] flex items-center justify-center">
            <svg
              className="animate-spin h-6 w-6 text-blue-500"
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
        ) : sessions.length === 0 ? (
          <div className="h-[200px] flex items-center justify-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No conversations yet
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Today */}
            {groupedSessions.today.length > 0 && (
              <div>
                <p className="text-xs font-bold text-gray-500 dark:text-gray-400 mb-2 px-2">
                  Today
                </p>
                <div className="space-y-1">
                  {groupedSessions.today.map((session) => (
                    <SessionItem
                      key={session.id}
                      session={session}
                      isActive={session.id === currentSessionId}
                      colorScheme={colorScheme}
                      onClick={() => onSelectSession(session.id)}
                      onDelete={(e) => handleDelete(e, session.id)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Yesterday */}
            {groupedSessions.yesterday.length > 0 && (
              <div>
                {groupedSessions.today.length > 0 && (
                  <hr className="border-gray-200 dark:border-gray-700 my-2" />
                )}
                <p className="text-xs font-bold text-gray-500 dark:text-gray-400 mb-2 px-2 mt-2">
                  Yesterday
                </p>
                <div className="space-y-1">
                  {groupedSessions.yesterday.map((session) => (
                    <SessionItem
                      key={session.id}
                      session={session}
                      isActive={session.id === currentSessionId}
                      colorScheme={colorScheme}
                      onClick={() => onSelectSession(session.id)}
                      onDelete={(e) => handleDelete(e, session.id)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Older */}
            {groupedSessions.older.length > 0 && (
              <div>
                {(groupedSessions.today.length > 0 ||
                  groupedSessions.yesterday.length > 0) && (
                  <hr className="border-gray-200 dark:border-gray-700 my-2" />
                )}
                <p className="text-xs font-bold text-gray-500 dark:text-gray-400 mb-2 px-2 mt-2">
                  Older
                </p>
                <div className="space-y-1">
                  {groupedSessions.older.map((session) => (
                    <SessionItem
                      key={session.id}
                      session={session}
                      isActive={session.id === currentSessionId}
                      colorScheme={colorScheme}
                      onClick={() => onSelectSession(session.id)}
                      onDelete={(e) => handleDelete(e, session.id)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
          YouTubeLM: One-for-all AI Assistant 
        </p>
      </div>
    </div>
  );
};
