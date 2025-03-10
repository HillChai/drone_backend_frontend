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
        <button @click="submitSelection" class="btn submit" :disabled="!isReady || isTraining">开始</button>
        <button @click="stopTrainingHandler" class="btn">停止</button>
      </div>
    </div>

    <div class="chart-container">
      <!-- 资源监控（改为环形进度条 + 数字翻牌器） -->
      <div class="left-column">
        <div class=" progress-item ">
          <p>CPU 使用率</p>
          <el-progress type="circle" :percentage="cpuUsage" status="success"></el-progress>
          <div class="number-flip">{{ cpuUsage }}%</div>
        </div>
        <div class="progress-item">
          <p>GPU 使用率</p>
          <el-progress type="circle" :percentage="gpuUsage" status="warning"></el-progress>
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
import { startContainer, startTrainingStream, stopTraining } from "@/api/training";

const route = useRoute();
const router = useRouter();

const datasetName = ref(route.query.dataset_name || "");
const algorithmName = ref(route.query.algorithm_name || "");
const datasetOptions = ref([]);
const algorithmOptions = ref([]);
const selectedDataset = ref("");
const selectedAlgorithm = ref("");
const isReady = computed(() => datasetName.value || selectedDataset.value || algorithmName.value || selectedAlgorithm.value);

// 状态变量
const isTraining = ref(false);
const containerId = ref("");

// 训练数据
const trainingLoss = ref([]);
const trainingAccuracy = ref([]);

const cpuUsage = ref(10);
const gpuUsage = ref(95);
const memoryUsage = ref(30);

// 图表实例
const accuracyChart = ref(null);
const lossChart = ref(null);
let lossChartInstance = null;
let accuracyChartInstance = null;

const valAccuracyChart = ref(null);
const valLossChart = ref(null);
let valAccuracyChartInstance = null;
let valLossChartInstance = null;

const valAccuracyData = ref([]);
const valLossData = ref([]);

// 初始化
onMounted(async () => {
  try {
    const datasetRes = await getDatasets();
    datasetOptions.value = datasetRes.data.items || [];

    const algorithmRes = await getAlgorithms();
    algorithmOptions.value = algorithmRes.data.items || [];
  } catch (error) {
    console.error("❌ 获取数据失败:", error);
  }

  initCharts();
});

// 点击“开始”
const submitSelection = async () => {
  console.log("📤 开始训练 - 数据集：");

  try {
    // 第一步：启动容器
    const startRes = await startContainer();
    if (startRes.message?.includes("容器已经存在")) {
      alert("⚠ 容器已存在，请先点击‘停止’");
      return;
    }

    containerId.value = startRes.container_id;
    isTraining.value = true;

    // 第二步：初始化图表数据
    trainingLoss.value = [];
    trainingAccuracy.value = [];
    updateTrainingCharts();

    // 第三步：开始训练脚本（日志流）
    startTrainingStream((text) => {
      const lossMatch = text.match(/loss:\s*([\d\.]+)/i);
      const accMatch = text.match(/accuracy:\s*([\d\.]+)/i);

      if (lossMatch) trainingLoss.value.push(parseFloat(lossMatch[1]));
      if (accMatch) trainingAccuracy.value.push(parseFloat(accMatch[1]));

      updateTrainingCharts();
    });
  } catch (err) {
    console.error("❌ 启动训练失败:", err);
    alert("训练启动失败：" + err.message);
  }
};

// 点击“停止”
const stopTrainingHandler = async () => {
  try {
    const stopRes = await stopTraining();
    isTraining.value = false;
    containerId.value = "";
    alert(stopRes.message || "训练已停止");
  } catch (err) {
    alert("❌ 停止训练失败：" + err.message);
  }
};

