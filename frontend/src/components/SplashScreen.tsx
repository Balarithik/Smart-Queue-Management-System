import { motion } from 'framer-motion'

export function SplashScreen() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-indigo-600 px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.92 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.45, ease: 'easeOut' }}
        className="text-center"
      >
        <p className="text-4xl font-bold tracking-tight text-white">SQMS</p>
        <p className="mt-2 text-sm font-medium text-indigo-100">Smart Queue Management</p>
      </motion.div>
      <motion.div
        className="mt-10 h-8 w-8 rounded-full border-2 border-white/30 border-t-white"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.9, ease: 'linear' }}
        aria-hidden
      />
    </div>
  )
}
