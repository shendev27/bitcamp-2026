import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { useWS } from './hooks/useWS'
import { getMoodTheme } from './theme'
import VideoPanel from './components/VideoPanel'
import AudioSpectrum from './components/AudioSpectrum'
import MusicPlayer from './components/MusicPlayer'
import HypeBar from './components/HypeBar'
import PeopleCard from './components/PeopleCard'
import EmotionCard from './components/EmotionCard'

function Starfield() {
  const stars = useMemo(() =>
    Array.from({ length: 200 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2 + 0.5,
      delay: Math.random() * 5,
      duration: Math.random() * 3 + 2,
    })), [])

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none" style={{ zIndex: 0 }}>
      {stars.map(s => (
        <motion.div
          key={s.id}
          className="absolute rounded-full bg-white"
          style={{ left: `${s.x}%`, top: `${s.y}%`, width: s.size, height: s.size }}
          animate={{ opacity: [0.1, 0.9, 0.1] }}
          transition={{ duration: s.duration, delay: s.delay, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}
      <div style={{
        position: 'absolute', top: '15%', left: '10%',
        width: 500, height: 500, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(90,40,220,0.18) 0%, transparent 70%)',
        filter: 'blur(70px)',
      }} />
      <div style={{
        position: 'absolute', bottom: '20%', right: '8%',
        width: 400, height: 400, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(220,40,100,0.14) 0%, transparent 70%)',
        filter: 'blur(60px)',
      }} />
      <div style={{
        position: 'absolute', top: '55%', left: '38%',
        width: 350, height: 350, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(30,120,255,0.12) 0%, transparent 70%)',
        filter: 'blur(50px)',
      }} />
    </div>
  )
}

export default function App() {
  const { state, connected } = useWS()
  const mood = state?.mood ?? 'dead'
  const theme = getMoodTheme(mood)
  const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost'

  const setMood = async (next) => {
    try {
      await fetch(`http://${host}:8000/debug/mood/${next}`, { method: 'POST' })
    } catch (_) {}
  }

  return (
    <div className="min-h-screen relative" style={{ background: '#050510', fontFamily: 'Inter, sans-serif' }}>
      <Starfield />

      <div className="relative px-4 pt-3 pb-2" style={{ zIndex: 1 }}>
        {/* Header */}
        <div className="text-center mb-2">
          <h1
            className="text-xl font-extrabold tracking-widest"
            style={{ color: theme.accent, textShadow: `0 0 30px ${theme.glow}` }}
          >
            PASS THE AUX
          </h1>
        </div>

        {/* 3-column — equal side widths so video is perfectly centered */}
        <div className="max-w-5xl mx-auto flex gap-5 items-stretch">
          {/* Left: Audio Spectrum — same width as right so video centers */}
          <div className="w-44 flex-shrink-0">
            <AudioSpectrum hype={state?.hype ?? 0} />
          </div>

          {/* Center: Video */}
          <div className="flex-1" style={{ zIndex: 1 }}>
            <VideoPanel mood={mood} connected={connected} />
          </div>

          {/* Right: People + Mood */}
          <div className="w-44 flex-shrink-0 flex flex-col gap-4" style={{ paddingTop: 44 }}>
            <PeopleCard count={state?.people_count ?? 0} mood={mood} />
            <EmotionCard mood={mood} />
          </div>
        </div>

        {/* Bottom — aligned under the centered video */}
        <div className="max-w-lg mx-auto mt-6 flex flex-col gap-4">
          <MusicPlayer state={state} mood={mood} />
          <HypeBar hype={state?.hype ?? 0} mood={mood} />
          <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur px-4 py-3">
            <span className="text-xs font-semibold uppercase tracking-widest text-white/40">Test Switch</span>
            <div className="mt-2 flex flex-wrap gap-2">
              {['dead', 'chill', 'neutral', 'hype', 'peak'].map((m) => (
                <button
                  key={m}
                  onClick={() => setMood(m)}
                  className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest border border-white/10"
                  style={{ color: theme.accent, background: `${theme.glow}22` }}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