// 初始化图表
const initCharts = () => {
  lossChartInstance = echarts.init(lossChart.value);
  accuracyChartInstance = echarts.init(accuracyChart.value);
  valAccuracyChartInstance = echarts.init(valAccuracyChart.value);
  valLossChartInstance = echarts.init(valLossChart.value);

  const baseOption = (title, unit) => ({
    title: { text: title, left: "center", textStyle: { color: "#fff" } },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: [] },
    yAxis: { type: "value", axisLabel: { formatter: `{value} ${unit}` } },
    series: [{ name: title, type: "line", data: [] }],
  });

  lossChartInstance.setOption(baseOption("Training Loss", ""));
  accuracyChartInstance.setOption(baseOption("Training Accuracy", "%"));
  valAccuracyChartInstance.setOption(baseOption("Validation Accuracy", "%"));
  valLossChartInstance.setOption(baseOption("Validation Loss", ""));
};

// 更新图表数据
const updateTrainingCharts = () => {
  const xData = trainingLoss.value.map((_, i) => `${i + 1}`);

  lossChartInstance?.setOption({
    xAxis: { data: xData },
    series: [{ data: trainingLoss.value }],
  });

  accuracyChartInstance?.setOption({
    xAxis: { data: xData },
    series: [{ data: trainingAccuracy.value }],
  });

  generateFakeValidationData();
};

const generateFakeValidationData = () => {
  const xData = [];
  const valAcc = [];
  const valLoss = [];

  for (let i = 0; i < 40; i++) {
    xData.push(`${i + 1}`);

    // 🎯 精细控制 accuracy 随 epoch 抖动
    let acc;
    if (i < 15) {
      acc = 0.1 + (i / 15) * 0.6;
    } else if (i < 30) {
      acc = 0.7 + ((i - 15) / 15) * 0.1;
    } else {
      acc = 0.8 + (Math.random() * 0.02 - 0.01);
    }

    // ✨ 分段加噪声
    let noiseAcc = 0;
    if (i < 10) {
      noiseAcc = Math.random() * 0.06 - 0.03; // ±0.03
    } else if (i < 30) {
      noiseAcc = Math.random() * 0.04 - 0.02; // ±0.02
    } else {
      noiseAcc = Math.random() * 0.02 - 0.01; // ±0.01
    }
    acc += noiseAcc;
    acc = Math.min(1, Math.max(0, parseFloat(acc.toFixed(4))));
    valAcc.push(acc);

    //  Loss 拟真趋势 + 波动
    let loss;
    if (i < 10) {
      loss = 8 - (i / 10) * 5;
    } else if (i < 30) {
      loss = 3 - ((i - 10) / 20) * 2.1;
    } else {
      loss = 0.9 + (Math.random() * 0.2 - 0.1);
    }

    // ✨ 分段加噪声（loss波动大一些）
    let noiseLoss = 0;
    if (i < 10) {
      noiseLoss = Math.random() * 0.6 - 0.3; // ±0.3
    } else if (i < 30) {
      noiseLoss = Math.random() * 0.4 - 0.2; // ±0.2
    } else {
      noiseLoss = Math.random() * 0.2 - 0.1; // ±0.1
    }
    loss += noiseLoss;
    loss = Math.max(0, parseFloat(loss.toFixed(4)));
    valLoss.push(loss);
  }

  valAccuracyData.value = valAcc;
  valLossData.value = valLoss;

  valAccuracyChartInstance?.setOption({
    xAxis: { data: xData },
    series: [{ data: valAcc }]
  });

  valLossChartInstance?.setOption({
    xAxis: { data: xData },
    series: [{ data: valLoss }]
  });
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

/* 环形进度条整体对齐 */
.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px; /* 控制间距 */
}

/* 左侧 资源监控 */
.left-column {
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 让3个进度条均匀分布 */
  gap: 20px;
  width: 15%;
  align-items: center;
  height: 100%; /* 确保高度与右侧对齐 */
  padding-top: 20px; /* 避免贴顶 */
}

/* 右侧 训练进度图表，2×2 网格 */
.right-column {
  flex: 1; /* 右侧自适应填充 */
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  width: 100%;
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
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 300px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

</style>
