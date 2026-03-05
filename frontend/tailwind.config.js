import daisyui from 'daisyui'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        tsmonitor: {
          "primary": "#3b82f6",
          "secondary": "#6366f1",
          "accent": "#f59e0b",
          "neutral": "#1e293b",
          "base-100": "#0f172a",
          "info": "#3abff8",
          "success": "#22c55e",
          "warning": "#f59e0b",
          "error": "#ef4444",
        },
      },
      "dark",
    ],
    darkTheme: "tsmonitor",
  },
}