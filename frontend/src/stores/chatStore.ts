// Zustand store for chat state management
import { TaskType } from '../types';

interface ChatStore {
  mode: TaskType | null;
  setMode: (mode: TaskType) => void;
}

// Simple implementation - can be replaced with Zustand later
let currentMode: TaskType | null = null;

export function useChatStore(): ChatStore {
  return {
    mode: currentMode,
    setMode: (mode: TaskType) => {
      currentMode = mode;
    },
  };
}

