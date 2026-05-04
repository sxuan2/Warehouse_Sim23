import axios from 'axios';

const apiClient = axios.create({
    // 保持你原本的 baseURL 和配置[cite: 13]
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

apiClient.interceptors.request.use(
    (config) => {
        // 保持你原本读取 auth_token 的逻辑[cite: 13]
        const token = localStorage.getItem('auth_token');
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // 核心修复：如果后端返回 401，说明没登录或令牌失效
        if (error.response?.status === 401) {
            localStorage.removeItem('auth_token');
            // 因为你没装路由，这里直接刷新页面，由下文 main.ts 控制显示登录框
            window.location.reload(); 
        }

        // 保持你原本的 console.error 处理逻辑[cite: 13]
        if (error.response) {
            console.error(`[API Error] ${error.response.status}:`, error.response.data);
        } else if (error.request) {
            console.error('[API Error] No response received from server:', error.request);
        } else {
            console.error('[API Error] Request setup failed:', error.message);
        }
        return Promise.reject(error);
    }
);

export default apiClient;