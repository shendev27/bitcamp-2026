import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { getMoodTheme } from '../theme'

const BAR_COUNT = 18

export default function AudioSpectrum({ mood, hype }) {
  const theme = getMoodTheme(mood)

  const bars = useMemo(() =>
    Array.from({ length: BAR_COUNT }, (_, i) => {
      // Shape: tall in center, shorter at edges — like a real spectrum
      const center = (BAR_COUNT - 1) / 2
      const distFromCenter = Math.abs(i - center) / center
      const baseMax = 70 - distFromCenter * 40 + Math.sin(i * 1.3) * 15
      return {
        id: i,
        maxPct: Math.max(15, baseMax),
        duration: 0.5 + Math.random() * 0.9,
        delay: (i / BAR_COUNT) * 0.5,
      }
    }), [])

  const intensity = Math.max(0.2, hype / 100)

  return (
    <div
      className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4 flex flex-col"
      style={{ minHeight: '200px' }}
    >
      <span className="text-xs font-semibold uppercase tracking-widest text-white/40 mb-3">
        Audio Spectrum
      </span>
      <div className="flex-1 flex items-end justify-between gap-1">
        {bars.map(bar => (
          <motion.div
            key={bar.id}
            className="flex-1 rounded-t-sm"
            style={{
              background: `linear-gradient(to top, ${theme.accent}, ${theme.glow}88)`,
              minWidth: 4,
              opacity: 0.85,
            }}
            animate={{
              height: [
                `${6 * intensity}%`,
                `${bar.maxPct * intensity}%`,
                `${10 * intensity}%`,
                `${bar.maxPct * 0.55 * intensity}%`,
                `${6 * intensity}%`,
              ],
            }}
            transition={{
              duration: bar.duration,
              delay: bar.delay,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>
    </div>
  )
}
