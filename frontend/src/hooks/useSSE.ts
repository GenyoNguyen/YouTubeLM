import { useCallback } from 'react';
import { SourceReference } from '../types';

interface UseSSEOptions {
  onToken: (token: string) => void;
  onProgress?: (progress: number) => void;
  onValidation?: (result: any) => void;
  onDone: (content: string, sources?: SourceReference[], sessionId?: string, quizId?: string) => Promise<void>;
  onError: (error: string) => void;
}

export function useSSE(options: UseSSEOptions) {
  const startStream = useCallback(
    async (url: string, body: any) => {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(body),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let content = '';
        let sources: SourceReference[] = [];
        let sessionId: string | undefined;
        let quizId: string | undefined;
        let progress = 0;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                await options.onDone(content, sources.length > 0 ? sources : undefined, sessionId, quizId);
                return;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.type === 'token') {
                  content += parsed.content || '';
                  options.onToken(parsed.content || '');
                } else if (parsed.type === 'progress') {
                  progress = parsed.progress || 0;
                  options.onProgress?.(progress);
                } else if (parsed.type === 'validation') {
                  options.onValidation?.(parsed.result);
                } else if (parsed.type === 'sources') {
                  sources = parsed.sources || [];
                } else if (parsed.type === 'session_id') {
                  sessionId = parsed.session_id;
                } else if (parsed.type === 'quiz_id') {
                  quizId = parsed.quiz_id;
                }
              } catch (e) {
                // Ignore JSON parse errors
              }
            }
          }
        }

        await options.onDone(content, sources.length > 0 ? sources : undefined, sessionId, quizId);
      } catch (error: any) {
        options.onError(error?.message || String(error));
      }
    },
    [options]
  );

  return { startStream };
}

