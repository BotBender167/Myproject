import axios from 'axios'

// ── Axios Instance ────────────────────────────────────────────────────────────

const API_KEY = import.meta.env.VITE_API_KEY ?? 'sentinel-dev-key'

const api = axios.create({
    baseURL: 'https://omniroute-1ety.onrender.com',
    timeout: 10_000,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
    },
})

// ── Request Interceptor ───────────────────────────────────────────────────────

api.interceptors.request.use(
    (config) => {
        // Ensure the API key is always present (in case headers were mutated)
        config.headers['X-API-Key'] = API_KEY
        return config
    },
    (error) => {
        console.error('[Sentinel API] Request config error:', error)
        return Promise.reject(error)
    }
)

// ── Response Interceptor ──────────────────────────────────────────────────────

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (!error.response) {
            // Network error — backend not reachable
            console.error(
                '[Sentinel API] Backend unreachable at https://omniroute-1ety.onrender.com'
            )
            return Promise.reject(
                new Error('Backend unreachable')
            )
        }

        const status = error.response?.status
        const detail = error.response?.data?.detail ?? 'Unknown error'

        if (status === 401) {
            console.error('[Sentinel API] 401 Unauthorized — check X-API-Key header')
            return Promise.reject(new Error('API key invalid or missing'))
        }

        if (status === 404) {
            console.error(`[Sentinel API] 404 Not Found: ${error.config?.url}`)
            return Promise.reject(new Error(`Resource not found: ${detail}`))
        }

        if (status === 422) {
            console.error(`[Sentinel API] 422 Validation Error: ${detail}`)
            return Promise.reject(new Error(`Validation error: ${detail}`))
        }

        if (status && status >= 500) {
            console.error(`[Sentinel API] ${status} Server Error: ${detail}`)
            return Promise.reject(new Error('Server error — check uvicorn logs'))
        }

        return Promise.reject(error)
    }
)

export default api
