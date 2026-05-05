"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

interface SlideContextValue {
  current: number;
  total: number;
  next: () => void;
  prev: () => void;
  goTo: (n: number) => void;
}

const SlideContext = createContext<SlideContextValue>({
  current: 0,
  total: 0,
  next: () => {},
  prev: () => {},
  goTo: () => {},
});

export function useSlide() {
  return useContext(SlideContext);
}

export function SlideProvider({
  children,
  total,
}: {
  children: React.ReactNode;
  total: number;
}) {
  const [current, setCurrent] = useState(0);

  const next = useCallback(
    () => setCurrent((c) => Math.min(c + 1, total - 1)),
    [total]
  );
  const prev = useCallback(() => setCurrent((c) => Math.max(c - 1, 0)), []);
  const goTo = useCallback(
    (n: number) => setCurrent(Math.max(0, Math.min(n, total - 1))),
    [total]
  );

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "ArrowRight" || e.key === "ArrowDown" || e.key === " ") {
        e.preventDefault();
        next();
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        prev();
      } else if (e.key === "Home") {
        e.preventDefault();
        goTo(0);
      } else if (e.key === "End") {
        e.preventDefault();
        goTo(total - 1);
      }
    }

    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [next, prev, goTo, total]);

  return (
    <SlideContext.Provider value={{ current, total, next, prev, goTo }}>
      {children}
    </SlideContext.Provider>
  );
}
