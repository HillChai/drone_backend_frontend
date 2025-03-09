import api from "./index";

// 获取分页历史记录
export const getHistory = async (page, limit = 10) => {
    return await api.get("/history", {
        params: { page, limit }  // ✅ Axios 自动处理 URL
    });
};

// 更新历史状态
export const updateHistoryStatus = (id, status) => api.put(`/history/${id}/status`, null, { params: { new_status: status } });

// 更新推理/训练结果路径
export const updateHistoryResults = (id, resultsPath) => api.put(`/history/${id}/results`, null, { params: { results_path: resultsPath } });

// 删除历史记录
export const deleteHistory = (id) => api.delete(`/history/${id}`);
