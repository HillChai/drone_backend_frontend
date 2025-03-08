<template>
  <div class="app-container">
    <Tabs />
    <router-view></router-view>
  </div>
</template>

<script setup>
import Tabs from './components/Tabs.vue';
</script>


<style>
.app-container {
  background-color: #1e1e2f;
  min-height: 100vh;
  color: #ffffff;
}
</style>
