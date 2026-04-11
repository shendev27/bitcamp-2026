import { motion, AnimatePresence } from 'framer-motion'
import { getMoodTheme } from '../theme'

function formatMs(ms) {
  if (ms === null || ms === undefined) return null
  const total = Math.max(0, Math.floor(ms / 1000))
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

/**
 * Current track, DJ reasoning, and rotating commentary.
 */
export default function DJPanel({ state }) {
  const mood = state?.mood ?? 'dead'
  const theme = getMoodTheme(mood)
  const track = state?.track ?? { name: '-', artist: '-', art_url: '' }
  const startLabel = formatMs(track.start_ms)
  const startIndex = track.start_track_index

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4 flex flex-col gap-4">
      {/* Track info */}
      <div className="flex items-center gap-3">
        {track.art_url ? (
          <img
            src={track.art_url}
            alt="album art"
            className="w-14 h-14 rounded-lg object-cover flex-shrink-0"
            style={{ boxShadow: `0 0 16px ${theme.glow}88` }}
          />
        ) : (
          <div
            className="w-14 h-14 rounded-lg flex-shrink-0 flex items-center justify-center text-[10px] font-bold"
            style={{ background: `${theme.glow}33`, color: theme.accent }}
          >
            MUSIC
          </div>
        )}
        <div className="min-w-0">
          <p className="font-semibold truncate text-white">{track.name}</p>
          <p className="text-sm text-white/50 truncate">{track.artist}</p>
          {(startLabel || startIndex) && (
            <p className="text-xs text-white/40 truncate">
              {startIndex ? `Track #${startIndex}` : 'Track'}
              {startLabel ? `  •  Start @ ${startLabel}` : ''}
            </p>
          )}
        </div>
      </div>

      {/* Reasoning */}
      <div>
        <span className="text-xs font-semibold uppercase tracking-widest text-white/40">Reasoning</span>
        <AnimatePresence mode="wait">
          <motion.p
            key={state?.action_reason}
            className="text-sm mt-1 text-white/70"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.3 }}
          >
            {state?.action_reason || 'Warming up...'}
          </motion.p>
        </AnimatePresence>
      </div>

      {/* Commentary */}
      <div
        className="rounded-lg p-3"
        style={{ background: `${theme.glow}22`, border: `1px solid ${theme.glow}44` }}
      >
        <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: theme.accent }}>
          DJ Says
        </span>
        <AnimatePresence mode="wait">
          <motion.p
            key={state?.commentary}
            className="mt-1 font-medium text-white"
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -8 }}
            transition={{ duration: 0.35 }}
          >
            {state?.commentary || '...'}
          </motion.p>
        </AnimatePresence>
      </div>
    </div>
  )
}