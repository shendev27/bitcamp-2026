import { motion, AnimatePresence } from 'framer-motion'
import { useWS } from './hooks/useWS'
import { getMoodTheme } from './theme'
import VideoPanel from './components/VideoPanel'
import StatsCards from './components/StatsCards'
import DJPanel from './components/DJPanel'
import HypeBar from './components/HypeBar'

export default function App() {
  const { state, connected } = useWS()
  const mood = state?.mood ?? 'dead'
  const theme = getMoodTheme(mood)

  return (
    <motion.div
      className={`min-h-screen bg-gradient-to-br ${theme.gradient} p-4`}
      animate={{ background: undefined }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      style={{ fontFamily: 'Inter, sans-serif' }}
    >
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-4 flex items-center justify-between">
        <h1
          className="text-xl font-extrabold tracking-tight"
          style={{ color: theme.accent, textShadow: `0 0 20px ${theme.glow}` }}
        >
          PASS THE AUX
        </h1>
        <span className="text-xs text-white/30 font-mono">
          {state ? `${state.ts ? new Date(state.ts * 1000).toLocaleTimeString() : ''}` : 'waiting…'}
        </span>
      </div>

      {/* Main layout */}
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-4">
        {/* Left 60%: video */}
        <div className="lg:w-[60%]">
          <VideoPanel mood={mood} connected={connected} />
        </div>

        {/* Right 40%: panels */}
        <div className="lg:w-[40%] flex flex-col gap-3">
          <StatsCards state={state} />
          <HypeBar hype={state?.hype ?? 0} mood={mood} />
          <DJPanel state={state} />
        </div>
      </div>
    </motion.div>
  )
}
