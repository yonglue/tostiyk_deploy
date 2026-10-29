/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // —— 历史保留（勿删，有组件在用 --border / --background / --foreground）——
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",

        // —— 新增语义 token：复用 style.css 底部已有的 --color-* 变量 ——
        primary: "var(--color-content-primary)",
        secondary: "var(--color-content-secondary)",
        muted: "var(--color-content-muted)",
        surface: {
          DEFAULT: "var(--color-surface)",
          raised: "var(--color-surface-raised)",
          muted: "var(--color-surface-sunken)",
        },
        line: {
          DEFAULT: "var(--color-border)",
          strong: "var(--color-border-strong)",
        },
        accent: {
          DEFAULT: "var(--color-brand)",
          hover: "var(--color-brand-hover)",
        },
        danger: "var(--color-status-danger)",
        success: "var(--color-status-success)",
        warning: "var(--color-status-warning)",
        info: "var(--color-status-info)",
      },
      boxShadow: {
        'saas': '0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 10px -2px rgba(0, 0, 0, 0.03)',
        'saas-hover': '0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)',
        'saas-dark': '0 4px 20px -2px rgba(0, 0, 0, 0.3), 0 2px 10px -2px rgba(0, 0, 0, 0.2)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}