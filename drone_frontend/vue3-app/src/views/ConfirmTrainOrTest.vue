<template>
  <div class="confirm-container">
    <div class="selection-row">
      <h2 v-if="datasetName">训练模式</h2>
      <h2 v-else-if="algorithmName">应用模式</h2>

      <!-- 数据集名称 -->
      <div v-if="datasetName" class="selection-item">
        <input v-if="datasetName" type="text" v-model="datasetName" class="input-box" disabled />
        <select v-else v-model="selectedDataset" class="input-box">
          <option v-for="dataset in datasetOptions" :key="dataset.id" :value="dataset">
            {{ dataset.name }}
          </option>
        </select>
      </div>

      <!-- 算法名称 -->
      <div class="selection-item">
        <input v-if="algorithmName" type="text" v-model="algorithmName" class="input-box" disabled />
        <select v-else v-model="selectedAlgorithm" class="input-box">
          <option v-for="algorithm in algorithmOptions" :key="algorithm.id" :value="algorithm">
            {{ algorithm.name }}
          </option>
        </select>
      </div>

      <!-- 按钮区域 -->
      <div class="button-group">
        <button @click="submitSelection" class="btn submit" :disabled="!isReady">开始</button>
        <button @click="goBack" class="btn">停止</button>
      </div>
    </div>

    <!-- 资源监控 -->
    <div class="chart-container" v-if="datasetName">
      <div ref="cpuChart" class="chart"></div>
      <div ref="gpuChart" class="chart"></div>
      <div ref="memoryChart" class="chart"></div>
    </div>

    <!-- 训练进度图表（仅在 "训练" 模式下显示） -->
    <div class="chart-container" v-if="datasetName">
      <div ref="accuracyChart" class="chart"></div>
      <div ref="lossChart" class="chart"></div>
      <div ref="valAccuracyChart" class="chart"></div>
      <div ref="valLossChart" class="chart"></div>
    </div>

    <!-- 应用模式下，额外显示 Application Accuracy -->
    <div class="chart-container" v-if="algorithmName">
      <div ref="appAccuracyChart" class="chart"></div>
      <div ref="cpuChart" class="chart"></div>
      <div ref="gpuChart" class="chart"></div>
      <div ref="memoryChart" class="chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import * as echarts from "echarts";
import { useRoute, useRouter } from "vue-router";
import { getDatasets } from "@/api/dataset";
import { getAlgorithms } from "@/api/algorithm";

const route = useRoute();
const router = useRouter();

// 训练 & 选择逻辑
const datasetName = ref(route.query.dataset_name || "");
const algorithmName = ref(route.query.algorithm_name || "");
const datasetOptions = ref([]);
const algorithmOptions = ref([]);
const selectedDataset = ref("");
const selectedAlgorithm = ref("");
const isReady = computed(() => datasetName.value || selectedDataset.value || algorithmName.value || selectedAlgorithm.value);

// ECharts 组件
const accuracyChart = ref(null);
const lossChart = ref(null);
const valAccuracyChart = ref(null);
const valLossChart = ref(null);
const cpuChart = ref(null);
const gpuChart = ref(null);
const memoryChart = ref(null);
const appAccuracyChart = ref(null); // 应用模式下的准确率图表

// 获取数据集 & 算法选项
onMounted(async () => {
  try {
    const datasetRes = await getDatasets();
    datasetOptions.value = datasetRes.data.items || [];

    const algorithmRes = await getAlgorithms();
    algorithmOptions.value = algorithmRes.data.items || [];
  } catch (error) {
    console.error("❌ 获取数据失败:", error);
  }

  // 初始化所有图表
  initCharts();
  simulateTrainingProgress();
});

// 提交选择
const submitSelection = () => {
  if (!datasetName.value && !selectedDataset.value) {
    alert("请选择数据集！");
    return;
  }
  if (!algorithmName.value && !selectedAlgorithm.value) {
    alert("请选择算法！");
    return;
  }

  const finalDataset = datasetName.value || selectedDataset.value;
  const finalAlgorithm = algorithmName.value || selectedAlgorithm.value;

  console.log("✅ 提交选择：", finalDataset, finalAlgorithm);
  alert(`已选择 数据集：${finalDataset.name}，算法：${finalAlgorithm.name}`);
};

// 初始化多个图表
const initCharts = () => {
  if (datasetName.value) {
    createChart(accuracyChart.value, "Training Accuracy", "%", [50, 60, 70, 80, 85]);
    createChart(lossChart.value, "Training Loss", "", [0.8, 0.6, 0.4, 0.2, 0.1]);
    createChart(valAccuracyChart.value, "Validation Accuracy", "%", [48, 58, 68, 78, 83]);
    createChart(valLossChart.value, "Validation Loss", "", [0.85, 0.65, 0.45, 0.25, 0.15]);
  }

  createChart(cpuChart.value, "CPU Usage", "%", [20, 40, 60, 70, 80]);
  createChart(gpuChart.value, "GPU Usage", "%", [10, 30, 50, 60, 75]);
  createChart(memoryChart.value, "Memory Usage", "%", [30, 50, 70, 80, 90]);

  if (algorithmName.value) {
    createChart(appAccuracyChart.value, "Application Accuracy", "%", [85, 87, 89, 90, 92]);
  }
};

// 创建图表
const createChart = (element, title, unit, data) => {
  const chart = echarts.init(element);
  const option = {
    title: { text: title },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: ["T1", "T2", "T3", "T4", "T5"] },
    yAxis: { type: "value", axisLabel: { formatter: `{value} ${unit}` } },
    series: [{ name: title, type: "line", data }]
  };
  chart.setOption(option);
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};
</script>

<style scoped>
/* 页面布局 */
.confirm-container {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
  align-items: center;
}

/* 训练进度与资源监控 */
.chart-container {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.chart {
  width: 45%;
  height: 300px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

/* 使输入框、选择框和按钮在同一行 */
.selection-row {
  display: flex;
  align-items: center;
  gap: 50px;
  width: 100%;
  justify-content: center;
}

/* 选择项样式 */
.selection-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 250px;
}

/* 输入框 & 选择框样式 */
.input-label {
  font-size: 14px;
  font-weight: bold;
}

.input-box {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

/* 按钮区域 */
.button-group {
  display: flex;
  gap: 30px;
}

/* 按钮样式 */
.btn {
  background-color: #007bff;
  color: white;
  font-size: 14px;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit {
  background-color: #28a745;
}

.btn:hover {
  opacity: 0.8;
}

.btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
