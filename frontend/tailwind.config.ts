
import type { Config } from "tailwindcss";

export default {
	darkMode: ["class"],
	content: [
		"./pages/**/*.{ts,tsx}",
		"./components/**/*.{ts,tsx}",
		"./app/**/*.{ts,tsx}",
		"./src/**/*.{ts,tsx}",
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px'
			}
		},
		extend: {
			fontFamily: {
				sans: ['Inter', 'sans-serif'],
				mono: ['IBM Plex Mono', 'monospace'],
				heading: ['IBM Plex Mono', 'monospace'],
			},
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))', // Updated to use CSS variable
					foreground: 'hsl(var(--accent-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				brand: {
					blue: '#2563eb',
					purple: '#7F5AF0',
					cyan: '#06b6d4',
					dark: '#111827',
					light: '#F9FAFB',
					neon: '#3BFFD3', // Neon Turquoise accent color
				},
				charcoal: '#14161B',
				navy: '#0D1B2A',
				darkgray: '#1E2128', // Used for section surfaces
				'card-dark': '#1E2128',
				'text-secondary': '#C1CAD7',
				sidebar: {
					DEFAULT: 'hsl(var(--sidebar-background))',
					foreground: 'hsl(var(--sidebar-foreground))',
					primary: 'hsl(var(--sidebar-primary))',
					'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
					accent: 'hsl(var(--sidebar-accent))',
					'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
					border: 'hsl(var(--sidebar-border))',
					ring: 'hsl(var(--sidebar-ring))'
				}
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			keyframes: {
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				},
				'float': {
					'0%': {
						transform: 'translateY(0px)'
					},
					'50%': {
						transform: 'translateY(-10px)'
					},
					'100%': {
						transform: 'translateY(0px)'
					}
				},
				'fade-in': {
					'0%': {
						opacity: '0',
						transform: 'translateY(20px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				'scale-in': {
					'0%': {
						opacity: '0',
						transform: 'scale(0.95)'
					},
					'100%': {
						opacity: '1',
						transform: 'scale(1)'
					}
				},
				'blob': {
					'0%': {
						transform: 'scale(1) translate(0px, 0px)'
					},
					'33%': {
						transform: 'scale(1.1) translate(20px, -10px)'
					},
					'66%': {
						transform: 'scale(0.9) translate(-10px, 10px)'
					},
					'100%': {
						transform: 'scale(1) translate(0px, 0px)'
					}
				},
				'grid-appear': {
					'0%': {
						opacity: '0',
					},
					'100%': {
						opacity: '0.08',
					}
				},
				'ripple': {
					'0%': {
						boxShadow: '0 0 0 0 rgba(59, 255, 211, 0.3)',
					},
					'100%': {
						boxShadow: '0 0 0 12px rgba(59, 255, 211, 0)',
					}
				},
				'pulse-subtle': {
					'0%': {
						opacity: '1',
					},
					'50%': {
						opacity: '0.8',
					},
					'100%': {
						opacity: '1',
					}
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'float': 'float 6s ease-in-out infinite',
				'fade-in': 'fade-in 0.8s ease-out forwards',
				'scale-in': 'scale-in 0.3s ease-out',
				'blob': 'blob 8s infinite ease-in-out',
				'grid-appear': 'grid-appear 0.2s ease-out forwards',
				'ripple': 'ripple 0.6s ease-out',
				'pulse-subtle': 'pulse-subtle 0.5s ease-in-out',
			}
		}
	},
	plugins: [require("tailwindcss-animate")],
} satisfies Config;
