import { useState } from "react";
import { motion } from "framer-motion";
import QRCode from "qrcode.react";
import { api } from "../../app/api";
import { useQueueStore } from "../../store/useQueueStore";

export function JoinQueuePage() {
  const [service, setService] = useState("1");
  const [loading, setLoading] = useState(false);
  const setQueue = useQueueStore((s) => s.setQueue);

  const join = async () => {
    setLoading(true);
    const { data } = await api.post("/queues/entries/join/", { service });
    setQueue({ position: data.position, eta: data.estimated_wait_minutes, status: data.status });
    setLoading(false);
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-xl font-semibold">Join Queue</h2>
      <div className="card">
        <input className="border rounded p-2 w-full" value={service} onChange={(e) => setService(e.target.value)} />
        <button onClick={join} className="mt-3 rounded bg-brand-600 text-white px-4 py-2">
          {loading ? "Joining..." : "Join Queue"}
        </button>
      </div>
      <motion.div whileHover={{ scale: 1.01 }} className="card inline-block">
        <QRCode value={`smartqueue://join/service/${service}`} />
      </motion.div>
    </div>
  );
}
