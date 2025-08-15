<template>
  <main class="max-w-7xl mx-auto px-6 py-8">
    <!-- 欢迎区域 -->
    <div class="flex flex-col md:flex-row justify-between mb-8">
      <div>
        <h1 class="text-2xl font-semibold text-gray-800">Welcome back, mmk</h1>
        <p class="text-gray-600 mt-1">
          Which knowledge bases will you use today?
        </p>
      </div>

      <div class="flex space-x-4 mt-4 md:mt-0">
        <!-- 搜索框 -->
        <search @search="handleSearch" class="h-[40px]" />
        <!-- 创建知识库按钮 -->
        <t-button theme="primary" class="h-[40px]" @click="toggleUploadModal">
          <template #icon><add-icon /></template>
          新建知识库
        </t-button>
      </div>
    </div>

    <!-- 创建知识库弹出界面 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div class="p-6">
          <h3 class="text-xl font-semibold text-gray-800 mb-4">创建知识库</h3>
          <form @submit.prevent="createKnowledgeBase">
            <div class="mb-4">
              <label for="kbName" class="block text-sm font-medium text-gray-700">知识库名称</label>
              <input type="text" id="kbName" v-model="kbName" required
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div class="mt-6 flex justify-end">
              <button type="button" @click="showCreateModal = false"
                class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md font-medium mr-3 hover:bg-gray-50">
                取消
              </button>
              <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium">
                创建
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 知识库卡片网格 - 瀑布流布局 -->
    <div class="knowledge-grid">
      <!-- 知识库卡片 -->
      <knowledge-cards v-for="card in filteredCards" :key="card.id" :card="card" :go-to-detail="goToDetail"
        @click="goToDetail(card.id)" class="knowledge-card" />

      <!-- 结束占位符 -->
      <div class="knowledge-card-placeholder knowledge-card-final">
        <div class="placeholder-content">
          <svg class="w-12 h-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <p class="text-gray-500 text-center">That's all. Nothing more.</p>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { AddIcon } from "tdesign-icons-vue-next";
import knowledgeCards from "@/components/knowledge-unit/knowledge-cards.vue";
import { ref } from "vue";
import search from "@/components/search-unit/search.vue";
import { useCardDataStore } from "../../store";
import { storeToRefs } from "pinia";
import { MessagePlugin } from "tdesign-vue-next";
import axios from "axios";

const router = useRouter();
const cardDataStore = useCardDataStore();
const goToDetail = (id: string) => {
  router.push(`/knowledge/knowledgeDetail/${id}`);
};

const handleSearch = (keyword: string) => {
  console.log("搜索关键词:", keyword);
  // 执行搜索逻辑，比如调用接口、过滤列表等
};

const { filteredCards } = storeToRefs(cardDataStore);

//创建知识库的界面
// 添加模态框显示状态和表单数据
const showCreateModal = ref(false);
const kbName = ref("");
const kbCover = ref("");

//模态框的显示和隐藏
const toggleUploadModal = () => {
  showCreateModal.value = !showCreateModal.value;
};

// 处理表单提交的方法
const createKnowledgeBase = async () => {
  try {
    // 发送 POST 请求到后端接口
    console.log("创建知识库:", kbName.value);
    const formData = new FormData();
    formData.append("kbName", kbName.value);

    await axios.post("/api/create-knowledgebase/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    // 处理成功响应
    console.log("创建知识库:", kbName.value);
    MessagePlugin.success("创建知识库：" + kbName.value + "  成功");

    // 清空表单数据并关闭模态框
    kbName.value = "";
    kbCover.value = "";
    showCreateModal.value = false;

    // 重新获取卡片数据，更新界面
    await cardDataStore.fetchCards();
  } catch (error:any) {
    if (error.response) {
      // 处理后端返回的错误
      if (error.response.status === 400) {
        MessagePlugin.error("知识库已存在");
      } else {
        MessagePlugin.error("创建知识库失败，请稍后重试");
      }
    } else {
      // 处理网络错误
      MessagePlugin.error("网络错误，请检查网络连接");
    }
    console.error("创建知识库失败:", error);
  }
};

import { onMounted } from "vue";

// 组件挂载时获取数据
onMounted(async () => {
  await cardDataStore.fetchCards(); // 组件挂载时获取数据
});
</script>

<style scoped>
/* 主容器样式 */
main {
  max-width: 100vw;
  overflow-x: hidden;
}

/* 瀑布流网格布局 */
.knowledge-grid {
  /* 使用 CSS Grid 实现瀑布流 */
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;

  /* 针对不同屏幕尺寸的响应式调整 */
  @media (min-width: 640px) {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.25rem;
  }

  @media (min-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }

  @media (min-width: 1280px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 2.5rem;
  }
}

/* 知识库卡片样式 */
.knowledge-card {
  /* 卡片基础样式 */
  break-inside: avoid;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  /* 悬停效果 */
  &:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow:
      0 20px 25px -5px rgba(0, 0, 0, 0.1),
      0 10px 10px -5px rgba(0, 0, 0, 0.04);
    cursor: pointer;
    z-index: 10;
  }

  /* 点击效果 */
  &:active {
    transform: translateY(-4px) scale(1.01);
    transition: all 0.1s ease;
  }
}

/* 占位符卡片样式 */
.knowledge-card-placeholder {
  height: 100%;
  padding: 7.5rem 2.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px dashed #cbd5e1;
  border-radius: 1rem;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;

  p {
    font-size: 1.1rem;
    font-weight: 500;
    color: #64748b;
  }
}

/* 滚动条隐藏 */
::-webkit-scrollbar {
  display: none;
}

/* 响应式调整 */
@media (max-width: 640px) {
  .knowledge-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 0 0.5rem;
  }

  .knowledge-card:hover {
    transform: translateY(-4px);
  }
}

@media (max-width: 1024px) {
  .knowledge-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}

/* 加载动画 */

.knowledge-card {
  animation: fadeInUp 0.6s ease-out backwards;
}

.knowledge-card:nth-child(1) {
  animation-delay: 0.1s;
}

.knowledge-card:nth-child(2) {
  animation-delay: 0.2s;
}

.knowledge-card:nth-child(3) {
  animation-delay: 0.3s;
}

.knowledge-card:nth-child(4) {
  animation-delay: 0.4s;
}

.knowledge-card:nth-child(5) {
  animation-delay: 0.5s;
}

.knowledge-card:nth-child(6) {
  animation-delay: 0.6s;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 改进的焦点样式 */
.knowledge-card:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* 平滑的页面过渡 */
main {
  animation: pageSlideIn 0.5s ease-out;
}

@keyframes pageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}



.knowledge-card-final {
  animation: fadeInUp 0.8s ease-out backwards;
  animation-delay: 1.2s;
  /* 在前6个卡片之后显示 */
}


@keyframes ripple {
  0% {
    width: 0;
    height: 0;
    opacity: 1;
  }

  100% {
    width: 200px;
    height: 200px;
    opacity: 0;
  }
}
</style>
