/**
 * React hooks for API interactions
 */
import { useState, useCallback } from 'react';
import { apiClient, SSEEvent, Source, VideoInfo } from '../services/api';

// ============================================================================
// Types
// ============================================================================

interface StreamState {
  isStreaming: boolean;
  content: string;
  sources: Source[];
  videoInfo: VideoInfo | null;
  sessionId: string | null;
  error: string | null;
}

// ============================================================================
// useQA Hook
// ============================================================================

export function useQA() {
  const [state, setState] = useState<StreamState>({
    isStreaming: false,
    content: '',
    sources: [],
    videoInfo: null,
    sessionId: null,
    error: null,
  });

  const ask = useCallback(async (
    query: string,
    options?: { chapters?: string[]; sessionId?: string }
  ) => {
    setState(prev => ({
      ...prev,
      isStreaming: true,
      content: '',
      sources: [],
      error: null,
    }));

    try {
      const stream = apiClient.qa.ask({
        query,
        chapters: options?.chapters,
        session_id: options?.sessionId,
      });

      for await (const event of stream) {
        handleSSEEvent(event, setState);
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        isStreaming: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      }));
    }
  }, []);

  const followup = useCallback(async (
    sessionId: string,
    query: string,
    chapters?: string[]
  ) => {
    setState(prev => ({
      ...prev,
      isStreaming: true,
      content: '',
      sources: [],
      error: null,
    }));

    try {
      const stream = apiClient.qa.followup({
        session_id: sessionId,
        query,
        chapters,
      });

      for await (const event of stream) {
        handleSSEEvent(event, setState);
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        isStreaming: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      }));
    }
  }, []);

  return {
    ...state,
    ask,
    followup,
  };
}

// ============================================================================
// useVideoSummary Hook
// ============================================================================

export function useVideoSummary() {
  const [state, setState] = useState<StreamState>({
    isStreaming: false,
    content: '',
    sources: [],
    videoInfo: null,
    sessionId: null,
    error: null,
  });

  const summarize = useCallback(async (
    videoId: string,
    options?: { summaryType?: 'detailed' | 'quick'; forceRegenerate?: boolean }
  ) => {
    setState(prev => ({
      ...prev,
      isStreaming: true,
      content: '',
      videoInfo: null,
      error: null,
    }));

    try {
      const stream = apiClient.videoSummary.summarize({
        video_id: videoId,
        summary_type: options?.summaryType,
        force_regenerate: options?.forceRegenerate,
      });

      for await (const event of stream) {
        handleSSEEvent(event, setState);
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        isStreaming: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      }));
    }
  }, []);

  const summarizeChapter = useCallback(async (chapter: string) => {
    setState(prev => ({
      ...prev,
      isStreaming: true,
      content: '',
      error: null,
    }));

    try {
      const stream = apiClient.videoSummary.summarizeChapter({ chapter });

      for await (const event of stream) {
        handleSSEEvent(event, setState);
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        isStreaming: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      }));
    }
  }, []);

  return {
    ...state,
    summarize,
    summarizeChapter,
  };
}

// ============================================================================
// useQuiz Hook
// ============================================================================

export function useQuiz() {
  const [state, setState] = useState<StreamState>({
    isStreaming: false,
    content: '',
    sources: [],
    videoInfo: null,
    sessionId: null,
    error: null,
  });

  const generate = useCallback(async (
    videoIds: string[],
    options?: {
      questionType?: 'mcq' | 'true_false' | 'fill_blank';
      numQuestions?: number;
      difficulty?: 'easy' | 'medium' | 'hard';
    }
  ) => {
    setState(prev => ({
      ...prev,
      isStreaming: true,
      content: '',
      error: null,
    }));

    try {
      const stream = apiClient.quiz.generate({
        video_ids: videoIds,
        question_type: options?.questionType || 'mcq',
        num_questions: options?.numQuestions || 5,
        difficulty: options?.difficulty,
      });

      for await (const event of stream) {
        handleSSEEvent(event, setState);
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        isStreaming: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      }));
    }
  }, []);

  return {
    ...state,
    generate,
  };
}

// ============================================================================
// Helper
// ============================================================================

function handleSSEEvent(
  event: SSEEvent,
  setState: React.Dispatch<React.SetStateAction<StreamState>>
) {
  switch (event.type) {
    case 'token':
      setState(prev => ({
        ...prev,
        content: prev.content + (event.content || ''),
      }));
      break;

    case 'sources':
      setState(prev => ({
        ...prev,
        sources: event.sources || [],
      }));
      break;

    case 'metadata':
      setState(prev => ({
        ...prev,
        videoInfo: event.video_info || null,
      }));
      break;

    case 'done':
      setState(prev => ({
        ...prev,
        isStreaming: false,
        sessionId: event.session_id || null,
        sources: event.sources || prev.sources,
      }));
      break;

    case 'cached':
      setState(prev => ({
        ...prev,
        isStreaming: false,
        content: event.content || '',
        videoInfo: event.video_info || null,
      }));
      break;

    case 'error':
      setState(prev => ({
        ...prev,
        isStreaming: false,
        error: event.content || 'Unknown error',
      }));
      break;
  }
}

