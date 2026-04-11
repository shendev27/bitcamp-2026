import { motion } from 'framer-motion'
import { getMoodTheme } from '../theme'
import blueAstronaut from '../blue.svg'

export default function PeopleCard({ count, mood }) {
  const theme = getMoodTheme(mood)

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4">
      <span className="text-xs font-semibold uppercase tracking-widest text-white/40">People</span>
      <div className="flex items-center justify-between mt-2">
        <motion.span
          key={count}
          className="text-6xl font-black"
          style={{ color: theme.accent, textShadow: `0 0 24px ${theme.glow}` }}
          initial={{ scale: 1.3, opacity: 0.6 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {count}
        </motion.span>
        <img src={blueAstronaut} alt="" className="w-16 h-16 object-contain" />
      </div>
    </div>
  )
}
