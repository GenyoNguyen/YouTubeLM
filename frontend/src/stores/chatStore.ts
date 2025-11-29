// Zustand store for chat state management
import { TaskType, ChatMessage, ChatSession, SourceReference } from '../types';

interface ChatState {
  currentMode: TaskType;
  setMode: (mode: TaskType) => void;
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  currentSession: ChatSession | null;
  setCurrentSession: (session: ChatSession | null) => void;
  isStreaming: boolean;
  setIsStreaming: (isStreaming: boolean) => void;
  streamingContent: string;
  appendStreamingContent: (content: string) => void;
  resetStreamingContent: () => void;
  selectedChapters: string[];
  setSelectedChapters: (chapters: string[]) => void;
  selectedVideo: string | null;
  setSelectedVideo: (videoId: string | null) => void;
}

// Simple implementation - can be replaced with Zustand later
let chatState: {
  currentMode: TaskType;
  messages: ChatMessage[];
  currentSession: ChatSession | null;
  isStreaming: boolean;
  streamingContent: string;
  selectedChapters: string[];
  selectedVideo: string | null;
} = {
  currentMode: 'qa',
  messages: [],
  currentSession: null,
  isStreaming: false,
  streamingContent: '',
  selectedChapters: [],
  selectedVideo: null,
};

export function useChatStore(): ChatState {
  return {
    currentMode: chatState.currentMode,
    setMode: (mode: TaskType) => {
      chatState.currentMode = mode;
    },
    messages: chatState.messages,
    addMessage: (message: ChatMessage) => {
      chatState.messages = [...chatState.messages, message];
    },
    setMessages: (messages: ChatMessage[]) => {
      chatState.messages = messages;
    },
    currentSession: chatState.currentSession,
    setCurrentSession: (session: ChatSession | null) => {
      chatState.currentSession = session;
    },
    isStreaming: chatState.isStreaming,
    setIsStreaming: (isStreaming: boolean) => {
      chatState.isStreaming = isStreaming;
    },
    streamingContent: chatState.streamingContent,
    appendStreamingContent: (content: string) => {
      chatState.streamingContent = chatState.streamingContent + content;
    },
    resetStreamingContent: () => {
      chatState.streamingContent = '';
    },
    selectedChapters: chatState.selectedChapters,
    setSelectedChapters: (chapters: string[]) => {
      chatState.selectedChapters = chapters;
    },
    selectedVideo: chatState.selectedVideo,
    setSelectedVideo: (videoId: string | null) => {
      chatState.selectedVideo = videoId;
    },
  };
}
