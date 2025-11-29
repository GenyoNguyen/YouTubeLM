/**
 * QuizDisplay component - Interactive quiz display with validation
 */
import React from 'react';
import { Quiz, QuizQuestion } from '../../types';
import { useQuizStore } from '../../stores/quizStore';

interface QuizDisplayProps {
  quiz: Quiz | null;
  colorScheme?: string;
  isGenerating: boolean;
  generationProgress: number;
  isValidating: boolean;
  onSubmitAnswers: () => void;
}

export const QuizDisplay: React.FC<QuizDisplayProps> = ({
  quiz,
  colorScheme = 'purple',
  isGenerating,
  generationProgress,
  isValidating,
  onSubmitAnswers,
}) => {
  const { userAnswers, setAnswer, validationResults } = useQuizStore();

  // Convert Map to object for controlled component
  const getAnswer = (questionIndex: number): string => {
    return userAnswers.get(questionIndex) || '';
  };

  // Check if all questions are answered
  const allAnswered =
    quiz?.questions?.every((q) => userAnswers.has(q.question_index)) ?? false;

  // Check if validation is complete
  const validationComplete =
    quiz?.questions?.every((q) => validationResults.has(q.question_index)) ??
    false;

  // Calculate score
  const calculateScore = () => {
    if (!quiz || !quiz.questions || validationResults.size === 0) return null;

    let totalScore = 0;
    let maxScore = quiz.questions.length * 100;

    quiz.questions.forEach((q) => {
      const result = validationResults.get(q.question_index);
      if (!result) return;

      if (q.question_type === 'mcq') {
        totalScore += result.is_correct ? 100 : 0;
      } else {
        totalScore += result.llm_score || 0;
      }
    });

    return Math.round((totalScore / maxScore) * 100);
  };

  // Render MCQ question
  const renderMCQQuestion = (question: QuizQuestion) => {
    const result = validationResults.get(question.question_index);
    const userAnswer = getAnswer(question.question_index);

    return (
      <div className="space-y-3">
        <div className="space-y-2">
          {Object.entries(question.options || {}).map(([key, value]) => {
            const isCorrect = key === question.correct_answer;
            const isUserAnswer = key === userAnswer;

            const borderColor = result
              ? isCorrect
                ? 'border-green-300'
                : isUserAnswer
                ? 'border-red-300'
                : 'border-gray-200 dark:border-gray-600'
              : 'border-gray-200 dark:border-gray-600';

            const bgColor = result
              ? isCorrect
                ? 'bg-green-50 dark:bg-green-900'
                : isUserAnswer
                ? 'bg-red-50 dark:bg-red-900'
                : 'bg-white dark:bg-gray-700'
              : 'bg-white dark:bg-gray-700';

            return (
              <label
                key={key}
                className={`p-3 rounded-md border ${borderColor} ${bgColor} flex items-center gap-3 cursor-pointer ${
                  validationComplete ? 'cursor-not-allowed opacity-60' : ''
                }`}
              >
                <input
                  type="radio"
                  name={`question-${question.question_index}`}
                  value={key}
                  checked={userAnswer === key}
                  onChange={() => setAnswer(question.question_index, key)}
                  disabled={validationComplete}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="flex-1 text-gray-800 dark:text-gray-100">
                  {value}
                </span>
                {result && isCorrect && (
                  <svg
                    className="w-5 h-5 text-green-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
                {result && isUserAnswer && !isCorrect && (
                  <svg
                    className="w-5 h-5 text-red-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </label>
            );
          })}
        </div>

        {/* Show validation result */}
        {result && (
          <div
            className={`rounded-md p-4 ${
              result.is_correct
                ? 'bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700'
                : 'bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700'
            }`}
          >
            <div className="flex items-start gap-2">
              {result.is_correct ? (
                <svg
                  className="w-5 h-5 text-green-500 mt-0.5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5 text-red-500 mt-0.5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
              <div className="flex-1">
                <p className="font-semibold text-sm">
                  {result.is_correct ? 'Correct!' : 'Incorrect'}
                </p>
                {result.explanation && (
                  <p className="text-sm mt-1 text-gray-700 dark:text-gray-300">
                    {result.explanation}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render open-ended question
  const renderOpenEndedQuestion = (question: QuizQuestion) => {
    const result = validationResults.get(question.question_index);
    const userAnswer = getAnswer(question.question_index);

    const getAlertStatus = () => {
      if (result?.llm_score && result.llm_score >= 70) return 'success';
      if (result?.llm_score && result.llm_score >= 50) return 'warning';
      return 'error';
    };

    const status = getAlertStatus();
    const statusColors = {
      success: {
        bg: 'bg-green-50 dark:bg-green-900',
        border: 'border-green-200 dark:border-green-700',
        icon: 'text-green-500',
      },
      warning: {
        bg: 'bg-yellow-50 dark:bg-yellow-900',
        border: 'border-yellow-200 dark:border-yellow-700',
        icon: 'text-yellow-500',
      },
      error: {
        bg: 'bg-red-50 dark:bg-red-900',
        border: 'border-red-200 dark:border-red-700',
        icon: 'text-red-500',
      },
    };

    return (
      <div className="space-y-3">
        <textarea
          placeholder="Enter your answer here..."
          value={userAnswer}
          onChange={(e) => setAnswer(question.question_index, e.target.value)}
          disabled={validationComplete}
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 min-h-[150px] focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
        />

        {/* Show validation result AFTER submission */}
        {result && result.llm_feedback && (
          <div
            className={`rounded-md p-4 border ${statusColors[status].bg} ${statusColors[status].border}`}
          >
            <div className="flex items-start gap-2">
              <svg
                className={`w-5 h-5 ${statusColors[status].icon} mt-0.5`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                {status === 'success' ? (
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                ) : (
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                )}
              </svg>
              <div className="flex-1">
                <p className="font-semibold text-sm">
                  Score: {result.llm_score}/100
                </p>
                <div className="mt-2 space-y-3">
                  {/* 1. Feedback */}
                  <div>
                    <p className="font-bold text-sm mb-1 text-gray-800 dark:text-gray-100">
                      Feedback:
                    </p>
                    <p className="text-sm text-gray-700 dark:text-gray-200">
                      {result.llm_feedback.feedback}
                    </p>
                  </div>

                  {/* 2. Reference Answer */}
                  {question.reference_answer && (
                    <div>
                      <p className="font-bold text-sm mb-1 text-gray-800 dark:text-gray-100">
                        Reference Answer:
                      </p>
                      <p className="text-sm text-gray-700 dark:text-gray-200">
                        {question.reference_answer}
                      </p>
                    </div>
                  )}

                  {/* 3. Points to Cover */}
                  {question.key_points && question.key_points.length > 0 && (
                    <div>
                      <p className="font-bold text-sm mb-1 text-gray-800 dark:text-gray-100">
                        Points to Cover:
                      </p>
                      <ul className="space-y-1 mt-1">
                        {question.key_points.map((point: string, idx: number) => (
                          <li key={idx} className="text-sm text-gray-700 dark:text-gray-200">
                            • {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 4. Covered Points */}
                  <div>
                    <p className="font-bold text-sm text-green-600 dark:text-green-400 mb-1">
                      Covered Points:
                    </p>
                    {result.llm_feedback.covered_points.length > 0 ? (
                      <ul className="space-y-1 mt-1">
                        {result.llm_feedback.covered_points.map((point: string, idx: number) => (
                          <li
                            key={idx}
                            className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200"
                          >
                            <svg
                              className="w-3 h-3 text-green-500"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                            >
                              <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                clipRule="evenodd"
                              />
                            </svg>
                            {point}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-600 dark:text-gray-400">None</p>
                    )}
                  </div>

                  {/* 5. Missing Points */}
                  <div>
                    <p className="font-bold text-sm text-red-600 dark:text-red-400 mb-1">
                      Missing Points:
                    </p>
                    {result.llm_feedback.missing_points.length > 0 ? (
                      <ul className="space-y-1 mt-1">
                        {result.llm_feedback.missing_points.map((point: string, idx: number) => (
                          <li
                            key={idx}
                            className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200"
                          >
                            <svg
                              className="w-3 h-3 text-red-500"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                            >
                              <path
                                fillRule="evenodd"
                                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                                clipRule="evenodd"
                              />
                            </svg>
                            {point}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-600 dark:text-gray-400">None</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render video source
  const renderVideoSource = (question: QuizQuestion) => {
    if (!question.video_id || !question.video_url) return null;

    const timestamp = question.timestamp || 0;
    const videoUrl = `${question.video_url}&t=${timestamp}s`;

    return (
      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
        <span className="font-medium">Source:</span>
        <a
          href={videoUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-500 dark:text-blue-300 hover:underline"
        >
          {question.video_title}
        </a>
        <span>
          ({Math.floor(timestamp / 60)}:
          {String(timestamp % 60).padStart(2, '0')})
        </span>
      </div>
    );
  };

  // Show generation progress
  if (isGenerating) {
    return (
      <div className="flex-1 w-full h-full flex items-center justify-center p-6">
        <div className="space-y-4 text-center">
          <svg
            className="animate-spin h-12 w-12 text-blue-500 mx-auto"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <p className="text-lg font-medium">
            {generationProgress === 0
              ? 'Starting quiz generation...'
              : 'Generating quiz...'}
          </p>
          {generationProgress > 0 && (
            <>
              <div className="w-[300px] bg-gray-200 dark:bg-gray-700 rounded-md h-2">
                <div
                  className={`bg-${colorScheme}-600 h-2 rounded-md transition-all`}
                  style={{ width: `${generationProgress}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {generationProgress}%
              </p>
            </>
          )}
        </div>
      </div>
    );
  }

  // Show message if no quiz or quiz has no questions (partial/corrupted data)
  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <div className="flex-1 w-full h-full flex items-center justify-center p-6">
        <p className="text-lg text-gray-500 dark:text-gray-400">
          Generate a quiz to get started
        </p>
      </div>
    );
  }

  const score = calculateScore();

  const colorSchemes: Record<string, { bg: string; text: string }> = {
    blue: { bg: 'bg-blue-100 dark:bg-blue-900', text: 'text-blue-800 dark:text-blue-200' },
    green: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-800 dark:text-green-200' },
    orange: { bg: 'bg-orange-100 dark:bg-orange-900', text: 'text-orange-800 dark:text-orange-200' },
    purple: { bg: 'bg-purple-100 dark:bg-purple-900', text: 'text-purple-800 dark:text-purple-200' },
  };

  const badgeColors = colorSchemes[colorScheme] || colorSchemes.purple;

  return (
    <div className="flex-1 w-full h-full overflow-y-auto overflow-x-hidden p-6 bg-white dark:bg-gray-800">
      <div className="space-y-6 max-w-4xl mx-auto">
        {/* Quiz Header */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
              {quiz.topic || 'Quiz'}
            </h2>
            <span className={`${badgeColors.bg} ${badgeColors.text} text-sm font-medium px-3 py-1 rounded-full`}>
              {quiz.num_questions} Questions
            </span>
          </div>
          {quiz.chapters && quiz.chapters.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Chapters:
              </span>
              {quiz.chapters.map((chapter) => (
                <span
                  key={chapter}
                  className={`${badgeColors.bg} ${badgeColors.text} text-xs font-medium px-2 py-1 rounded`}
                >
                  {chapter}
                </span>
              ))}
            </div>
          )}
          {/* Video URL Input */}
          {(() => {
            // Collect unique video URLs from questions
            const videoUrls = Array.from(
              new Set(
                quiz.questions
                  .filter((q) => q.video_url)
                  .map((q) => q.video_url!)
              )
            );
            
            if (videoUrls.length === 0) return null;
            
            const videoUrl = videoUrls[0]; // Show first video URL, or join if multiple
            
            return (
              <div className="mt-3">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Video URL:
                </label>
                <input
                  type="text"
                  value={videoUrls.length > 1 ? videoUrls.join(', ') : videoUrl}
                  readOnly
                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={(e) => {
                    // Select all text when clicked for easy copying
                    (e.target as HTMLInputElement).select();
                  }}
                />
              </div>
            );
          })()}
        </div>

        <hr className="border-gray-200 dark:border-gray-700" />

        {/* Score Display (after validation) */}
        {validationComplete && score !== null && (
          <div
            className={`rounded-md p-4 border ${
              score >= 70
                ? 'bg-green-50 dark:bg-green-900 border-green-200 dark:border-green-700'
                : score >= 50
                ? 'bg-yellow-50 dark:bg-yellow-900 border-yellow-200 dark:border-yellow-700'
                : 'bg-red-50 dark:bg-red-900 border-red-200 dark:border-red-700'
            }`}
          >
            <div className="flex items-start gap-2">
              <svg
                className={`w-5 h-5 mt-0.5 ${
                  score >= 70
                    ? 'text-green-500'
                    : score >= 50
                    ? 'text-yellow-500'
                    : 'text-red-500'
                }`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <div>
                <p className="font-semibold text-sm">Quiz Complete!</p>
                <p className="text-sm mt-1 text-gray-700 dark:text-gray-300">
                  Your score: {score}% ({validationResults.size}/{quiz.num_questions}{' '}
                  questions)
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Questions */}
        {quiz.questions.map((question, idx) => {
          const result = validationResults.get(question.question_index);
          const questionScore = result
            ? question.question_type === 'mcq'
              ? result.is_correct
                ? 100
                : 0
              : result.llm_score || 0
            : null;

          const scoreBadgeColor =
            questionScore !== null
              ? questionScore >= 70
                ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                : questionScore >= 50
                ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
              : '';

          return (
            <div
              key={question.id}
              className="p-5 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700"
            >
              <div className="space-y-4">
                {/* Question Header */}
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
                      Question {idx + 1}
                    </h3>
                    {questionScore !== null && (
                      <span
                        className={`text-sm font-medium px-2 py-1 rounded ${scoreBadgeColor}`}
                      >
                        {questionScore}/100
                      </span>
                    )}
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-1 rounded ${
                      question.question_type === 'mcq'
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                        : 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                    }`}
                  >
                    {question.question_type === 'mcq'
                      ? 'Multiple Choice'
                      : 'Open-ended'}
                  </span>
                </div>

                {/* Question Text */}
                <p className="text-base text-gray-700 dark:text-gray-200">
                  {question.question}
                </p>

                {/* Answer Input */}
                {question.question_type === 'mcq'
                  ? renderMCQQuestion(question)
                  : renderOpenEndedQuestion(question)}

                {/* Video Source (show after validation) */}
                {validationComplete && renderVideoSource(question)}
              </div>
            </div>
          );
        })}

        {/* Submit Button */}
        {!validationComplete && (
          <button
            onClick={onSubmitAnswers}
            disabled={!allAnswered || isValidating}
            className={`w-full ${badgeColors.bg} ${badgeColors.text} py-3 px-6 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
          >
            {isValidating ? (
              <>
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Validating...
              </>
            ) : (
              'Submit Answers'
            )}
          </button>
        )}

        {/* Validation Progress */}
        {isValidating && !validationComplete && (
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Validating answers... ({validationResults.size}/{quiz.num_questions})
            </p>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-md h-2">
              <div
                className="bg-blue-600 h-2 rounded-md transition-all"
                style={{
                  width: `${(validationResults.size / quiz.num_questions) * 100}%`,
                }}
              ></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
