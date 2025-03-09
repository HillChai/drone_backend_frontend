<template>
  <div class="confirm-container dark-theme">
    <div class="selection-row">
      <h2>训练模式</h2>

      <!-- 数据集名称 -->
      <div class="selection-item">
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

    <div class="chart-container">
      <!-- 资源监控（改为环形进度条 + 数字翻牌器） -->
      <div class="left-column">
        <div class=" progress-item ">
          <p>CPU 使用率</p>
          <el-progress type="circle" :percentage="cpuUsage" status="exception"></el-progress>
          <div class="number-flip">{{ cpuUsage }}%</div>
        </div>
        <div class="progress-item">
          <p>GPU 使用率</p>
          <el-progress type="circle" :percentage="gpuUsage" status="exception"></el-progress>
          <div class="number-flip">{{ gpuUsage }}%</div>
        </div>
        <div class="progress-item">
          <p>内存使用率</p>
          <el-progress type="circle" :percentage="memoryUsage" status="success"></el-progress>
          <div class="number-flip">{{ memoryUsage }}%</div>
        </div>
      </div>
      <!-- 训练进度图表（仅在 "训练" 模式下显示） -->
      <div class="right-column">
        <div ref="accuracyChart" class="chart"></div>
        <div ref="lossChart" class="chart"></div>
        <div ref="valAccuracyChart" class="chart"></div>
        <div ref="valLossChart" class="chart"></div>
      </div>
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

// 资源监控
const cpuUsage = ref(90);
const gpuUsage = ref(95);
const memoryUsage = ref(30);

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
    title: {
      text: title,
      textStyle: {
        color: '#ffffff', // 设置标题颜色为白色
        fontSize: 16, // 适当调大字体
        fontWeight: 'bold' // 加粗
      },
    },
    textStyle: {
      color: '#ffffff', // 设置标题颜色为白色
      fontSize: 16, // 适当调大字体
      fontWeight: 'bold' // 加粗
    },
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
  color: black; /* 确保输入文本是白色 */
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

.chart-container {
  display: flex;
  justify-content: space-between;
  align-items: center; /* 让左右内容对齐 */
  width: 100%;
  padding-right: 20px; /* 右侧预留空间 */
}

/* 左侧 资源监控 */
.left-column {
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 让3个进度条均匀分布 */
  gap: 20px;
  width: 20%;
  align-items: center;
  height: 100%; /* 确保高度与右侧对齐 */
  padding-top: 20px; /* 避免贴顶 */
}

/* 环形进度条整体对齐 */
.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px; /* 控制间距 */
}

/* 右侧 训练进度图表，2×2 网格 */
.right-column {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  width: 75%;
  padding-right: 20px; /* 让图表不靠边 */
}

/* 百分比数字 */
.number-flip {
  font-size: 22px;
  font-weight: bold;
  margin-top: 5px;
}

/* 右侧图表 */
.chart {
  width: 100%; /* 让图表自适应网格 */
  height: 260px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

</style>
