import { motion, AnimatePresence } from 'framer-motion'
import { getMoodTheme } from '../theme'

export default function EmotionCard({ mood }) {
  const theme = getMoodTheme(mood)

  return (
    <div
      className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4 flex-1"
      style={{ minHeight: '90px' }}
    >
      <span className="text-xs font-semibold uppercase tracking-widest text-white/40">Mood</span>
      <AnimatePresence mode="wait">
        <motion.div
          key={mood}
          className="mt-3"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.3 }}
        >
          <span
            className="text-xl font-bold tracking-widest"
            style={{ color: theme.accent, textShadow: `0 0 16px ${theme.glow}` }}
          >
            {theme.label}
          </span>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
