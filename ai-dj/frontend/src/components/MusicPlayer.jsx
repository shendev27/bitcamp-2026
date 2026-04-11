import { motion, AnimatePresence } from 'framer-motion'
import { getMoodTheme } from '../theme'

export default function MusicPlayer({ state, mood }) {
  const theme = getMoodTheme(mood)
  const track = state?.track ?? { name: '-', artist: '-', art_url: '' }

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-3">
      <div className="flex items-center gap-5">
        {/* Album art */}
        {track.art_url ? (
          <img
            src={track.art_url}
            alt="album"
            className="w-16 h-16 rounded-lg flex-shrink-0 object-cover"
            style={{ boxShadow: `0 0 24px ${theme.glow}99` }}
          />
        ) : (
          <div
            className="w-16 h-16 rounded-lg flex-shrink-0 flex items-center justify-center text-xs font-bold"
            style={{ background: `${theme.glow}33`, color: theme.accent }}
          >
            MUSIC
          </div>
        )}

        {/* Controls column */}
        <div className="flex-1 min-w-0">
          {/* Track info */}
          <AnimatePresence mode="wait">
            <motion.div
              key={track.name}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.3 }}
            >
              <p className="font-semibold truncate text-white">{track.name}</p>
              <p className="text-sm text-white/50 truncate">{track.artist}</p>
            </motion.div>
          </AnimatePresence>

          {/* Playback controls */}
          <div className="flex items-center justify-center gap-6 my-2">
            <button className="text-white/40 hover:text-white transition-colors text-lg leading-none">⏮</button>
            <div
              className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ background: theme.accent, boxShadow: `0 0 16px ${theme.glow}88` }}
            >
              <span style={{ color: '#000', fontSize: 16, lineHeight: 1 }}>⏸</span>
            </div>
            <button className="text-white/40 hover:text-white transition-colors text-lg leading-none">⏭</button>
          </div>

          {/* Progress bar */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-white/40 w-8">0:00</span>
            <div className="flex-1 h-1 rounded-full bg-white/10">
              <div
                className="h-full rounded-full"
                style={{ width: '30%', background: theme.accent }}
              />
            </div>
            <span className="text-xs text-white/40 w-8 text-right">3:45</span>
          </div>
        </div>
      </div>

      {/* DJ Says */}
      <div className="mt-4 pt-3 border-t border-white/10">
        <AnimatePresence mode="wait">
          <motion.p
            key={state?.commentary}
            className="text-sm text-white/70"
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -8 }}
            transition={{ duration: 0.35 }}
          >
            <span className="text-xs font-semibold uppercase tracking-widest text-white/40 mr-2">
              DJ says...
            </span>
            {state?.commentary || '...'}
          </motion.p>
        </AnimatePresence>
      </div>
    </div>
  )
}
