/**
 * ChatInput component with mode switcher and chapter filter
 */
import React, { useState, useEffect } from 'react';
import { TaskType } from '../../types';
import { chaptersAPI, videoSummaryAPI, type VideoInfo } from '../../services/api';

interface ChatInputProps {
  currentMode: TaskType;
  colorScheme?: string;
  onModeChange: (mode: TaskType) => void;
  onSend: (message: string) => void;
  isStreaming: boolean;
  selectedChapters: string[];
  onChaptersChange: (chapters: string[]) => void;
  selectedVideo: string | null;
  onVideoChange: (videoId: string | null) => void;
  // Quiz-specific props
  quizQuestionType?: string;
  onQuizQuestionTypeChange?: (type: string) => void;
  quizNumQuestions?: number;
  onQuizNumQuestionsChange?: (num: number) => void;
  quizVideoUrl?: string;
  onQuizVideoUrlChange?: (url: string) => void;
}

const MODE_LABELS: Record<TaskType, string> = {
  qa: 'Q&A',
  video_summary: 'Video Summary',
  quiz: 'Quiz',
};

const colorSchemes: Record<string, { bg: string; hover: string }> = {
  blue: { bg: 'bg-blue-600', hover: 'hover:bg-blue-700' },
  green: { bg: 'bg-green-600', hover: 'hover:bg-green-700' },
  orange: { bg: 'bg-orange-600', hover: 'hover:bg-orange-700' },
  purple: { bg: 'bg-purple-600', hover: 'hover:bg-purple-700' },
};

