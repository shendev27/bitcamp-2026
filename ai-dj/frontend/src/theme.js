/** Maps mood → visual theme tokens used throughout the UI. */
export const MOOD_THEME = {
  dead: {
    glow: '#1a1a40',
    accent: '#6666aa',
    gradient: 'from-[#0a0a0f] via-[#0d0d1a] to-[#0a0a0f]',
    label: 'DEAD',
    barColor: '#6666aa',
  },
  chill: {
    glow: '#2d4a7a',
    accent: '#4d8aff',
    gradient: 'from-[#0a0a0f] via-[#0d1525] to-[#0a0a0f]',
    label: 'CHILL',
    barColor: '#4d8aff',
  },
  neutral: {
    glow: '#4a7a4a',
    accent: '#66cc66',
    gradient: 'from-[#0a0a0f] via-[#0d1a0d] to-[#0a0a0f]',
    label: 'NEUTRAL',
    barColor: '#66cc66',
  },
  hype: {
    glow: '#ff6600',
    accent: '#ff8833',
    gradient: 'from-[#0a0a0f] via-[#1a0800] to-[#0a0a0f]',
    label: 'HYPE',
    barColor: '#ff6600',
  },
  peak: {
    glow: '#ff0066',
    accent: '#ff33aa',
    gradient: 'from-[#0a0a0f] via-[#1a0015] to-[#0a0a0f]',
    label: 'PEAK',
    barColor: '#ff0066',
  },
}

export function getMoodTheme(mood) {
  return MOOD_THEME[mood] ?? MOOD_THEME.neutral
}
