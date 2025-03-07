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

// **获取算法代码内容**
export const getAlgorithmContent = async (filePath) => {
    try {
        console.log("📡 请求算法代码:", filePath);
        const res = await api.get("/algorithms/get-algorithm-code/", {
            params: { file_path: filePath }
        });

        console.log("🌍 API 响应:", res.data);

        if (!res.data || typeof res.data !== "object" || !("code" in res.data)) {
            console.warn("⚠️ API 响应格式异常", res.data);
            return { code: "" };
        }

        return res.data;
    } catch (error) {
        console.error("❌ 无法获取算法内容", error);
        return { code: "" };
    }
};


export const saveAlgorithm = async (name, file) => {
    try {
        const formData = new FormData();
        formData.append("name", name);   // 确保字段名和后端匹配
        formData.append("file", file);   // 确保是一个 `File` 对象

        const res = await api.post("/algorithms/save-algorithm/", formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });

        return res.data;
    } catch (error) {
        console.error("保存算法失败:", error);
        throw error;
    }
};

export const listAlgorithmFiles = async (filePath) => {
    try {
        console.log("🔍 请求算法文件列表，前缀:", filePath);
        const res = await api.get("/algorithms/list-algorithm-files/", { params: { prefix: filePath } });

        console.log("✅ API 返回的算法文件:", res.data);
        return res.data;
    } catch (error) {
        console.error("❌ 获取算法文件列表失败:", error);
        return { files: [] };  // 避免 `undefined`
    }
};

