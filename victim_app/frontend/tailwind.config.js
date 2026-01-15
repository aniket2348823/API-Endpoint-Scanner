/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#0a0a0a',
                surface: '#121212',
                primary: '#06b6d4', // Cyan-500
                secondary: '#8b5cf6', // Violet-500
                danger: '#ef4444',
            },
            fontFamily: {
                mono: ['"Fira Code"', 'monospace'],
                sans: ['Inter', 'sans-serif'],
            },
            animation: {
                'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glitch': 'glitch 0.2s ease-in-out infinite',
            },
        },
    },
    plugins: [],
}
