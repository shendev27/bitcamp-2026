import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

const SEGMENTS = 24

function segmentColor(i) {
  if (i < 14) return '#22c55e'
  if (i < 19) return '#eab308'
  return '#ef4444'
}

export default function AudioSpectrum({ hype }) {
  const [level, setLevel] = useState(0)
  const [micActive, setMicActive] = useState(false)
  const rafRef = useRef(null)
  const analyserRef = useRef(null)
  const streamRef = useRef(null)

  useEffect(() => {
    let ctx

    async function startMic() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        streamRef.current = stream
        ctx = new AudioContext()
        const source = ctx.createMediaStreamSource(stream)
        const analyser = ctx.createAnalyser()
        analyser.fftSize = 256
        analyser.smoothingTimeConstant = 0.75
        source.connect(analyser)
        analyserRef.current = analyser
        setMicActive(true)

        const data = new Uint8Array(analyser.frequencyBinCount)

        function tick() {
          analyser.getByteFrequencyData(data)
          // Average of all frequency bins → 0–255 → 0–100
          const avg = data.reduce((a, b) => a + b, 0) / data.length
          setLevel((avg / 255) * 100)
          rafRef.current = requestAnimationFrame(tick)
        }
        tick()
      } catch {
        setMicActive(false)
      }
    }

    startMic()

    return () => {
      cancelAnimationFrame(rafRef.current)
      streamRef.current?.getTracks().forEach(t => t.stop())
      ctx?.close()
    }
  }, [])

  // Fall back to hype-based jitter when mic is unavailable
  useEffect(() => {
    if (micActive) return
    const id = setInterval(() => {
      const jitter = (Math.random() - 0.4) * 28
      setLevel(Math.max(0, Math.min(100, hype + jitter)))
    }, 120)
    return () => clearInterval(id)
  }, [micActive, hype])

  const activeCount = Math.round((level / 100) * SEGMENTS)

  return (
    <div
      className="rounded-xl border border-white/10 bg-white/5 backdrop-blur h-full flex flex-col items-center"
      style={{ padding: '10px 8px' }}
    >
      <span className="text-[9px] font-semibold uppercase tracking-widest text-white/30 mb-2">
        {micActive ? 'MIC' : 'VOL'}
      </span>

      <div className="flex-1 flex flex-col-reverse justify-start gap-[3px] w-full">
        {Array.from({ length: SEGMENTS }, (_, i) => {
          const active = i < activeCount
          const color = segmentColor(i)
          return (
            <motion.div
              key={i}
              className="w-full rounded-sm"
              style={{ height: 8, flexShrink: 0 }}
              animate={{
                background: active ? color : 'rgba(255,255,255,0.06)',
                boxShadow: active ? `0 0 6px ${color}99` : 'none',
                opacity: active ? 1 : 0.4,
              }}
              transition={{ duration: 0.05 }}
            />
          )
        })}
      </div>

      <div className="flex flex-col-reverse justify-between w-full mt-1" style={{ height: 36 }}>
        {['0', '50', '100'].map(label => (
          <span key={label} className="text-[8px] text-white/25 text-center leading-none">
            {label}
          </span>
        ))}
      </div>
    </div>
  )
}
