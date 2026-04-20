import { motion } from "framer-motion";

type Props = { position: number; eta: number; status: string };

export function AnimatedQueueTracker({ position, eta, status }: Props) {
  return (
    <motion.div layout className="card space-y-3">
      <div className="flex justify-between">
        <span>Status</span>
        <span className="font-semibold capitalize">{status}</span>
      </div>
      <div className="w-full bg-slate-200 rounded h-2">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(8, 100 - position * 10)}%` }}
          className="h-2 bg-brand-600 rounded"
        />
      </div>
      <p>Position: {position}</p>
      <p>Estimated wait: {eta} minutes</p>
    </motion.div>
  );
}
