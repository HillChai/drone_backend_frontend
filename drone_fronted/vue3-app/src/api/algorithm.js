import api from "./index";
import axios from "axios";

// 获取算法列表
export const getAlgorithms = async (page = 1, limit = 10) => {
    return await api.get(`/algorithms?page=${page}&limit=${limit}`);
};

// 创建算法（处理唯一性错误）
export const createAlgorithm = async (data) => {
    try {
        return await api.post("/algorithms", data);
    } catch (error) {
        if (error.response && error.response.status === 400) {
            console.warn("⚠️ 该算法已存在:", error.response.data.detail);
        } else {
            console.error("创建算法失败:", error);
        }
        throw error;
    }
};

// 删除算法
export const deleteAlgorithm = (id) => api.delete(`/algorithms/${id}`);

export const uploadAlgorithm = async (formData) => {
    const res = await axios.post("/api/upload-algorithm/", formData);
    return res.data;
};

export const saveAlgorithm = async (data) => {
    return await axios.post("/api/save-algorithm/", new URLSearchParams(data));
};