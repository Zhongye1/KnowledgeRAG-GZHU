<template>
  <t-config-provider :global-config="{ classPrefix: 't' }">
    <div class="app-container">
      <!-- 应用导航栏 -->
      <thea v-if="showHeader"></thea>
      <!-- <app-navbar class="navbar"/> -->
      <!-- 路由视图 -->
      <router-view class="router-view" />
    </div>
  </t-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
//import AppNavbar from './components/AppNavbar.vue';
import thea from './components/T-HeadBar.vue'
//import '@/assets/fadeIn.css';
import "@/assets/scroll.css"

const route = useRoute();

// 定义不需要显示头部的路由路径
const hideHeaderRoutes = ['/LogonOrRegister'];

// 根据当前路由决定是否显示头部
const showHeader = computed(() => {
  return !hideHeaderRoutes.includes(route.path);
});
</script>

<style>
.app-container {
  background-color: #f9fafb;
  height: 100vh;
  width: 100vw;
  position: fixed;
  z-index: -1;
  overflow: hidden;
}

.navbar {
  height: 8vh;
  /* 设置导航栏高度 */
}

.router-view {
  height: 92vh;
  /* 设置路由视图高度 */
}
</style>
