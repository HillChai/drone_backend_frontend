import api from "./index";

// 获取历史记录
export const getHistory = () => api.get("/history");

// 更新历史状态
export const updateHistoryStatus = (id, status) => api.put(`/history/${id}/status`, null, { params: { new_status: status } });

// 更新推理/训练结果路径
export const updateHistoryResults = (id, resultsPath) => api.put(`/history/${id}/results`, null, { params: { results_path: resultsPath } });

// 删除历史记录
export const deleteHistory = (id) => api.delete(`/history/${id}`);
