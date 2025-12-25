// src/hooks/useProcessLog.js
import { useState, useEffect } from "react";
import { useContext } from "react";
import { WebSocketContext } from "../context/Context";

/**
 * Custom hook to track progress messages and running state for a process.
 *
 * @param {Object} options
 * @param {string} options.processName - The process name to filter messages.
 */
export default function useProcessLog({ processName }) {
  const { messages } = useContext(WebSocketContext);

  const [progressMessages, setProgressMessages] = useState([]);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!messages || messages.length === 0) return;

    messages.forEach((msg) => {
      if (msg.process_name !== processName) return;

      // Clear logs on process_start
      if (msg.type === "process_start") {
        setProgressMessages([]);
        setIsRunning(true);
        return;
      }

      // Append progress messages
      if (msg.payload?.message) {
        const newMessage = {
          text: msg.payload.message,
          time: new Date().toLocaleTimeString(),
        };
        setProgressMessages((prev) => [newMessage, ...prev]);
      }

      // Stop running when process completes
      if (msg.process_complete) {
        setIsRunning(false);
      }
    });
  }, [messages, processName]);

  // Optional helper to clear manually
  const clear = () => {
    setProgressMessages([]);
    setIsRunning(false);
  };

  return {
    progressMessages,
    isRunning,
    clear,
  };
}
