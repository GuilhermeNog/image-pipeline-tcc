import type { JobProgress } from "@/types/job";
import { useCallback, useEffect, useRef } from "react";

interface UseWebSocketOptions {
  jobId: string | null;
  onProgress: (data: JobProgress) => void;
  onComplete: (data: JobProgress) => void;
  onError: (data: JobProgress) => void;
}

export function useWebSocket({ jobId, onProgress, onComplete, onError }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!jobId) return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/jobs/${jobId}`);
    ws.onmessage = (event) => {
      const data: JobProgress = JSON.parse(event.data);
      if (data.status === "completed") {
        onComplete(data);
        ws.close();
      } else if (data.status === "failed") {
        onError(data);
        ws.close();
      } else {
        onProgress(data);
      }
    };
    ws.onerror = () => {
      onError({ job_id: jobId, status: "failed", error: "WebSocket connection failed" });
    };
    wsRef.current = ws;
  }, [jobId, onProgress, onComplete, onError]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return { disconnect };
}
