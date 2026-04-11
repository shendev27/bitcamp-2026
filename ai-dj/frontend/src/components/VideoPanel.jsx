import { motion } from 'framer-motion'
import { getMoodTheme } from '../theme'
import redSaturn from '../red.svg'
import greenAlien from '../green.svg'

export default function VideoPanel({ mood = 'dead', connected = false }) {
  const theme = getMoodTheme(mood)
  const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost'

  return (
    <div className="relative" style={{ paddingTop: 36, paddingBottom: 36 }}>
      {/* Red saturn — floats off the top-left corner of the video */}
      <motion.img
        src={redSaturn}
        alt=""
        className="absolute pointer-events-none"
        style={{ top: -30, left: -40, width: 160, height: 160, zIndex: 20 }}
        animate={{ y: [0, -12, 0], rotate: [-4, 4, -4] }}
        transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Spaceship window frame — outer ring */}
      <div
        style={{
          borderRadius: 24,
          padding: 3,
          background: 'linear-gradient(135deg, #6b7280 0%, #374151 40%, #9ca3af 60%, #4b5563 100%)',
          boxShadow: '0 0 0 1px #1f2937, 0 8px 32px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.1)',
        }}
      >
        {/* Inner bezel */}
        <div
          style={{
            borderRadius: 21,
            padding: 6,
            background: 'linear-gradient(180deg, #1f2937 0%, #111827 100%)',
            boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.9), inset 0 -1px 0 rgba(255,255,255,0.05)',
          }}
        >
          {/* Rivet dots — top */}
          <div className="flex justify-between px-4 mb-1">
            {[...Array(6)].map((_, i) => (
              <div key={i} style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'radial-gradient(circle at 35% 35%, #9ca3af, #374151)',
                boxShadow: '0 1px 2px rgba(0,0,0,0.8)',
              }} />
            ))}
          </div>

          {/* Video feed */}
          <div className="relative overflow-hidden" style={{ borderRadius: 12 }}>
            <img
              src={`http://${host}:8000/video_feed`}
              alt=""
              className="w-full object-cover"
              style={{ display: 'block', minHeight: '400px', maxHeight: '60vh' }}
            />
            {/* Mood label */}
            <div
              className="absolute bottom-3 left-3 rounded-full px-3 py-1 text-xs font-bold tracking-widest"
              style={{
                background: `${theme.glow}55`,
                color: theme.accent,
                border: `1px solid ${theme.accent}44`,
                backdropFilter: 'blur(8px)',
                transition: 'all 0.3s ease',
              }}
            >
              {theme.label}
            </div>
          </div>

          {/* Rivet dots — bottom */}
          <div className="flex justify-between px-4 mt-1">
            {[...Array(6)].map((_, i) => (
              <div key={i} style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'radial-gradient(circle at 35% 35%, #9ca3af, #374151)',
                boxShadow: '0 1px 2px rgba(0,0,0,0.8)',
              }} />
            ))}
          </div>
        </div>
      </div>

      {/* Green alien — floats off the bottom-right corner of the video */}
      <motion.img
        src={greenAlien}
        alt=""
        className="absolute pointer-events-none"
        style={{ bottom: -8, right: -20, width: 100, height: 100, zIndex: 20 }}
        animate={{ y: [0, -8, 0], rotate: [4, -4, 4] }}
        transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut', delay: 0.6 }}
      />
    </div>
  )
}
