<template>
  <div>
    <el-card>
      <h2>算法管理</h2>
      <div style="display: flex; gap: 10px; margin-bottom: 10px;">
        <el-input v-model="searchName" placeholder="输入算法名称" clearable />
        <el-button type="primary">搜索</el-button>
        <el-button type="success" @click="editAlgorithm">创建</el-button>
      </div>

      <el-table v-if="algorithms.length" :data="algorithms" border style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="算法名称" />
        <el-table-column prop="file_path" label="存储路径" />
        <el-table-column label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" @click="editAlgorithm(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <p v-else>暂无算法数据</p>

      <el-pagination
          v-if="totalAlgorithms > 0"
          background
          layout="prev, pager, next"
          :total="totalAlgorithms"
          :current-page="algorithmPage"
          :page-size="algorithmPageSize"
          @current-change="handleAlgorithmPageChange"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import dayjs from "dayjs";
import { getAlgorithms } from "@/api/algorithm";
import { useRouter } from "vue-router";

const algorithms = ref([]);
const searchName = ref("");
const router = useRouter();

// 分页参数
const algorithmPage = ref(1);
const algorithmPageSize = ref(10);
const totalAlgorithms = ref(0);

const fetchAlgorithms = async () => {
  try {
    const response = await getAlgorithms(algorithmPage.value, algorithmPageSize.value);
    console.log("获取的算法数据:", response.data);
    algorithms.value = response.data.items || [];
    totalAlgorithms.value = response.data.total || 0;
  } catch (error) {
    console.error("获取算法失败:", error);
    algorithms.value = [];
  }
};

const handleAlgorithmPageChange = (page) => {
  algorithmPage.value = page;
  fetchAlgorithms();
};

const formatDate = (date) => {
  return date ? dayjs(date).format("YYYY-MM-DD HH:mm:ss") : "无日期";
};

// **编辑算法**
const editAlgorithm = (algorithm) => {
  router.push({
    name: "EditAlgorithmView", // 确保路由配置中有这个 name
    query: {
      id: algorithm.id,
      name: algorithm.name,
      file_path: algorithm.file_path
    }
  });
};

onMounted(fetchAlgorithms);
</script>