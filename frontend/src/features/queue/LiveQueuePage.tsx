import { useEffect } from "react";
import { useQueueStore } from "../../store/useQueueStore";
import { AnimatedQueueTracker } from "./AnimatedQueueTracker";

export function LiveQueuePage() {
  const { position, eta, status, setQueue } = useQueueStore();

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/queues/1/");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.payload?.queue_entry) {
        setQueue({
          status: data.type,
          position: data.payload.queue_entry.position,
          eta: data.payload.queue_entry.estimated_wait_minutes
        });
      }
    };
    return () => ws.close();
  }, [setQueue]);

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Live Queue Tracker</h2>
      <AnimatedQueueTracker position={position} eta={eta} status={status} />
    </div>
  );
}
