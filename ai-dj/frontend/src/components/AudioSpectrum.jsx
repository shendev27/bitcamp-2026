import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

const SEGMENTS = 24
const GAIN = 8  // multiply raw signal so normal speech reaches mid-meter

// Smooth green → yellow → red gradient using HSL
function segmentColor(i, total) {
  const hue = Math.round(120 - (i / (total - 1)) * 120)  // 120 = green, 0 = red
  return `hsl(${hue}, 100%, 45%)`
}

export default function AudioSpectrum({ hype = 0 }) {
  const [level, setLevel] = useState(0)
  const [micActive, setMicActive] = useState(false)
  const rafRef = useRef(null)
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
        analyser.fftSize = 512
        analyser.smoothingTimeConstant = 0.55  // faster decay = more responsive
        source.connect(analyser)
        setMicActive(true)

        const data = new Uint8Array(analyser.frequencyBinCount)

        function tick() {
          analyser.getByteFrequencyData(data)
          // Use RMS of frequency bins for a more natural loudness reading
          const rms = Math.sqrt(data.reduce((sum, v) => sum + v * v, 0) / data.length)
          const boosted = Math.min(100, (rms / 255) * 100 * GAIN)
          setLevel(boosted)
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

  // Fallback: hype-based jitter when mic is unavailable
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
          const color = segmentColor(i, SEGMENTS)
          return (
            <div
              key={i}
              className="w-full rounded-sm"
              style={{
                height: 8,
                flexShrink: 0,
                background: active ? color : 'rgba(255,255,255,0.06)',
                boxShadow: active ? `0 0 7px ${color}bb` : 'none',
                opacity: active ? 1 : 0.35,
                transition: 'background 0.05s, box-shadow 0.05s, opacity 0.05s',
              }}
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
