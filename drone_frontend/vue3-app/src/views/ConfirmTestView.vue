<template>
  <div class="confirm-container">
    <div class="selection-row">
      <h2>应用模式</h2>

      <!-- 算法名称 -->
      <div class="selection-item">
        <input v-if="algorithmName" type="text" v-model="algorithmName" class="input-box" disabled />
        <select v-else v-model="selectedAlgorithm" class="input-box">
          <option v-for="algorithm in algorithmOptions" :key="algorithm.id" :value="algorithm">
            {{ algorithm }}
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
      <!-- 资源监控 -->
      <div class="left-column">
        <div class="progress-item">
          <p>CPU 使用率</p>
          <el-progress type="circle" :percentage="cpuUsage" status="success"></el-progress>
          <div class="number-flip">{{ cpuUsage }}%</div>
        </div>
        <div class="progress-item">
          <p>GPU 使用率</p>
          <el-progress type="circle" :percentage="gpuUsage" status="success"></el-progress>
          <div class="number-flip">{{ gpuUsage }}%</div>
        </div>
        <div class="progress-item">
          <p>内存使用率</p>
          <el-progress type="circle" :percentage="memoryUsage" status="success"></el-progress>
          <div class="number-flip">{{ memoryUsage }}%</div>
        </div>
      </div>

      <!-- 推理记录表格（滚动加载） -->
      <div class="right-column">
        <el-table
            :data="visibleRecords"
            border
            style="width: 100%; height: 710px; overflow-y: auto"
            ref="tableRef"
            @scroll.native="loadMore"
        >
          <el-table-column prop="startTime" label="开始时间" width="180"></el-table-column>
          <el-table-column prop="endTime" label="结束时间" width="180"></el-table-column>
          <el-table-column prop="category" label="分类结果" width="150"></el-table-column>
          <el-table-column label="是否正确" width="150">
            <template #default="{ row }">
              <el-select v-model="row.correctness" placeholder="选择">
                <el-option label="正确" value="正确"></el-option>
                <el-option label="错误" value="错误"></el-option>
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="附加描述">
            <template #default="{ row }">
              <el-input v-model="row.comment" placeholder="输入描述"></el-input>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getAlgorithms } from "@/api/algorithm";

const route = useRoute();
const router = useRouter();

// 训练 & 选择逻辑
const algorithmName = ref(route.query.algorithm_name || "");
const algorithmOptions = ref([]);
const selectedAlgorithm = ref("");
const isReady = computed(() => algorithmName.value || selectedAlgorithm.value);

// 资源监控
const cpuUsage = ref(5);
const gpuUsage = ref(20);
const memoryUsage = ref(10);

// 推理记录列表（模拟 100 条数据）
const allRecords = ref([]);
const visibleRecords = ref([]);
const pageSize = 20;
const loadedCount = ref(0);

// 模拟生成 100 条数据
const generateRecords = () => {
  allRecords.value = [];
  const now = new Date(); // 当前时间
  const oneMonthAgo = new Date();
  oneMonthAgo.setDate(now.getDate() - 30); // 30天前的日期

  for (let i = 0; i < 15; i++) {
    // 生成最近一个月内的随机日期
    const startTimestamp = new Date(
      oneMonthAgo.getTime() + Math.random() * (now.getTime() - oneMonthAgo.getTime())
    );

    // 生成 100ms - 500ms 的随机间隔
    const duration = Math.floor(Math.random() * 400) + 100;
    const endTimestamp = new Date(startTimestamp.getTime() + duration);

    // 格式化时间函数
    const format = (date) => {
      const Y = date.getFullYear();
      const M = String(date.getMonth() + 1).padStart(2, "0");
      const D = String(date.getDate()).padStart(2, "0");
      const h = String(date.getHours()).padStart(2, "0");
      const m = String(date.getMinutes()).padStart(2, "0");
      const s = String(date.getSeconds()).padStart(2, "0");
      const ms = String(date.getMilliseconds()).padStart(3, "0");
      return `${Y}-${M}-${D} ${h}:${m}:${s}.${ms}`;
    };

    allRecords.value.push({
      startTime: format(startTimestamp),
      endTime: format(endTimestamp),
      category: String(Math.floor(Math.random() * 21) + 1), // 生成 1-21 之间的随机类别
      correctness: "",
      comment: "",
    });
  }

  // 按时间降序排序（最近的时间最靠前）
  allRecords.value.sort((a, b) => new Date(b.startTime) - new Date(a.startTime));
};

// 监听滚动加载
const loadMore = (event) => {
  const tableBody = event.target;
  if (tableBody.scrollTop + tableBody.clientHeight >= tableBody.scrollHeight - 10) {
    // 判断是否滚动到底部
    if (loadedCount.value < allRecords.value.length) {
      const nextBatch = allRecords.value.slice(loadedCount.value, loadedCount.value + pageSize);
      visibleRecords.value = [...visibleRecords.value, ...nextBatch];
      loadedCount.value += pageSize;
    }
  }
};

// 获取算法选项
onMounted(async () => {
  try {
    const algorithmRes = await getAlgorithms();
    algorithmOptions.value = algorithmRes.data.items || [];
  } catch (error) {
    console.error("❌ 获取数据失败:", error);
  }

  // 初始化数据
  generateRecords();
  visibleRecords.value = allRecords.value.slice(0, pageSize);
  loadedCount.value = pageSize;
});

// 提交选择
const submitSelection = () => {
  if (!algorithmName.value && !selectedAlgorithm.value) {
    alert("请选择算法！");
    return;
  }

  const finalAlgorithm = algorithmName.value || selectedAlgorithm.value;
  console.log("✅ 选择的算法：", finalAlgorithm);
  alert(`已选择算法：${finalAlgorithm}`);
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
  justify-content: space-between;
  gap: 10px;
  margin-top: 20px;
}

/* 资源监控（左侧） */
.left-column {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;
  width: 20%;
  align-items: center;
  height: 100%;
}

/* 右侧 推理记录表格 */
.right-column {
  width: 75%;
  padding-right: 20px;
}

/* 表格滚动 */
.el-table {
  height: 500px;
  overflow-y: auto;
}

/* 环形进度条 */
.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

/* 百分比数字 */
.number-flip {
  font-size: 22px;
  font-weight: bold;
  margin-top: 5px;
}

/* 选择框 */
.el-select {
  width: 100px;
}

/* 评价输入框 */
.el-input {
  width: 100%;
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
  color: black;
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
