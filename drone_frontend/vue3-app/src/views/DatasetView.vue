<template>
  <div>
    <el-card>
      <h2>数据集管理</h2>
      <div style="display: flex; gap: 10px; margin-bottom: 10px;">
        <el-input v-model="searchName" placeholder="输入数据集名称" clearable />
        <el-button type="primary" @click="fetchDatasets">搜索</el-button>
      </div>

      <el-table v-if="datasets.length" :data="datasets" border style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="数据集名称" />
        <el-table-column label="描述">
          <template #default="{ row }">
            <el-input
                v-model="row.description"
                @blur="updateDescription(row)"
                @keyup.enter="updateDescription(row)"
                placeholder="点击编辑描述"
            />
          </template>
        </el-table-column>
        <el-table-column label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
<!--        <el-table-column label="操作" width="160">-->
<!--          <template #default="{ row }">-->
<!--            <el-button type="danger" @click="deleteDataset(row.id)">删除</el-button>-->
<!--          </template>-->
<!--        </el-table-column>-->
      </el-table>
      <p v-else>暂无数据</p>

      <!-- ✅ 添加分页 -->
      <el-pagination
          v-if="totalDatasets > 0"
          background
          layout="prev, pager, next"
          :total="totalDatasets"
          :current-page="datasetPage"
          :page-size="datasetPageSize"
          @current-change="handleDatasetPageChange"
      />
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import dayjs from "dayjs";
import { getDatasets, deleteDataset, updateDatasetDescription } from "@/api/dataset";

export default {
  setup() {
    const datasets = ref([]);
    const searchName = ref("");

    // 分页参数
    const datasetPage = ref(1);
    const datasetPageSize = ref(10);
    const totalDatasets = ref(0);

    const fetchDatasets = async () => {
      try {
        const response = await getDatasets(datasetPage.value, datasetPageSize.value);
        console.log("获取的数据集:", response.data);  // 🐞 调试
        datasets.value = response.data.items || [];
        totalDatasets.value = response.data.total || 0;
      } catch (error) {
        console.error("获取数据集失败:", error);
        datasets.value = [];
      }
    };

    const deleteDataset = async (id) => {
      try {
        await deleteDataset(id);
        fetchDatasets();
      } catch (error) {
        console.error("删除数据集失败:", error);
      }
    };

    // 更新描述
    const updateDescription = async (row) => {
      try {
        await updateDatasetDescription(row.id, row.description);
        console.log(`描述已更新: ${row.description}`);
      } catch (error) {
        console.error("更新描述失败:", error);
      }
    };

    // 处理数据集分页
    const handleDatasetPageChange = (page) => {
      datasetPage.value = page;
      fetchDatasets();
    };

    // ✅ 格式化日期
    const formatDate = (date) => {
      return date ? dayjs(date).format("YYYY-MM-DD HH:mm:ss") : "无日期";
    };

    onMounted(fetchDatasets);

    return {
      datasets,
      searchName,
      datasetPage,
      datasetPageSize,
      totalDatasets,
      fetchDatasets,
      deleteDataset,
      handleDatasetPageChange,
      updateDescription,
      formatDate,
    };
  },
};
</script>
