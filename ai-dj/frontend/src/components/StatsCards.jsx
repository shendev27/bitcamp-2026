import { motion } from 'framer-motion'
import { getMoodTheme } from '../theme'

function Card({ label, value, accent }) {
  return (
    <motion.div
      className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4 flex flex-col gap-1"
      style={{ boxShadow: `0 0 20px ${accent}22` }}
      layout
    >
      <span className="text-xs font-semibold uppercase tracking-widest text-white/40">{label}</span>
      <span className="text-2xl font-bold truncate" style={{ color: accent }}>{value}</span>
    </motion.div>
  )
}

/**
 * 2×2 grid of stat cards: People, Emotion, Hype, Mood.
 */
export default function StatsCards({ state }) {
  const mood = state?.mood ?? 'dead'
  const theme = getMoodTheme(mood)

  return (
    <div className="grid grid-cols-2 gap-3">
      <Card label="People" value={state?.people_count ?? 0} accent={theme.accent} />
      <Card
        label="Emotion"
        value={(state?.dominant_emotion ?? 'neutral').toUpperCase()}
        accent={theme.accent}
      />
      <Card label="Hype" value={`${Math.round(state?.hype ?? 0)}`} accent={theme.accent} />
      <Card
        label="Mood"
        value={theme.label}
        accent={theme.glow}
      />
    </div>
  )
}
