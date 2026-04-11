import { getMoodTheme } from '../theme'

/**
 * Left panel: MJPEG webcam feed with bounding-box overlays (drawn server-side).
 * Falls back to a placeholder if the feed isn't available.
 */
export default function VideoPanel({ mood = 'dead', connected = false }) {
  const theme = getMoodTheme(mood)

  return (
    <div
      className="relative rounded-2xl overflow-hidden border border-white/10 bg-black"
      style={{
        boxShadow: `0 0 40px ${theme.glow}55`,
        transition: 'box-shadow 0.3s ease',
      }}
    >
      {/* MJPEG feed */}
      <img
        src="http://localhost:8000/video_feed"
        alt="Live webcam"
        className="w-full h-full object-cover"
        style={{ display: 'block', minHeight: '360px' }}
      />

      {/* Connection badge */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5 rounded-full px-3 py-1 bg-black/60 backdrop-blur border border-white/10">
        <span
          className="w-2 h-2 rounded-full"
          style={{ background: connected ? '#22c55e' : '#ef4444' }}
        />
        <span className="text-xs font-medium text-white/70">
          {connected ? 'LIVE' : 'CONNECTING…'}
        </span>
      </div>

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
  )
}
