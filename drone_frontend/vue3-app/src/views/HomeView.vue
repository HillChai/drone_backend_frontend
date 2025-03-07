<template>
  <div>
    <!-- 数据集管理 -->
    <el-card>
      <div style="display: flex; gap: 10px; margin-bottom: 10px;">
        <el-input v-model="searchDataset" placeholder="输入数据集名称" clearable />
        <el-button type="primary" @click="fetchDatasets">搜索</el-button>
      </div>

      <el-table v-if="datasets.length" :data="datasets" border>
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="数据集名称" />
        <el-table-column label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="success" @click="trainDataset(row.name)">训练</el-button>
          </template>
        </el-table-column>
      </el-table>
      <p v-else>暂无数据</p>

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

    <!-- 算法管理 -->
    <el-card>
      <div style="display: flex; gap: 10px; margin-bottom: 10px;">
        <el-input v-model="searchAlgorithm" placeholder="输入算法名称" clearable />
        <el-button type="primary" @click="fetchAlgorithms">搜索</el-button>
      </div>

      <el-table v-if="algorithms.length" :data="algorithms" border>
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="算法名称" />
        <el-table-column label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="success" @click="applyAlgorithm(row.name)">应用</el-button>
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

<script>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getDatasets } from "@/api/dataset";
import { getAlgorithms } from "@/api/algorithm";
import dayjs from "dayjs";

export default {
  setup() {
    const router = useRouter();

    const datasets = ref([]);
    const algorithms = ref([]);
    const searchDataset = ref("");
    const searchAlgorithm = ref("");

    // 分页参数
    const datasetPage = ref(1);
    const datasetPageSize = ref(5);
    const totalDatasets = ref(0);

    const algorithmPage = ref(1);
    const algorithmPageSize = ref(5);
    const totalAlgorithms = ref(0);

    // 获取数据集列表（分页）
    const fetchDatasets = async () => {
      try {
        const response = await getDatasets(datasetPage.value, datasetPageSize.value);
        datasets.value = response.data.items || [];
        totalDatasets.value = response.data.total || 0;
      } catch (error) {
        datasets.value = [];
      }
    };

    // 获取算法列表（分页）
    const fetchAlgorithms = async () => {
      try {
        const response = await getAlgorithms(algorithmPage.value, algorithmPageSize.value);
        algorithms.value = response.data.items || [];
        totalAlgorithms.value = response.data.total || 0;
      } catch (error) {
        algorithms.value = [];
      }
    };

    // 训练数据集（跳转到选择页面）
    const trainDataset = (datasetName) => {
      router.push({ path: "/confirm", query: { dataset_name: datasetName } });
    };

    // 应用算法（跳转到选择页面）
    const applyAlgorithm = (algorithmName) => {
      router.push({ path: "/confirm", query: { algorithm_name: algorithmName } });
    };

    // 处理分页
    const handleDatasetPageChange = (page) => {
      datasetPage.value = page;
      fetchDatasets();
    };
    const handleAlgorithmPageChange = (page) => {
      algorithmPage.value = page;
      fetchAlgorithms();
    };

    // 格式化日期
    const formatDate = (date) => {
      return date ? dayjs(date).format("YYYY-MM-DD HH:mm:ss") : "无日期";
    };

    onMounted(() => {
      fetchDatasets();
      fetchAlgorithms();
    });

    return {
      datasets,
      algorithms,
      searchDataset,
      searchAlgorithm,
      datasetPage,
      datasetPageSize,
      totalDatasets,
      fetchDatasets,
      algorithmPage,
      algorithmPageSize,
      totalAlgorithms,
      fetchAlgorithms,
      trainDataset,
      applyAlgorithm,
      handleDatasetPageChange,
      handleAlgorithmPageChange,
      formatDate,
    };
  },
};
</script>
