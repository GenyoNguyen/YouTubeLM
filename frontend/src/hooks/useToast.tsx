import { useState, useCallback } from 'react';

interface ToastOptions {
  title: string;
  description?: string;
  status?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  isClosable?: boolean;
}

interface Toast extends ToastOptions {
  id: string;
}

let toastIdCounter = 0;

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((options: ToastOptions) => {
    const id = `toast-${toastIdCounter++}`;
    const newToast: Toast = {
      id,
      title: options.title,
      description: options.description,
      status: options.status || 'info',
      duration: options.duration || 3000,
      isClosable: options.isClosable !== false,
    };

    setToasts((prev) => [...prev, newToast]);

    // Auto-remove after duration
    const duration = newToast.duration ?? 3000;
    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }

    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return { toast, toasts, removeToast };
}

// Toast Container Component
export function ToastContainer({ toasts, onRemove }: { toasts: Toast[]; onRemove: (id: string) => void }) {
  if (toasts.length === 0) return null;

  const statusColors: { [key in NonNullable<Toast['status']>]: string } = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500',
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => {
        const status = toast.status || 'info';
        return (
          <div
            key={toast.id}
            className={`${statusColors[status]} text-white px-4 py-3 rounded-lg shadow-lg min-w-[300px] max-w-md flex items-start gap-3`}
          >
            <div className="flex-1">
              <p className="font-semibold">{toast.title}</p>
              {toast.description && (
                <p className="text-sm mt-1 opacity-90">{toast.description}</p>
              )}
            </div>
            {toast.isClosable && (
              <button
                onClick={() => onRemove(toast.id)}
                className="opacity-70 hover:opacity-100 transition-opacity"
                aria-label="Close toast"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}

