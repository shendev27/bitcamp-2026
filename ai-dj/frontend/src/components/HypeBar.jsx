import { motion } from 'framer-motion'
import { getMoodTheme } from '../theme'

/**
 * Animated hype meter bar (0–100). Pulses when hype > 85.
 */
export default function HypeBar({ hype = 0, mood = 'dead' }) {
  const theme = getMoodTheme(mood)
  const pct = Math.max(0, Math.min(100, hype))
  const isPeak = hype > 85

  const BANDS = [
    { label: 'SUPER CHILL', start: 0,  end: 20  },
    { label: 'CHILL',   start: 20, end: 40  },
    { label: 'NEUTRAL', start: 40, end: 60  },
    { label: 'HYPE',    start: 60, end: 80  },
    { label: 'PEAK',    start: 80, end: 100 },
  ]

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-semibold uppercase tracking-widest text-white/40">Hype</span>
        <motion.span
          className="text-sm font-bold"
          style={{ color: theme.accent }}
          animate={isPeak ? { scale: [1, 1.15, 1] } : { scale: 1 }}
          transition={isPeak ? { repeat: Infinity, duration: 0.6 } : {}}
        >
          {Math.round(pct)}
        </motion.span>
      </div>

      <div className="h-3 rounded-full bg-white/10 overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ background: theme.barColor }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />
      </div>

      {/* Band key */}
      <div className="flex mt-2">
        {BANDS.map(band => {
          const active = pct >= band.start && (band.end === 100 ? pct <= 100 : pct < band.end)
          return (
            <div key={band.label} className="flex-1 text-center">
              <span
                className="text-[9px] font-bold tracking-widest"
                style={{
                  color: active ? theme.accent : 'rgba(255,255,255,0.2)',
                  transition: 'color 0.3s',
                }}
              >
                {band.label}
              </span>
            </div>
          )
        })}
      </div>

      {isPeak && (
        <motion.div
          className="mt-1 text-center text-xs font-bold tracking-widest"
          style={{ color: theme.accent }}
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ repeat: Infinity, duration: 0.5 }}
        >
          ⚡ PEAK ⚡
        </motion.div>
      )}
    </div>
  )
}
