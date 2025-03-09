import api from "./index";
import axios from "axios";

// 获取算法列表
export const getAlgorithms = async (page = 1, limit = 20) => {
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
export const getAlgorithmContent = async (file_path) => {
    try {
        console.log("📡 请求算法代码:", file_path);

        const res = await api.get("/algorithms/get-algorithm-code/", {
            params: { file_path: file_path }  // ✅ 确保前端传递的是文件名，而非路径
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



export const saveAlgorithm = async (name, file, file_path) => {
    try {
        if (!file_path) {
            console.error("❌ file_path 为空，检查传递参数！");
            return;
        }

        const formData = new FormData();
        formData.append("name", name);  // 确保字段名与后端匹配
        formData.append("file", file);  // 确保 `file` 是 `File` 对象
        formData.append("file_path", file_path);  // 传递完整路径

        console.log("📤 发送算法数据:", name, file, file_path);

        const res = await api.post("/algorithms/save-algorithm/", formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });

        console.log("✅ 保存成功:", res.data);
        return res.data;  // {message, id, file_path}
    } catch (error) {
        console.error("❌ 保存算法失败:", error.response?.data || error);
        throw error;
    }
};


export const listAlgorithmFiles = async (filePrefix) => {
    try {
        console.log("🔍 请求算法文件列表，前缀:", filePrefix);

        const res = await api.get("/algorithms/list-algorithm-files/", {
            params: { prefix: filePrefix }  // ✅ 确保参数名与后端匹配
        });

        console.log("✅ API 返回的算法文件:", res.data);
        return res.data;
    } catch (error) {
        console.error("❌ 获取算法文件列表失败:", error);
        return { files: [] };  // 避免 `undefined`
    }
};

export const getAlgorithmById = async (algorithm_id) => {
    return await api.get(`/algorithms/${algorithm_id}`);
};