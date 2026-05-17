import { motion } from 'framer-motion'

type LoadingScreenProps = {
  message?: string
}

export function LoadingScreen({ message = 'Loading…' }: LoadingScreenProps) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-4 text-slate-600">
      <motion.div
        className="h-9 w-9 rounded-full border-2 border-slate-200 border-t-indigo-600"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.85, ease: 'linear' }}
        aria-hidden
      />
      <p className="text-sm">{message}</p>
    </div>
  )
}

export function PageLoader({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-500">
      <motion.span
        className="inline-block h-4 w-4 rounded-full border-2 border-slate-200 border-t-indigo-600"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.85, ease: 'linear' }}
        aria-hidden
      />
      <span>{label}</span>
    </div>
  )
}
