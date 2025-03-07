import api from "./index";

export const getDatasets = async (page = 1, limit = 10) => {
    return await api.get(`/datasets?page=${page}&limit=${limit}`);
};

export const deleteDataset = async (id) => {
    return await api.delete(`/datasets/${id}`);
};

// ✅ 新增：更新数据集描述
export const updateDatasetDescription = async (id, description) => {
    return await api.put(`/datasets/${id}/description`, { description });
};
