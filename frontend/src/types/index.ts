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
  sources?: Source[];
  timestamp: Date;
}

export interface Source {
  video_url: string;
  timestamp: string;
  chapter: string;
}

export type TaskType = 'text_summary' | 'qa' | 'video_summary' | 'quiz';

