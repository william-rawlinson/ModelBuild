// src/components/ProcessLogDisplay.jsx
import React from "react";

export default function ProcessLogDisplay({
  progressMessages,
  isRunning,
  topMessageRef,
  completionText = "✅ Process completed!",
  completionCondition, // optional boolean to control when to show completion banner
}) {
  if (!progressMessages || progressMessages.length === 0) return null;

  const showCompletion = !isRunning && (completionCondition ?? true);

  return (
    <div className="w-full mt-6 space-y-4">
      {/* Completion Banner */}
      {showCompletion && (
        <div className="rounded-2xl border bg-emerald-50 px-6 py-4 text-center">
          <p className="text-2xl font-semibold text-emerald-700">
            {completionText}
          </p>
        </div>
      )}

      {/* Live Messages Log */}
      <div className="w-full rounded-2xl border bg-slate-50 p-5 max-h-80 overflow-y-auto space-y-2">
        {progressMessages.map((msg, idx) => (
          <div
            key={idx}
            ref={idx === 0 ? topMessageRef : null} // top-most message for auto-scroll
            className="text-slate-900 text-lg md:text-xl font-medium"
          >
            <span className="font-mono text-slate-500 mr-3">{msg.time}</span>
            <span>{msg.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
