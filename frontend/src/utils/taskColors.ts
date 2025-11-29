import { TaskType } from '../types';

export function getTaskColor(taskType: TaskType): string {
  const colorMap: Record<TaskType, string> = {
    qa: 'green',
    video_summary: 'orange',
    quiz: 'purple',
  };
  return colorMap[taskType] || 'green';
}

