import { useState, useEffect, useRef } from 'react'

const SEGMENTS = 24
const GAIN = 4

function segmentColor(i, total) {
  const hue = Math.round(120 - (i / (total - 1)) * 120)
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
        analyser.smoothingTimeConstant = 0.55
        source.connect(analyser)
        setMicActive(true)

        const data = new Uint8Array(analyser.frequencyBinCount)
        function tick() {
          analyser.getByteFrequencyData(data)
          const rms = Math.sqrt(data.reduce((sum, v) => sum + v * v, 0) / data.length)
          setLevel(Math.min(100, (rms / 255) * 100 * GAIN))
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
      className="rounded-xl border border-white/10 bg-white/5 backdrop-blur h-full flex flex-col"
      style={{ padding: '10px 10px 10px 6px' }}
    >
      {/* Label */}
      <span className="text-[9px] font-semibold uppercase tracking-widest text-white/30 mb-2 text-center">
        {micActive ? 'MIC' : 'VOL'}
      </span>

      {/* Meter row: scale labels | bars */}
      <div className="flex-1 flex flex-row gap-2 min-h-0">
        {/* Scale labels — pinned top/middle/bottom alongside bars */}
        <div className="flex flex-col justify-between py-0.5 flex-shrink-0">
          <span className="text-[8px] text-white/30 leading-none">100</span>
          <span className="text-[8px] text-white/30 leading-none">50</span>
          <span className="text-[8px] text-white/30 leading-none">0</span>
        </div>

        {/* Segments — fill full height */}
        <div className="flex-1 flex flex-col-reverse gap-[2px] min-h-0">
          {Array.from({ length: SEGMENTS }, (_, i) => {
            const active = i < activeCount
            const color = segmentColor(i, SEGMENTS)
            return (
              <div
                key={i}
                className="flex-1 rounded-sm w-full"
                style={{
                  background: active ? color : 'rgba(255,255,255,0.06)',
                  boxShadow: active ? `0 0 7px ${color}bb` : 'none',
                  opacity: active ? 1 : 0.35,
                  transition: 'background 0.05s, box-shadow 0.05s, opacity 0.05s',
                }}
              />
            )
          })}
        </div>
      </div>
    </div>
  )
}
