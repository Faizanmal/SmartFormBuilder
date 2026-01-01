/**
 * Touch Gesture Hooks for Mobile Experience
 * Provides swipe, pinch, long-press, and other gesture support
 */
'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

// Types
interface Position {
  x: number;
  y: number;
}

interface SwipeState {
  direction: 'left' | 'right' | 'up' | 'down' | null;
  distance: number;
  velocity: number;
}

interface PinchState {
  scale: number;
  center: Position;
  isActive: boolean;
}

interface GestureCallbacks {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onPinch?: (scale: number) => void;
  onLongPress?: () => void;
  onDoubleTap?: () => void;
  onPan?: (delta: Position) => void;
  onTap?: () => void;
}

interface GestureOptions {
  swipeThreshold?: number;
  swipeVelocityThreshold?: number;
  longPressDelay?: number;
  doubleTapDelay?: number;
  pinchEnabled?: boolean;
}

// Main gesture hook
export function useGestures(
  callbacks: GestureCallbacks,
  options: GestureOptions = {}
) {
  const {
    swipeThreshold = 50,
    swipeVelocityThreshold = 0.3,
    longPressDelay = 500,
    doubleTapDelay = 300,
    pinchEnabled = true,
  } = options;

  const [swipeState, setSwipeState] = useState<SwipeState>({
    direction: null,
    distance: 0,
    velocity: 0,
  });
  
  const [pinchState, setPinchState] = useState<PinchState>({
    scale: 1,
    center: { x: 0, y: 0 },
    isActive: false,
  });

  const startPoint = useRef<Position | null>(null);
  const startTime = useRef<number>(0);
  const lastTap = useRef<number>(0);
  const longPressTimer = useRef<NodeJS.Timeout | null>(null);
  const initialDistance = useRef<number>(0);

  // Calculate distance between two points
  const getDistance = useCallback((p1: Position, p2: Position): number => {
    return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
  }, []);

  // Get center point between two touches
  const getCenter = useCallback((touches: React.TouchList): Position => {
    if (touches.length < 2) {
      return { x: touches[0].clientX, y: touches[0].clientY };
    }
    return {
      x: (touches[0].clientX + touches[1].clientX) / 2,
      y: (touches[0].clientY + touches[1].clientY) / 2,
    };
  }, []);

  // Handle touch start
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (e.touches.length === 1) {
      startPoint.current = {
        x: e.touches[0].clientX,
        y: e.touches[0].clientY,
      };
      startTime.current = Date.now();
      
      // Start long press timer
      longPressTimer.current = setTimeout(() => {
        callbacks.onLongPress?.();
        startPoint.current = null;
      }, longPressDelay);
      
    } else if (e.touches.length === 2 && pinchEnabled) {
      // Pinch start
      const touch1 = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      const touch2 = { x: e.touches[1].clientX, y: e.touches[1].clientY };
      initialDistance.current = getDistance(touch1, touch2);
      
      setPinchState({
        scale: 1,
        center: getCenter(e.touches),
        isActive: true,
      });
    }
  }, [callbacks, longPressDelay, pinchEnabled, getDistance, getCenter]);

  // Handle touch move
  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    // Cancel long press on movement
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }

    if (e.touches.length === 1 && startPoint.current) {
      const currentPoint = {
        x: e.touches[0].clientX,
        y: e.touches[0].clientY,
      };
      
      const deltaX = currentPoint.x - startPoint.current.x;
      const deltaY = currentPoint.y - startPoint.current.y;
      
      callbacks.onPan?.({ x: deltaX, y: deltaY });
      
      // Update swipe state
      const distance = Math.max(Math.abs(deltaX), Math.abs(deltaY));
      let direction: SwipeState['direction'] = null;
      
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        direction = deltaX > 0 ? 'right' : 'left';
      } else {
        direction = deltaY > 0 ? 'down' : 'up';
      }
      
      setSwipeState({ direction, distance, velocity: 0 });
      
    } else if (e.touches.length === 2 && pinchEnabled) {
      // Pinch move
      const touch1 = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      const touch2 = { x: e.touches[1].clientX, y: e.touches[1].clientY };
      const currentDistance = getDistance(touch1, touch2);
      const scale = currentDistance / initialDistance.current;
      
      setPinchState(prev => ({
        ...prev,
        scale,
        center: getCenter(e.touches),
      }));
      
      callbacks.onPinch?.(scale);
    }
  }, [callbacks, pinchEnabled, getDistance, getCenter]);

  // Handle touch end
  const handleTouchEnd = useCallback((e: React.TouchEvent) => {
    // Clear long press timer
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }

    if (e.touches.length === 0 && startPoint.current) {
      const endTime = Date.now();
      const duration = endTime - startTime.current;
      
      const endPoint = {
        x: e.changedTouches[0].clientX,
        y: e.changedTouches[0].clientY,
      };
      
      const deltaX = endPoint.x - startPoint.current.x;
      const deltaY = endPoint.y - startPoint.current.y;
      const distance = Math.max(Math.abs(deltaX), Math.abs(deltaY));
      const velocity = distance / duration;
      
      // Check for swipe
      if (distance >= swipeThreshold && velocity >= swipeVelocityThreshold) {
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          if (deltaX > 0) {
            callbacks.onSwipeRight?.();
          } else {
            callbacks.onSwipeLeft?.();
          }
        } else {
          if (deltaY > 0) {
            callbacks.onSwipeDown?.();
          } else {
            callbacks.onSwipeUp?.();
          }
        }
      } else if (distance < 10) {
        // Check for double tap
        const now = Date.now();
        if (now - lastTap.current < doubleTapDelay) {
          callbacks.onDoubleTap?.();
          lastTap.current = 0;
        } else {
          lastTap.current = now;
          // Delay single tap to allow for double tap
          setTimeout(() => {
            if (lastTap.current === now) {
              callbacks.onTap?.();
            }
          }, doubleTapDelay);
        }
      }
      
      setSwipeState({
        direction: null,
        distance: 0,
        velocity: 0,
      });
      startPoint.current = null;
    }

    // Reset pinch state
    if (e.touches.length < 2) {
      setPinchState({
        scale: 1,
        center: { x: 0, y: 0 },
        isActive: false,
      });
    }
  }, [callbacks, swipeThreshold, swipeVelocityThreshold, doubleTapDelay]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (longPressTimer.current) {
        clearTimeout(longPressTimer.current);
      }
    };
  }, []);

  return {
    swipeState,
    pinchState,
    handlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
    },
  };
}

