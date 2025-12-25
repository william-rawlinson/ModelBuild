// src/context/Context.jsx
import React, { createContext, useRef, useEffect, useState } from "react";

export const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000/ws");

    ws.current.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      console.log("Raw WebSocket message received:", event.data);

      let msg;
      try {
        msg = JSON.parse(event.data);
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
        return;
      }

      console.log("Parsed WebSocket message:", msg);
      setMessages((prev) => [...prev, msg]);

      // optional: log process completion
      if (msg.process_complete) {
        console.log(`Process "${msg.process_name}" completed`);
      }
    };

    ws.current.onclose = (event) => {
      console.log("WebSocket closed:", event);
      setIsConnected(false);
    };

    ws.current.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    return () => {
      console.log("Cleaning up WebSocket connection...");
      ws.current?.close();
    };
  }, []);

  const sendMessage = (message) => {
    if (ws.current && isConnected) {
      console.log("WebSocket sending message:", message);
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn("WebSocket not connected yet, cannot send:", message);
    }
  };

  return (
    <WebSocketContext.Provider
      value={{
        ws: ws.current,
        sendMessage,
        messages,
        isConnected,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};
