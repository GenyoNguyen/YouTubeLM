/**
 * ResizablePanels - A component that provides resizable split panels
 * Supports both horizontal (side-by-side) and vertical (stacked) layouts
 */
import React, { useState, useRef, useCallback, useEffect } from 'react';

interface ResizablePanelsProps {
  direction?: 'horizontal' | 'vertical';
  defaultSizes?: [number, number]; // Percentage sizes [first, second]
  minSizes?: [number, number]; // Minimum percentage sizes
  children: [React.ReactNode, React.ReactNode];
  className?: string;
}

export const ResizablePanels: React.FC<ResizablePanelsProps> = ({
  direction = 'horizontal',
  defaultSizes = [50, 50],
  minSizes = [20, 20],
  children,
  className,
}) => {
  const [sizes, setSizes] = useState<[number, number]>(defaultSizes);
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startPosRef = useRef<number>(0);
  const startSizesRef = useRef<[number, number]>([0, 0]);
  const isResizingRef = useRef(false);

  // Store current sizes in ref to avoid stale closures
  const sizesRef = useRef<[number, number]>(sizes);
  useEffect(() => {
    sizesRef.current = sizes;
  }, [sizes]);

  // Setup mouse event handlers with useEffect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizingRef.current || !containerRef.current) return;

      e.preventDefault();
      e.stopPropagation();

      const container = containerRef.current;
      const containerSize =
        direction === 'horizontal' ? container.offsetWidth : container.offsetHeight;

      const currentPos = direction === 'horizontal' ? e.clientX : e.clientY;
      const delta = currentPos - startPosRef.current;
      const deltaPercent = (delta / containerSize) * 100;

      const [firstSize, secondSize] = startSizesRef.current;
      let newFirstSize = firstSize + deltaPercent;
      let newSecondSize = secondSize - deltaPercent;

      // Apply minimum size constraints
      const [minFirst, minSecond] = minSizes;
      if (newFirstSize < minFirst) {
        newFirstSize = minFirst;
        newSecondSize = 100 - minFirst;
      } else if (newSecondSize < minSecond) {
        newSecondSize = minSecond;
        newFirstSize = 100 - minSecond;
      }

      setSizes([newFirstSize, newSecondSize]);
    };

    const handleMouseUp = () => {
      if (!isResizingRef.current) return;

      isResizingRef.current = false;
      setIsResizing(false);

      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing, direction, minSizes]);

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();

      if (isResizingRef.current) return;

      isResizingRef.current = true;
      setIsResizing(true);
      startPosRef.current = direction === 'horizontal' ? e.clientX : e.clientY;
      startSizesRef.current = sizesRef.current;
    },
    [direction]
  );

  const dividerHitArea = 8;
  const isHorizontal = direction === 'horizontal';

  return (
    <div
      ref={containerRef}
      className={`flex h-full w-full ${className || ''} ${
        isHorizontal ? 'flex-row' : 'flex-col'
      }`}
    >
      {/* First Panel */}
      <div
        className="overflow-hidden relative"
        style={{
          flex: `0 0 ${sizes[0]}%`,
          [isHorizontal ? 'minWidth' : 'minHeight']: `${minSizes[0]}%`,
          pointerEvents: isResizing ? 'none' : 'auto',
        }}
      >
        {children[0]}
      </div>

      {/* Resizable Divider */}
      <div
        onMouseDown={handleMouseDown}
        role="separator"
        aria-label="Resize panels"
        aria-orientation={direction}
        className={`flex items-center justify-center flex-shrink-0 relative z-10 transition-colors ${
          isHorizontal
            ? `w-4 cursor-col-resize ${isResizing ? 'bg-blue-400' : 'bg-transparent hover:bg-blue-200'}`
            : `h-4 cursor-row-resize ${isResizing ? 'bg-blue-400' : 'bg-transparent hover:bg-blue-200'}`
        }`}
      >
        <div
          className={`${
            isHorizontal ? 'w-0.5 h-[60%]' : 'h-0.5 w-[60%]'
          } rounded-sm ${isResizing ? 'bg-blue-500' : 'bg-gray-400'} transition-colors`}
        />
      </div>

      {/* Second Panel */}
      <div
        className="overflow-hidden relative"
        style={{
          flex: `0 0 ${sizes[1]}%`,
          [isHorizontal ? 'minWidth' : 'minHeight']: `${minSizes[1]}%`,
          pointerEvents: isResizing ? 'none' : 'auto',
        }}
      >
        {children[1]}
      </div>
    </div>
  );
};