// Swipe-only hook (simpler)
export function useSwipe(
  onSwipe: (direction: 'left' | 'right' | 'up' | 'down') => void,
  threshold = 50
) {
  const { swipeState, handlers } = useGestures({
    onSwipeLeft: () => onSwipe('left'),
    onSwipeRight: () => onSwipe('right'),
    onSwipeUp: () => onSwipe('up'),
    onSwipeDown: () => onSwipe('down'),
  }, { swipeThreshold: threshold });

  return { swipeState, handlers };
}

// Long press hook
export function useLongPress(
  onLongPress: () => void,
  delay = 500
) {
  const { handlers } = useGestures(
    { onLongPress },
    { longPressDelay: delay }
  );

  return handlers;
}

// Pan gesture hook
export function usePan(
  onPan: (delta: Position) => void
) {
  const { handlers } = useGestures({ onPan });
  return handlers;
}

// Pinch-to-zoom hook
export function usePinchZoom(
  onZoom: (scale: number) => void,
  minScale = 0.5,
  maxScale = 3
) {
  const [currentScale, setCurrentScale] = useState(1);
  const baseScale = useRef(1);

  const handlePinch = useCallback((scale: number) => {
    const newScale = Math.max(minScale, Math.min(maxScale, baseScale.current * scale));
    setCurrentScale(newScale);
    onZoom(newScale);
  }, [minScale, maxScale, onZoom]);

  const { pinchState, handlers } = useGestures(
    { onPinch: handlePinch },
    { pinchEnabled: true }
  );

  // Update base scale when pinch ends
  useEffect(() => {
    if (!pinchState.isActive) {
      baseScale.current = currentScale;
    }
  }, [pinchState.isActive, currentScale]);

  return {
    scale: currentScale,
    handlers,
    reset: () => {
      setCurrentScale(1);
      baseScale.current = 1;
    },
  };
}

// Pull-to-refresh hook
export function usePullToRefresh(
  onRefresh: () => Promise<void>,
  threshold = 80
) {
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const startY = useRef(0);
  const canPull = useRef(true);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    // Only allow pull if at top of scrollable area
    const target = e.target as HTMLElement;
    canPull.current = target.scrollTop === 0;
    startY.current = e.touches[0].clientY;
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!canPull.current || isRefreshing) return;

    const currentY = e.touches[0].clientY;
    const distance = currentY - startY.current;

    if (distance > 0) {
      // Apply resistance
      const dampedDistance = Math.pow(distance, 0.7);
      setPullDistance(Math.min(dampedDistance, threshold * 1.5));
    }
  }, [isRefreshing, threshold]);

  const handleTouchEnd = useCallback(async () => {
    if (pullDistance >= threshold && !isRefreshing) {
      setIsRefreshing(true);
      try {
        await onRefresh();
      } finally {
        setIsRefreshing(false);
        setPullDistance(0);
      }
    } else {
      setPullDistance(0);
    }
  }, [pullDistance, threshold, isRefreshing, onRefresh]);

  return {
    pullDistance,
    isRefreshing,
    progress: Math.min(pullDistance / threshold, 1),
    handlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
    },
  };
}

// Swipeable card/item hook (for list items)
export function useSwipeableItem(
  onSwipeLeft?: () => void,
  onSwipeRight?: () => void,
  threshold = 100
) {
  const [offsetX, setOffsetX] = useState(0);
  const [isReleased, setIsReleased] = useState(false);
  const startX = useRef(0);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    setIsReleased(false);
    startX.current = e.touches[0].clientX - offsetX;
  }, [offsetX]);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    const currentX = e.touches[0].clientX;
    const newOffset = currentX - startX.current;
    
    // Apply bounds
    const bounded = Math.max(-threshold * 1.5, Math.min(threshold * 1.5, newOffset));
    setOffsetX(bounded);
  }, [threshold]);

  const handleTouchEnd = useCallback(() => {
    setIsReleased(true);
    
    if (Math.abs(offsetX) >= threshold) {
      if (offsetX > 0 && onSwipeRight) {
        onSwipeRight();
      } else if (offsetX < 0 && onSwipeLeft) {
        onSwipeLeft();
      }
    }
    
    setOffsetX(0);
  }, [offsetX, threshold, onSwipeLeft, onSwipeRight]);

  return {
    offsetX,
    isReleased,
    progress: Math.abs(offsetX) / threshold,
    handlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
    },
    style: {
      transform: `translateX(${offsetX}px)`,
      transition: isReleased ? 'transform 0.3s ease-out' : 'none',
    },
  };
}

export default useGestures;
