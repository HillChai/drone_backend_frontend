<template>
  <div>
    <el-card>
      <h2>历史记录</h2>
      <div style="display: flex; gap: 10px; margin-bottom: 10px;">
        <el-input v-model="searchName" placeholder="输入描述" clearable />
        <el-button type="primary">搜索</el-button>
      </div>

      <el-table v-if="histories.length" :data="histories" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80"/>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="mode" label="模式" width="180"/>

        <!-- 算法名称 -->
        <el-table-column prop="algorithm_name" label="算法名称" width="240"/>

        <!-- 训练模式时显示数据集 -->
        <el-table-column prop="dataset_name" label="数据集名称" width="240"/>

        <el-table-column prop="results_path" label="结果存储路径" show-overflow-tooltip />

        <!-- 创建时间 -->
        <el-table-column label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <!-- 完成时间 -->
        <el-table-column label="完成时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.completed_at) }}
          </template>
        </el-table-column>

      </el-table>
      <p v-else>暂无历史数据</p>

      <!-- 分页组件 -->
      <el-pagination
        v-if="totalHistories > 0"
        background
        layout="prev, pager, next"
        :total="totalHistories"
        :current-page="historyPage"
        :page-size="historyPageSize"
        @current-change="handleHistoryPageChange"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import dayjs from "dayjs";
import { getHistory } from "@/api/history";
import { getAlgorithmById } from "@/api/algorithm";
import { getDatasetById } from "@/api/dataset";

const histories = ref([]);
const algorithms = ref([]);
const datasets = ref([]);
const searchName = ref("");
const historyPage = ref(1);
const historyPageSize = ref(10);
const totalHistories = ref(0);

const fetchHistories = async () => {
  try {
    const response = await getHistory(Number(historyPage.value), Number(historyPageSize.value));
    console.log("获取历史数据:", response.data)
    // 处理模式字段
    const historyItems = await Promise.all(
      response.data.items.map(async (history) => {
        let algorithmName = "未知算法";
        let datasetName = "未知数据";

        // 获取算法名称
        if (history.algorithm_id) {
          try {
            const algResponse = await getAlgorithmById(history.algorithm_id);
            console.log(`算法ID ${history.algorithm_id} 的 API 返回:`, algResponse.data);
            algorithmName = algResponse.data.name;
          } catch (error) {
            console.warn(`无法获取算法ID ${history.algorithm_id}:`, error);
          }
        }

        // 获取数据集名称
        if (history.dataset_id) {
          try {
            const datasetResponse = await getDatasetById(history.dataset_id);
            console.log(`数据集ID ${history.dataset_id} 的 API 返回:`, datasetResponse.data);
            datasetName = datasetResponse.data.name;
          } catch (error) {
            console.warn(`无法获取数据集ID ${history.dataset_id}:`, error);
          }
        }

        return {
          ...history,
          mode: history.dataset_id ? "训练" : "应用",
          algorithm_name: algorithmName,
          dataset_name: datasetName,
        };
      })
    );
    
    histories.value = historyItems;
    totalHistories.value = response.data.total;
  } catch (error) {
    console.error("获取历史记录失败:", error);
  }
};


// **格式化日期**
const formatDate = (date) => {
  return date ? dayjs(date).format("YYYY-MM-DD HH:mm:ss") : "无日期";
};

// **状态颜色**
const getStatusTag = (status) => {
  return status === "completed" ? "success"
       : status === "failed" ? "danger"
       : "warning";
};

const handleHistoryPageChange = (page) => {
  historyPage.value = Number(page); // 确保是整数
  fetchHistories(); // 触发更新
};

watch(historyPage, () => {
  fetchHistories();
});
onMounted(fetchHistories);
</script>