import axios from 'axios';

const apiClient = axios.create({
    // 使用 import.meta.env 获取环境变量，生产环境默认为 /api
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('auth_token');
        if (token && config.headers) {
            // 拼接 Bearer 协议前缀
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
        // 排除掉登录接口本身的 401（防止登录失败时页面死循环刷新）
        const isLoginRequest = error.config.url.includes('/token/');

        if (error.response?.status === 401 && !isLoginRequest) {
            localStorage.removeItem('auth_token');
            // 触发 main.ts 的 rootComponent 重新判定
            window.location.reload(); 
        }

        if (error.response) {
            console.error(`[API Error] ${error.response.status}:`, error.response.data);
        } else {
            console.error('[API Error]:', error.message);
        }
        return Promise.reject(error);
    }
);

export default apiClient;