export const ChatInput: React.FC<ChatInputProps> = ({
  currentMode,
  colorScheme = 'blue',
  onModeChange,
  onSend,
  isStreaming,
  selectedChapters,
  onChaptersChange,
  selectedVideo,
  onVideoChange,
  quizQuestionType = 'mcq',
  onQuizQuestionTypeChange,
  quizNumQuestions = 5,
  onQuizNumQuestionsChange,
  quizVideoUrl = '',
  onQuizVideoUrlChange,
}) => {
  const [input, setInput] = useState('');
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [loadingVideos, setLoadingVideos] = useState(false);
  const [isChapterMenuOpen, setIsChapterMenuOpen] = useState(false);
  const [isModeHovered, setIsModeHovered] = useState(false);

  // Get available chapters (hardcoded from chapters_urls.json ground truth)
  const availableChapters = chaptersAPI.getChapters();

  // Load videos when video_summary mode is active
  useEffect(() => {
    if (currentMode === 'video_summary' && videos.length === 0) {
      setLoadingVideos(true);
      videoSummaryAPI
        .getVideos()
        .then((list) => {
          // Sort by chapter then title using localeCompare for correct Vietnamese ordering
          list.sort((a, b) => {
            const chapterCompare = a.chapter.localeCompare(b.chapter, 'vi');
            return chapterCompare !== 0
              ? chapterCompare
              : a.title.localeCompare(b.title, 'vi');
          });
          setVideos(list);
        })
        .catch(console.error)
        .finally(() => setLoadingVideos(false));
    }
  }, [currentMode, videos.length]);

  const handleSend = () => {
    if (currentMode === 'video_summary') {
      // For video_summary, send button triggers summarization
      if (selectedVideo && !isStreaming) {
        onSend('__VIDEO_SUMMARY_REGENERATE__'); // Special marker to skip user message
      }
    } else if (currentMode === 'quiz') {
      // For quiz, send button triggers quiz generation
      if (!isStreaming) {
        // Pass the query (optional) via the onSend handler
        onSend(input.trim() || '__QUIZ_GENERATE__');
        setInput('');
      }
    } else if (input.trim() && !isStreaming) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChapterToggle = (chapter: string) => {
    if (selectedChapters.includes(chapter)) {
      onChaptersChange(selectedChapters.filter((c) => c !== chapter));
    } else {
      onChaptersChange([...selectedChapters, chapter]);
    }
  };

  const handleModeCycle = () => {
    // Define all modes in order
    const modes: TaskType[] = ['qa', 'video_summary', 'quiz'];
    
    // Find current mode index, default to 0 if not found
    const currentIndex = modes.indexOf(currentMode);
    const nextIndex = currentIndex >= 0 
      ? (currentIndex + 1) % modes.length 
      : 0;
    
    onModeChange(modes[nextIndex]);
  };

  const buttonColors = colorSchemes[colorScheme] || colorSchemes.blue;
  const allModes: TaskType[] = ['qa', 'video_summary', 'quiz'];

  return (
    <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex items-center gap-2 flex-wrap">
      {/* Mode Switcher */}
      <div 
        className="relative"
        onMouseEnter={() => setIsModeHovered(true)}
        onMouseLeave={() => setIsModeHovered(false)}
      >
        <button
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md min-w-[180px] flex items-center justify-center gap-2 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={handleModeCycle}
          disabled={isStreaming}
          title="Click to cycle through modes"
        >
          {MODE_LABELS[currentMode]}
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
            />
          </svg>
        </button>
        {isModeHovered && !isStreaming && (
          <div 
            className="absolute bottom-full mb-1 z-30 w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg"
          >
            <div className="p-2">
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-2 py-1 mb-1">
                Available Modes:
              </p>
              {allModes.map((mode) => (
                <button
                  key={mode}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    onModeChange(mode);
                    setIsModeHovered(false);
                  }}
                  className={`w-full text-left px-3 py-1.5 text-sm rounded cursor-pointer transition-colors ${
                    mode === currentMode
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 font-medium'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                >
                  {MODE_LABELS[mode]}
                  {mode === currentMode && (
                    <span className="ml-2 text-xs">(current)</span>
                  )}
                </button>
              ))}
              <p className="text-xs text-gray-500 dark:text-gray-400 px-2 py-1 mt-1 border-t border-gray-200 dark:border-gray-600 pt-1">
                Click a mode to select, or click button to cycle
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Chapter Filter (for qa and quiz) */}
        {(currentMode === 'qa' ||
        currentMode === 'quiz') && (
        <div className="relative">
          <button
            className={`p-2 rounded-md border ${
              selectedChapters.length > 0
                ? `${buttonColors.bg} text-white border-transparent`
                : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200'
            }`}
            onClick={() => setIsChapterMenuOpen(!isChapterMenuOpen)}
            aria-label="Filter chapters"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </button>
          {isChapterMenuOpen && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setIsChapterMenuOpen(false)}
              />
              <div className="absolute z-20 mt-1 right-0 w-64 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-[300px] overflow-y-auto">
                <div className="p-2 space-y-1">
                  <p className="font-bold text-sm px-2 py-1">Chọn chương:</p>
                  {selectedChapters.length > 0 && (
                    <button
                      className="text-xs px-2 py-1 text-red-600 hover:bg-red-50 dark:hover:bg-red-900 rounded"
                      onClick={() => {
                        onChaptersChange([]);
                        setIsChapterMenuOpen(false);
                      }}
                    >
                      Clear all
                    </button>
                  )}
                  {availableChapters.map((chapter) => (
                    <label
                      key={chapter}
                      className="flex items-center px-2 py-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedChapters.includes(chapter)}
                        onChange={() => handleChapterToggle(chapter)}
                        className="mr-2"
                      />
                      <span className="text-sm">{chapter}</span>
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Quiz Options (for quiz mode) */}
      {currentMode === 'quiz' && (
        <>
          <select
            value={quizQuestionType}
            onChange={(e) => onQuizQuestionTypeChange?.(e.target.value)}
            disabled={isStreaming}
            className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 min-w-[140px]"
          >
            <option value="mcq">MCQ</option>
            <option value="open_ended">Open-ended</option>
            <option value="mixed">Mixed</option>
          </select>
          <div className="flex items-center border border-gray-300 dark:border-gray-600 rounded-md min-w-[100px]">
            <input
              type="number"
              value={quizNumQuestions}
              onChange={(e) =>
                onQuizNumQuestionsChange?.(
                  isNaN(parseInt(e.target.value)) ? 5 : parseInt(e.target.value)
                )
              }
              min={1}
              max={20}
              disabled={isStreaming}
              className="w-full px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-l-md border-0 focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex flex-col border-l border-gray-300 dark:border-gray-600">
              <button
                onClick={() =>
                  onQuizNumQuestionsChange?.(
                    Math.min(20, quizNumQuestions + 1)
                  )
                }
                disabled={isStreaming || quizNumQuestions >= 20}
                className="px-2 py-0.5 text-xs border-b border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600"
              >
                ▲
              </button>
              <button
                onClick={() =>
                  onQuizNumQuestionsChange?.(
                    Math.max(1, quizNumQuestions - 1)
                  )
                }
                disabled={isStreaming || quizNumQuestions <= 1}
                className="px-2 py-0.5 text-xs hover:bg-gray-100 dark:hover:bg-gray-600"
              >
                ▼
              </button>
            </div>
          </div>
          <input
            type="text"
            value={quizVideoUrl}
            onChange={(e) => onQuizVideoUrlChange?.(e.target.value)}
            placeholder="Enter video URL (optional)..."
            disabled={isStreaming}
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </>
      )}

      {/* Video Selection (for video_summary) */}
      {currentMode === 'video_summary' && (
        <input
          type="text"
          value={selectedVideo || ''}
          onChange={(e) => onVideoChange(e.target.value || null)}
          placeholder="Enter video URL..."
          disabled={isStreaming || loadingVideos}
          className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        
      )}
      {currentMode === 'qa' && (
        <>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Enter topic or question (e.g., 'ResNet architecture')..."
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
        </>
      )}


      {/* Send/Regenerate/Generate Button */}
      <button
        onClick={handleSend}
        disabled={
          currentMode === 'video_summary'
            ? !selectedVideo || isStreaming
            : currentMode === 'quiz'
            ? isStreaming
            : currentMode === 'qa'
            ? !input.trim() || isStreaming
            : isStreaming
        }
        className={`${buttonColors.bg} ${buttonColors.hover} text-white px-4 py-2 rounded-md font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 ${
          currentMode === 'quiz' ? 'min-w-[140px]' : ''
        }`}
      >
        {isStreaming ? (
          <>
            <svg
              className="animate-spin h-4 w-4"
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
            {currentMode === 'video_summary'
              ? 'Regenerating...'
              : currentMode === 'quiz'
              ? 'Generating...'
              : 'Sending...'}
          </>
        ) : (
          <>
            {currentMode === 'video_summary' && (
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            )}
            {currentMode === 'video_summary'
              ? 'Regenerate'
              : currentMode === 'quiz'
              ? 'Generate Quiz'
              : 'Send'}
          </>
        )}
      </button>
    </div>
  );
};
