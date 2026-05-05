"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useSlide } from "./SlideProvider";

export function Slide({
  index,
  children,
  compact = false,
}: {
  index: number;
  children: React.ReactNode;
  compact?: boolean;
}) {
  const { current } = useSlide();
  const isActive = current === index;

  return (
    <AnimatePresence>
      {isActive && (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="absolute inset-0 flex items-center justify-center overflow-y-auto"
        >
          <div
            className={`w-full max-w-[1200px] mx-auto px-12 ${compact ? "py-6" : "py-16"}`}
          >
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
