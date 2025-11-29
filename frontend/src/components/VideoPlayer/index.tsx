/**
 * VideoPlayer - Video player component with timestamp navigation
 * Displays a video with clickable timestamps from citations
 */
import React, { useRef, forwardRef, useImperativeHandle, useState } from 'react';

export interface VideoPlayerHandle {
  seekToTime: (seconds: number) => void;
}

interface VideoPlayerProps {
  videoUrl: string;
  videoTitle: string;
  onTimeUpdate?: (currentTime: number) => void;
}

export const VideoPlayer = forwardRef<VideoPlayerHandle, VideoPlayerProps>(
  function VideoPlayer(
    { videoUrl, videoTitle, onTimeUpdate },
    ref
  ) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [isPaused, setIsPaused] = useState(true);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);

    const handlePlayPause = () => {
      if (videoRef.current) {
        if (videoRef.current.paused) {
          videoRef.current.play();
          setIsPaused(false);
        } else {
          videoRef.current.pause();
          setIsPaused(true);
        }
      }
    };

    const seekToTime = (seconds: number) => {
      if (videoRef.current) {
        videoRef.current.currentTime = seconds;
        setCurrentTime(seconds);
        videoRef.current.play();
        setIsPaused(false);
      }
    };

    // Expose seek function to parent component via ref
    useImperativeHandle(ref, () => ({
      seekToTime,
    }));

    const handleTimeUpdate = () => {
      if (videoRef.current) {
        const time = videoRef.current.currentTime;
        setCurrentTime(time);
        if (onTimeUpdate) {
          onTimeUpdate(time);
        }
      }
    };

    const handleLoadedMetadata = () => {
      if (videoRef.current) {
        setDuration(videoRef.current.duration);
      }
    };

    const handlePlay = () => {
      setIsPaused(false);
    };

    const handlePause = () => {
      setIsPaused(true);
    };

    const formatTime = (seconds: number) => {
      if (!isFinite(seconds) || isNaN(seconds)) return '00:00';
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newTime = parseFloat(e.target.value);
      if (videoRef.current) {
        videoRef.current.currentTime = newTime;
        setCurrentTime(newTime);
      }
    };

    return (
      <div className="w-full flex flex-col gap-4">
        <div className="bg-black rounded-md overflow-hidden w-full aspect-video">
          <video
            ref={videoRef}
            width="100%"
            height="100%"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onPlay={handlePlay}
            onPause={handlePause}
            className="block w-full h-full"
            crossOrigin="anonymous"
          >
            <source src={videoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>

        <div className="flex flex-col gap-2 w-full">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">
            {videoTitle}
          </h2>

          <div className="w-full flex justify-between items-center px-2">
            <button
              aria-label="Play/Pause"
              onClick={handlePlayPause}
              className="p-2 rounded bg-blue-600 hover:bg-blue-700 text-white transition-colors flex items-center justify-center"
            >
              {isPaused ? (
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  style={{ transform: 'rotate(90deg)' }}
                >
                  <path
                    fillRule="evenodd"
                    d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>

            <span className="text-sm text-gray-600 dark:text-gray-400">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          {duration > 0 && (
            <div className="w-full px-2">
              <input
                type="range"
                min="0"
                max={duration}
                value={currentTime}
                onChange={handleSeek}
                className="w-full cursor-pointer"
              />
            </div>
          )}
        </div>
      </div>
    );
  }
);

VideoPlayer.displayName = 'VideoPlayer';
