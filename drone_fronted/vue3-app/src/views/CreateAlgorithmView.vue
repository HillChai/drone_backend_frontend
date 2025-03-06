<template>
  <h2>新增算法</h2>
  <div class="container">
    <!-- 代码编辑器 -->
    <div ref="editorContainer" class="editor"></div>

    <!-- 按钮区域 -->
    <div class="button-group">
      <button @click="uploadCode" class="btn"> 上传代码</button>
      <button @click="saveAlgorithm" :disabled="!fileUrl" class="btn submit"> 提交算法</button>
    </div>

    <p v-if="fileUrl" class="file-link">
      文件已上传: <a :href="fileUrl" target="_blank">查看代码</a>
    </p>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import * as monaco from "monaco-editor";
import { uploadAlgorithm, saveAlgorithm } from "@/api/algorithm";

export default {
  setup() {
    const algorithmName = ref("");
    const fileUrl = ref("");
    const editorContainer = ref(null);
    let editorInstance = null;

    onMounted(() => {
      editorInstance = monaco.editor.create(editorContainer.value, {
        value: "# 在这里输入Python代码...",
        language: "python",
        theme: "vs-dark",
        automaticLayout: true,
      });
    });

    const uploadCode = async () => {
      const code = editorInstance.getValue();
      const formData = new FormData();
      const blob = new Blob([code], {type: "text/plain"});
      formData.append("file", new File([blob], "algorithm.py"));

      const res = await uploadAlgorithm(formData);
      fileUrl.value = res.file_url;
    };

    const saveAlgorithmData = async () => {
      await saveAlgorithm({name: algorithmName.value, file_url: fileUrl.value});
      alert("算法已保存！");
    };

    return {algorithmName, fileUrl, editorContainer, uploadCode, saveAlgorithm: saveAlgorithmData};
  }
};
</script>

<style scoped>
/* 让整个容器居中 */
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 800px;
  margin: 0 auto;
}

/* 代码编辑器样式 */
.editor {
  width: 100%;
  height: 500px;
  border-radius: 20px;
  border: 2px solid #ddd;
  overflow: hidden;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
}

/* 按钮组 */
.button-group {
  display: flex;
  justify-content: center;
  gap: 50px; /* 按钮间距 */
  margin-top: 20px;
}

/* 按钮基础样式 */
.btn {
  background-color: #007bff;
  color: white;
  font-size: 16px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 提交按钮特效 */
.submit {
  background-color: #28a745;
}

/* 按钮悬停效果 */
.btn:hover {
  opacity: 0.8;
}

/* 禁用按钮样式 */
.btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 文件链接样式 */
.file-link {
  margin-top: 15px;
  font-size: 14px;
}

.file-link a {
  color: #007bff;
  text-decoration: none;
}

.file-link a:hover {
  text-decoration: underline;
}
</style>
