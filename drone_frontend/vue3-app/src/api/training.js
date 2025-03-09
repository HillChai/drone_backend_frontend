// src/api/training.js
import api from "./index";

// 统一 baseURL（来源 axios 封装）
const baseURL = api.defaults.baseURL;

/**
 * 启动容器（准备训练）
 */
export async function startContainer() {
  try {
    const res = await api.post("/start_training");
    return res.data;
  } catch (error) {
    console.error("❌ startContainer 容器启动失败:", error);
    throw error;
  }
}

/**
 * 启动训练脚本（读取 loss/accuracy 流）
 * @param {Function} onDataCallback - 每次日志片段的回调
 */
export async function startTrainingStream(onDataCallback) {
  try {
    const res = await fetch(`${baseURL}/run_training_script`, {
      method: "POST"
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      onDataCallback(text);
    }
  } catch (error) {
    console.error("❌ startTrainingStream 失败:", error);
  }
}

/**
 * 停止并删除容器
 */
export async function stopTraining() {
  try {
    const res = await api.post("/stop_training");
    return res.data;
  } catch (error) {
    console.error("❌ stopTraining 失败:", error);
    throw error;
  }
}
