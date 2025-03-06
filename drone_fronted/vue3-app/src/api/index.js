import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL, // 读取环境变量
    timeout: 5000,   // 请求超时时间
    headers: {
        "Content-Type": "application/json",
    },
});

export default api;
