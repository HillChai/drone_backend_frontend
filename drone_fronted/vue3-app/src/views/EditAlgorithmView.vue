<template>
  <div class="editor-container">
    <!-- 左侧设置栏 -->
    <div class="sidebar">
      <h2>修改算法</h2>

      <!-- 选择算法文件 -->
      <label class="input-label">选择算法文件：</label>
      <select v-if="algorithmFiles.length > 0" v-model="selectedFile" @change="loadCode" class="select-box">
        <option disabled value="">请选择算法文件</option>
        <option v-for="file in algorithmFiles" :key="file" :value="file">
          {{ file.split('/').pop() }}
        </option>
      </select>

      <!-- 编辑代码文件名称 -->
      <label class="input-label">代码文件名称：</label>
      <input type="text" v-model="fileName" class="input-box" />

      <!-- MinIO 存储路径 -->
      <label class="input-label">MinIO 存储路径：</label>
      <input type="text" v-model="minioPath" class="input-box" />

      <!-- 按钮区域 -->
      <div class="button-group">
        <button @click="saveCode" class="btn submit" :disabled="!selectedFile">保存代码</button>
        <button @click="goBack" class="btn">返回</button>
      </div>
    </div>

    <!-- 右侧代码编辑器 -->
    <div class="code-editor">
      <div ref="editorContainer" class="editor"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import * as monaco from "monaco-editor";
import {listAlgorithmFiles, getAlgorithmContent, saveAlgorithm} from "@/api/algorithm";

const route = useRoute();
const router = useRouter();
const algorithmId = ref(route.query.id || "");
const filePath = ref(route.query.file_path || "");
const directoryPath = ref(filePath.value.replace(/\/[^/]+$/, ""));
const algorithmFiles = ref([]);
const selectedFile = ref("");
const fileName = ref("");  // 代码文件名称
const minioPath = ref(""); // MinIO 存储路径
const editorContainer = ref(null);
let editorInstance = null;

onMounted(async () => {
  editorInstance = monaco.editor.create(editorContainer.value, {
    value: "# 请选择一个算法文件",
    language: "python",
    theme: "vs-dark",
    automaticLayout: true,
  });

  if (!algorithmId.value) {
    console.error("❌ 缺少 algorithmId 参数");
    return;
  }

  try {
    const res = await listAlgorithmFiles(directoryPath.value);
    algorithmFiles.value = res.files || [];

    if (algorithmFiles.value.length > 0) {
      selectedFile.value = algorithmFiles.value[0];
      await loadCode();
    }
  } catch (error) {
    console.error("❌ 获取文件列表失败:", error);
  }
});

// 加载代码
const loadCode = async () => {
  if (!selectedFile.value) return;
  try {
    const res = await getAlgorithmContent(selectedFile.value);
    if (res && res.code) {
      editorInstance.setValue(res.code);
      fileName.value = selectedFile.value.split('/').pop() || ""; // 设定文件名称
      minioPath.value = selectedFile.value; // 设定 MinIO 存储路径
    }
  } catch (error) {
    console.error("❌ 代码加载失败:", error);
  }
};

// 监听 selectedFile 变化
watch(selectedFile, async (newFile) => {
  if (!newFile) return;
  await loadCode();
});

const saveCode = async () => {
  if (!fileName.value) {
    alert("请输入代码文件名称！");
    return;
  }

  const codeContent = editorInstance.getValue();  // 获取 Monaco 编辑器内容
  const blob = new Blob([codeContent], { type: "text/plain" });
  const file = new File([blob], fileName.value, { type: "text/plain" });

  try {
    console.log("📡 正在上传代码...");
    const res = await saveAlgorithm(fileName.value, file);

    if (res && res.file_url) {
      console.log("✅ 代码上传成功:", res);
      minioPath.value = res.file_url;  // ✅ 更新文件路径
      selectedFile.value = res.file_url;
      alert("代码已成功保存！");
    } else {
      throw new Error("后端未返回文件 URL");
    }
  } catch (error) {
    console.error("❌ 代码保存失败:", error);
    alert("代码保存失败，请重试！");
  }
};

const goBack = () => {
  router.go(-1);
};
</script>

<style scoped>
/* 页面布局 */
.editor-container {
  display: flex;
  gap: 50px;
  padding: 20px;
}

/* 左侧设置栏 */
.sidebar {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 右侧代码编辑器 */
.code-editor {
  flex: 1; /* 让代码编辑器占据剩余空间 */
  //min-width: 1000px; /* 设置一个最小宽度 */
  max-width: 1100px; /* 可选，防止编辑器过宽 */
  display: flex;
  justify-content: center;
}

/* 代码编辑器样式 */
.editor {
  width: 100%; /* 确保 Monaco Editor 占满 .code-editor */
  height: 600px;
  border-radius: 8px;
  border: 2px solid #ddd;
  overflow: hidden;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
}


/* 输入框样式 */
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

/* 下拉框样式 */
.select-box {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 5px;
  cursor: pointer;
}

/* 按钮样式 */
.button-group {
  display: flex;
  gap: 10px;
}

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
