import { useRef } from 'react';
import type { TouchEvent } from 'react';

export function useSwipeTabs(onLeft: () => void, onRight: () => void) {
  const startX = useRef<number | null>(null);

  function onTouchStart(e: TouchEvent) {
    startX.current = e.changedTouches[0].clientX;
  }

  function onTouchEnd(e: TouchEvent) {
    if (startX.current === null) return;
    const delta = e.changedTouches[0].clientX - startX.current;
    if (delta < -50) onLeft();
    if (delta > 50) onRight();
    startX.current = null;
  }

  return { onTouchStart, onTouchEnd };
}
