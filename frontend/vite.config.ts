import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    build: {
        // Production build optimizations
        minify: 'terser',
        sourcemap: false,
        rollupOptions: {
            output: {
                // Code splitting for better caching
                manualChunks: {
                    vendor: ['react', 'react-dom', 'react-router-dom'],
                    charts: ['plotly.js', 'react-plotly.js', 'recharts'],
                    ui: ['framer-motion', 'lucide-react'],
                },
            },
        },
        // Increase chunk size warning limit
        chunkSizeWarningLimit: 1000,
    },
    server: {
        // Development server configuration
        port: 5173,
        strictPort: true,
    },
    preview: {
        // Preview server configuration
        port: 4173,
    },
})
