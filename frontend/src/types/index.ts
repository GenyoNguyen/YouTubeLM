// TypeScript type definitions

export interface Video {
  id: string;
  title: string;
  url: string;
  chapter: string;
  duration: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceReference[];
  timestamp: Date;
}

export interface Source {
  video_url: string;
  timestamp: string;
  chapter: string;
}

export interface SourceReference {
  index: number;
  video_url: string;
  video_title: string;
  start_time: number;
  end_time: number;
  chapter: string;
  text?: string;
}

export interface ChatSession {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface QuizQuestion {
  id: string;
  question_index: number;
  question: string;
  question_type: 'mcq' | 'open_ended';
  options?: Record<string, string>;
  correct_answer?: string;
  reference_answer?: string;
  key_points?: string[];
  video_id?: string;
  video_url?: string;
  video_title?: string;
  timestamp?: number;
}

export interface Quiz {
  id: string;
  user_id: string;
  topic?: string;
  chapters?: string[];
  question_type: 'mcq' | 'open_ended' | 'mixed';
  num_questions: number;
  created_at: string;
  questions: QuizQuestion[];
}

export interface QuizHistory {
  id: string;
  topic?: string;
  num_questions: number;
  question_type: string;
  created_at: string;
}

export interface QuizValidationResult {
  is_correct: boolean;
  llm_score?: number;
  explanation?: string;
  llm_feedback?: {
    feedback: string;
    covered_points: string[];
    missing_points: string[];
  };
}

export type TaskType = 'qa' | 'video_summary' | 'quiz';

