// Quiz store for managing quiz state
import { Quiz, QuizValidationResult } from '../types';

interface QuizStore {
  currentQuiz: Quiz | null;
  setCurrentQuiz: (quiz: Quiz | null) => void;
  persistedQuizId: string | null;
  setPersistedQuizId: (id: string | null) => void;
  isGenerating: boolean;
  setIsGenerating: (value: boolean) => void;
  generationProgress: number;
  setGenerationProgress: (value: number) => void;
  isValidating: boolean;
  setIsValidating: (value: boolean) => void;
  addValidationResult: (questionIndex: number, result: QuizValidationResult) => void;
  clearValidationResults: () => void;
  resetQuiz: () => void;
  selectedChapters: string[];
  setSelectedChapters: (chapters: string[]) => void;
  userAnswers: Map<number, string>;
  setAnswer: (questionIndex: number, answer: string) => void;
  clearAnswers: () => void;
  validationResults: Map<number, QuizValidationResult>;
}

// Simple implementation - can be replaced with Zustand later
let quizState: {
  currentQuiz: Quiz | null;
  persistedQuizId: string | null;
  isGenerating: boolean;
  generationProgress: number;
  isValidating: boolean;
  selectedChapters: string[];
  userAnswers: Map<number, string>;
  validationResults: Map<number, QuizValidationResult>;
} = {
  currentQuiz: null,
  persistedQuizId: null,
  isGenerating: false,
  generationProgress: 0,
  isValidating: false,
  selectedChapters: [],
  userAnswers: new Map(),
  validationResults: new Map(),
};

export function useQuizStore(): QuizStore {
  return {
    currentQuiz: quizState.currentQuiz,
    setCurrentQuiz: (quiz: Quiz | null) => {
      quizState.currentQuiz = quiz;
    },
    persistedQuizId: quizState.persistedQuizId,
    setPersistedQuizId: (id: string | null) => {
      quizState.persistedQuizId = id;
    },
    isGenerating: quizState.isGenerating,
    setIsGenerating: (value: boolean) => {
      quizState.isGenerating = value;
    },
    generationProgress: quizState.generationProgress,
    setGenerationProgress: (value: number) => {
      quizState.generationProgress = value;
    },
    isValidating: quizState.isValidating,
    setIsValidating: (value: boolean) => {
      quizState.isValidating = value;
    },
    addValidationResult: (questionIndex: number, result: QuizValidationResult) => {
      quizState.validationResults.set(questionIndex, result);
    },
    clearValidationResults: () => {
      quizState.validationResults.clear();
    },
    resetQuiz: () => {
      quizState.currentQuiz = null;
      quizState.persistedQuizId = null;
      quizState.isGenerating = false;
      quizState.generationProgress = 0;
      quizState.isValidating = false;
      quizState.userAnswers.clear();
      quizState.validationResults.clear();
    },
    selectedChapters: quizState.selectedChapters,
    setSelectedChapters: (chapters: string[]) => {
      quizState.selectedChapters = chapters;
    },
    userAnswers: quizState.userAnswers,
    setAnswer: (questionIndex: number, answer: string) => {
      quizState.userAnswers.set(questionIndex, answer);
    },
    clearAnswers: () => {
      quizState.userAnswers.clear();
    },
    validationResults: quizState.validationResults,
  };
}

