<template>
  <div class="tabs-container">
    <!-- 左侧 Logo + 系统名称 + 导航栏 -->
    <div class="left-section">
      <img src="../assets/logo.png" alt="logo" class="logo" />
      <span class="system-name">无人机检测分类系统</span>

      <!-- 导航栏 -->
      <div class="tabs">
        <router-link to="/home" class="tab" :class="{ active: $route.path === '/home' }">主页</router-link>
        <router-link to="/create" class="tab" :class="{ active: $route.path === '/create' }">新建算法</router-link>
        <router-link to="/dataset" class="tab" :class="{ active: $route.path === '/dataset' }">数据集管理</router-link>
        <router-link to="/algorithm" class="tab" :class="{ active: $route.path === '/algorithm' }">算法管理</router-link>
        <router-link to="/history" class="tab" :class="{ active: $route.path === '/history' }">历史记录</router-link>
      </div>
    </div>

    <!-- 右侧登录图标 -->
    <div class="login-icon">
      <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          width="24px"
          height="24px"
      >
        <path
            d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
        />
      </svg>
    </div>
  </div>
</template>

<style scoped>
/* 外层容器，使左侧（Logo + 名称 + Tabs）靠左，登录图标靠右 */
.tabs-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #ddd;
  padding: 10px 20px;
}

/* 左侧 Logo + 系统名称 + 导航栏 */
.left-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* Logo 图片样式 */
.logo {
  width: 40px;
  height: 40px;
}

/* 系统名称样式 */
.system-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

/* 导航栏 Tabs */
.tabs {
  display: flex;
  gap: 20px;
  margin-left: 30px;
}

.tab {
  text-decoration: none;
  color: black;
  font-size: 16px;
  padding: 10px 0;
  position: relative;
}

.tab:hover {
  color: #007bff;
}

.active {
  color: #007bff;
}

.active::after {
  content: "";
  display: block;
  width: 100%;
  height: 2px;
  background-color: #007bff;
  position: absolute;
  bottom: -2px;
  left: 0;
}

/* 右侧登录图标 */
.login-icon {
  width: 40px;
  height: 40px;
  background-color: #007bff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.3s, box-shadow 0.3s;
}

.login-icon:hover {
  background-color: #0056b3;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}

.login-icon svg {
  color: #fff;
  transition: color 0.3s;
}
</style>
<script setup lang="ts">
</script>