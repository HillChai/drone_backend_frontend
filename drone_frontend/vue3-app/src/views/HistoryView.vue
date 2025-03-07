<template>
  <div>
    <h1>历史记录</h1>
    <el-table v-if="histories.length" :data="histories" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="results_path" label="推理结果路径" />

      <el-table-column label="操作">
        <template #default="{ row }">
          <el-select v-model="row.status" @change="updateStatus(row)">
            <el-option label="pending" value="pending" />
            <el-option label="completed" value="completed" />
          </el-select>
          <el-input v-model="row.results_path" placeholder="输入推理结果路径" @blur="updateResults(row)" />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getHistory, updateHistoryStatus, updateHistoryResults } from "@/api/history";

const histories = ref([]);

const fetchHistories = async () => {
  try {
    const response = await getHistory();
    histories.value = response.data;
  } catch (error) {
    console.error("获取历史记录失败:", error);
  }
};

const updateStatus = async (row) => {
  try {
    await updateHistoryStatus(row.id, row.status);
    console.log(`状态更新成功: ${row.status}`);
  } catch (error) {
    console.error("状态更新失败:", error);
  }
};

const updateResults = async (row) => {
  try {
    await updateHistoryResults(row.id, row.results_path);
    console.log(`推理结果路径更新成功: ${row.results_path}`);
  } catch (error) {
    console.error("推理结果路径更新失败:", error);
  }
};

onMounted(fetchHistories);
</script>
