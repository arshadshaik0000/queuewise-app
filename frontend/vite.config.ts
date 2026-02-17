import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    build: {
        outDir: '../backend/static',
        emptyOutDir: true,
    },
    server: {
        port: 3000,
        proxy: {
            '/queues': {
                target: 'http://127.0.0.1:5000',
                changeOrigin: true,
            },
        },
    },
})
