/**
 * API Client for YouTubeLM Backend
 * Supports REST endpoints and SSE (Server-Sent Events) for streaming
 */

// Base URL - use environment variable or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================================================
// Types
// ============================================================================

export interface VideoInfo {
  video_id: string;
  title: string;
  chapter: string;
  video_url: string;
  duration: string;
  duration_seconds: number;
}

export interface Source {
  index: number;
  video_id: string;
  video_title: string;
  video_url: string;
  start_time: number;
  end_time: number;
  text: string;
  score: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  created_at: string;
}

export interface ChatSession {
  id: string;
  task_type: 'qa' | 'video_summary' | 'quiz';
  title: string;
  created_at: string;
  updated_at: string;
}

export interface SSEEvent {
  type: 'token' | 'sources' | 'metadata' | 'done' | 'error' | 'cached';
  content?: string;
  sources?: Source[];
  video_info?: VideoInfo;
  session_id?: string;
  error?: string;
}

// ============================================================================
// Helper Functions
// ============================================================================

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Stream SSE events from backend
 */
async function* streamSSE(
  endpoint: string,
  body: Record<string, unknown>
): AsyncGenerator<SSEEvent> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          yield data as SSEEvent;
        } catch {
          // Skip invalid JSON
        }
      }
    }
  }
}

// ============================================================================
// API Client
// ============================================================================

export const apiClient = {
  // ==========================================================================
  // Health Check
  // ==========================================================================
  
  health: {
    check: () => fetchAPI<{ status: string }>('/api/health'),
  },

  // ==========================================================================
  // Q&A Endpoints
  // ==========================================================================
  
  qa: {
    /**
     * Ask a question with streaming response
     */
    ask: (params: {
      query: string;
      chapters?: string[];
      session_id?: string;
    }) => streamSSE('/api/qa/ask', params),

    /**
     * Followup question in existing session
     */
    followup: (params: {
      session_id: string;
      query: string;
      chapters?: string[];
    }) => streamSSE('/api/qa/followup', params),

    /**
     * Get chat history for a session
     */
    getHistory: (sessionId: string) =>
      fetchAPI<ChatMessage[]>(`/api/qa/history/${sessionId}`),
  },

  // ==========================================================================
  // Video Summary Endpoints
  // ==========================================================================
  
  videoSummary: {
    /**
     * Summarize a video with streaming response
     */
    summarize: (params: {
      video_id: string;
      summary_type?: 'detailed' | 'quick';
      session_id?: string;
      force_regenerate?: boolean;
    }) => streamSSE('/api/video-summary/summarize', params),

    /**
     * Summarize a chapter/playlist
     */
    summarizeChapter: (params: {
      chapter: string;
      session_id?: string;
    }) => streamSSE('/api/video-summary/summarize-chapter', params),

    /**
     * List available videos
     */
    listVideos: (chapter?: string) =>
      fetchAPI<VideoInfo[]>(`/api/video-summary/videos${chapter ? `?chapter=${chapter}` : ''}`),

    /**
     * List available chapters
     */
    listChapters: () =>
      fetchAPI<{ name: string; video_count: number }[]>('/api/video-summary/chapters'),
  },

  // ==========================================================================
  // Quiz Endpoints
  // ==========================================================================
  
  quiz: {
    /**
     * Generate quiz questions
     */
    generate: (params: {
      video_ids: string[];
      question_type: 'mcq' | 'true_false' | 'fill_blank';
      num_questions: number;
      difficulty?: 'easy' | 'medium' | 'hard';
    }) => streamSSE('/api/quiz/generate', params),

    /**
     * Submit quiz answer
     */
    submitAnswer: (params: {
      question_id: string;
      answer: string;
    }) => fetchAPI<{ correct: boolean; explanation: string }>('/api/quiz/submit', {
      method: 'POST',
      body: JSON.stringify(params),
    }),
  },

  // ==========================================================================
  // Session Management
  // ==========================================================================
  
  sessions: {
    /**
     * List all sessions
     */
    list: (taskType?: string) =>
      fetchAPI<ChatSession[]>(`/api/sessions${taskType ? `?task_type=${taskType}` : ''}`),

    /**
     * Get session by ID
     */
    get: (sessionId: string) =>
      fetchAPI<ChatSession>(`/api/sessions/${sessionId}`),

    /**
     * Delete session
     */
    delete: (sessionId: string) =>
      fetchAPI<void>(`/api/sessions/${sessionId}`, { method: 'DELETE' }),
  },
};

export default apiClient;
