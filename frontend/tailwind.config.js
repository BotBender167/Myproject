/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            colors: {
                // Primary Brand — Amber
                amber: {
                    50: '#fffbeb',
                    100: '#fef3c7',
                    200: '#fde68a',
                    300: '#fcd34d',
                    400: '#ffb940',
                    500: '#ff9d00',
                    600: '#e08a00',
                    700: '#b87100',
                    800: '#92400e',
                    900: '#78350f',
                    950: '#451a03',
                },
                // Secondary Brand - Steel
                steel: {
                    400: '#9ca3af',
                    500: '#6b7280',
                    600: '#4b5563',
                    700: '#374151',
                    800: '#1f2937',
                    900: '#111827',
                }
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-in': 'slideIn 0.25s ease-out',
                'pulse-alert': 'pulseAlert 1.5s infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'scale(0.97)' },
                    '100%': { opacity: '1', transform: 'scale(1)' },
                },
                slideIn: {
                    '0%': { opacity: '0', transform: 'translateY(-6px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                pulseAlert: {
                    '0%, 100%': { opacity: '1', transform: 'scale(1)' },
                    '50%': { opacity: '0.6', transform: 'scale(1.05)' },
                }
            },
            boxShadow: {
                'glow-amber': '0 0 20px rgba(255,157,0,0.15)',
                'glow-amber-sm': '0 0 10px rgba(255,157,0,0.2)',
                'glow-red': '0 0 20px rgba(239,68,68,0.25)',
            },
            backgroundColor: {
                root: '#050505',
            },
            borderColor: {
                steel: '#444444',
            }
        },
    },
    plugins: [],
}
