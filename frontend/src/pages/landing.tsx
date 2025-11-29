/**
 * Landing Page component with task selection cards
 * Inspired by Podia's landing page design
 */
import { useNavigate } from "react-router-dom";
import { TaskType } from "../types";
import { useChatStore } from "../stores/chatStore";
import qaImage from "../assets/images/tiepLM_qa-circular.png";
import vidSumImage from "../assets/images/tiepLM_vid_sum-circular.png";
import quizImage from "../assets/images/tiepLM_quiz-circular.png";

const TASK_INFO: Record<
  TaskType,
  { title: string; description: string; color: string; image: string }
> = {
  qa: {
    title: "Q&A",
    description:
      "Ask questions about the course content and get accurate answers with citations to relevant video segments.",
    color: "green",
    image: '',
  },
  video_summary: {
    title: "Video Summary",
    description:
      "Get timestamp-based video summaries that help you navigate and understand video content efficiently.",
    color: "orange",
    image: '',
  },
  quiz: {
    title: "Quiz",
    description:
      "Auto-generate quizzes from course material to test your understanding and reinforce learning.",
    color: "purple",
    image: '',
  },
};

// Color mapping for Tailwind classes
const colorClasses = {
  blue: {
    bg: "bg-blue-50",
    border: "border-blue-200",
    title: "text-blue-700",
    icon: "text-blue-600",
    imageBorder: "border-blue-300",
    button: "bg-blue-600 hover:bg-blue-700",
  },
  green: {
    bg: "bg-green-50",
    border: "border-green-200",
    title: "text-green-700",
    icon: "text-green-600",
    imageBorder: "border-green-300",
    button: "bg-green-600 hover:bg-green-700",
  },
  orange: {
    bg: "bg-orange-50",
    border: "border-orange-200",
    title: "text-orange-700",
    icon: "text-orange-600",
    imageBorder: "border-orange-300",
    button: "bg-orange-600 hover:bg-orange-700",
  },
  purple: {
    bg: "bg-purple-50",
    border: "border-purple-200",
    title: "text-purple-700",
    icon: "text-purple-600",
    imageBorder: "border-purple-300",
    button: "bg-purple-600 hover:bg-purple-700",
  },
} as const;

export default function LandingPage() {
  const navigate = useNavigate();
  const { setMode } = useChatStore();

  const handleTaskSelect = (taskType: TaskType) => {
    setMode(taskType);
    // Navigate to chat route
    navigate("/chat");
  };

  return (
    <div className="min-h-screen bg-gray-50 relative overflow-hidden">
      {/* Decorative shapes */}
      <div className="absolute top-[10%] left-[5%] w-[100px] h-[100px] bg-blue-200 rounded-full opacity-30 z-0" />
      <div className="absolute top-[20%] right-[10%] w-[80px] h-[80px] bg-orange-200 rounded-2xl opacity-30 z-0 rotate-45" />
      <div className="absolute bottom-[20%] left-[10%] w-[120px] h-[120px] bg-purple-200 rounded-[30px] opacity-30 z-0 -rotate-30" />
      <div className="absolute bottom-[15%] right-[8%] w-[90px] h-[90px] bg-green-200 rounded-full opacity-30 z-0" />

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="space-y-8">
          {/* Header Section */}
          <div className="text-center space-y-4 py-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
              YouTubeLM: One-for-all AI Assistant
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              An AI assistant which helps you navigate through YouTube videos
              and learn more efficiently.
            </p>
          </div>

          {/* Task Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
            {(
              Object.entries(TASK_INFO) as [
                TaskType,
                (typeof TASK_INFO)[TaskType]
              ][]
            ).map(([taskType, info], index) => {
              // Create slight rotation for visual interest (like Podia)
              const rotation = index % 2 === 0 ? "rotate-2" : "-rotate-2";
              const colors =
                colorClasses[info.color as keyof typeof colorClasses];

              return (
                <div
                  key={taskType}
                  className={`${colors.bg} ${colors.border} rounded-2xl overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-3 hover:shadow-2xl ${rotation} border min-h-[300px] flex flex-col`}
                  onClick={() => handleTaskSelect(taskType)}
                >
                  <div className="p-6 flex flex-col flex-1">
                    {/* Circular Image */}
                    <div className="flex justify-center mb-4">
                      <img
                        src={info.image}
                        alt={info.title}
                        className={`w-[100px] h-[100px] object-cover rounded-full border-4 ${colors.imageBorder} shadow-md`}
                      />
                    </div>

                    <div className="flex justify-between items-start mb-4">
                      <h3 className={`text-xl font-bold ${colors.title}`}>
                        {info.title}
                      </h3>
                      <svg
                        className={`w-6 h-6 ${colors.icon}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 7l5 5m0 0l-5 5m5-5H6"
                        />
                      </svg>
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed flex-1 mb-4">
                      {info.description}
                    </p>
                    <button
                      className={`${colors.button} text-white px-4 py-2 rounded-lg font-semibold mt-auto self-start flex items-center gap-2 transition-colors`}
                    >
                      Get Started
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 7l5 5m0 0l-5 5m5-5H6"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
