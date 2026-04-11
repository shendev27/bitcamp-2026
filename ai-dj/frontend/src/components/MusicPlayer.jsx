import { motion, AnimatePresence } from 'framer-motion'
import { getMoodTheme } from '../theme'

export default function MusicPlayer({ state, mood }) {
  const theme = getMoodTheme(mood)
  const track = state?.track ?? { name: '-', artist: '-', art_url: '' }

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur overflow-hidden">
      <div className="flex items-stretch">
        {/* Album art — fills the left side */}
        {track.art_url ? (
          <img
            src={track.art_url}
            alt="album"
            className="w-24 h-24 object-cover flex-shrink-0"
            style={{ boxShadow: `4px 0 20px ${theme.glow}66` }}
          />
        ) : (
          <div
            className="w-24 h-24 flex-shrink-0 flex items-center justify-center text-xs font-bold"
            style={{ background: `${theme.glow}33`, color: theme.accent }}
          >
            MUSIC
          </div>
        )}

        {/* Right side: track info + controls */}
        <div className="flex-1 min-w-0 px-4 py-2 flex flex-col justify-between">
          {/* Track info */}
          <AnimatePresence mode="wait">
            <motion.div
              key={track.name}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.3 }}
            >
              <p className="font-semibold truncate text-white text-sm leading-tight">{track.name}</p>
              <p className="text-xs text-white/50 truncate">{track.artist}</p>
            </motion.div>
          </AnimatePresence>

          {/* Playback controls */}
          <div className="flex items-center justify-center gap-5">
            <button className="text-white/40 hover:text-white transition-colors text-base leading-none">⏮</button>
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ background: theme.accent, boxShadow: `0 0 14px ${theme.glow}88` }}
            >
              <span style={{ color: '#000', fontSize: 14, lineHeight: 1 }}>⏸</span>
            </div>
            <button className="text-white/40 hover:text-white transition-colors text-base leading-none">⏭</button>
          </div>

          {/* Progress bar */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-white/40">0:00</span>
            <div className="flex-1 h-1 rounded-full bg-white/10">
              <div className="h-full rounded-full w-[30%]" style={{ background: theme.accent }} />
            </div>
            <span className="text-[10px] text-white/40">3:45</span>
          </div>
        </div>
      </div>

      {/* DJ Says */}
      <div className="px-4 py-2 border-t border-white/10">
        <AnimatePresence mode="wait">
          <motion.p
            key={state?.commentary}
            className="text-xs text-white/60"
            initial={{ opacity: 0, x: 6 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -6 }}
            transition={{ duration: 0.3 }}
          >
            <span className="font-semibold uppercase tracking-widest text-white/30 mr-2">DJ says...</span>
            {state?.commentary || '...'}
          </motion.p>
        </AnimatePresence>
      </div>
    </div>
  )
}
