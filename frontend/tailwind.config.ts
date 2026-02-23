import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        progress: '#22c55e',
        maintaining: '#3b82f6',
        overreaching: '#f97316',
        detraining: '#9ca3af',
        recovery: '#06b6d4',
        power: '#a855f7',
        raceprep: '#ef4444'
      }
    }
  },
  plugins: []
} satisfies Config;
