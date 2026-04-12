import { motion, AnimatePresence } from 'framer-motion'
import { getMoodTheme } from '../theme'

export default function EmotionCard({ mood }) {
  const theme = getMoodTheme(mood)

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4 flex flex-col justify-center items-center gap-2">
      <span className="text-xs font-semibold uppercase tracking-widest text-white/40">Mood</span>
      <AnimatePresence mode="wait">
        <motion.span
          key={mood}
          className="text-2xl font-black tracking-widest text-center"
          style={{ color: theme.accent, textShadow: `0 0 20px ${theme.glow}` }}
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.85 }}
          transition={{ duration: 0.3 }}
        >
          {theme.label}
        </motion.span>
      </AnimatePresence>
      {/* Mood glow dot */}
      <motion.div
        className="rounded-full"
        style={{ width: 8, height: 8, background: theme.accent, boxShadow: `0 0 12px ${theme.accent}` }}
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  )
}
