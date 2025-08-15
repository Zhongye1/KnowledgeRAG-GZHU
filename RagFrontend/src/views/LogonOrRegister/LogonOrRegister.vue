<template>
  <div
    class="min-h-screen relative font-sans bg-cover bg-[url('https://pic3.zhimg.com/v2-30a45afb19fee7450415d366cedacd30_r.jpg')] ">
    <!-- 顶部标题区域 -->
    <div class="text-center py-10 relative z-10">
      <div class="text-5xl font-thin text-white mb-4 tracking-wider drop-shadow-lg">RAG-F智能知识库系统</div>
      <div class="flex justify-center">
        <vue-typewriter-effect :strings="typewriterStrings" class="text-2xl text-white font-light" :loop="true">
        </vue-typewriter-effect>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="grid grid-cols-[1fr_1fr] gap-16 max-w-6xl mx-auto px-8 pb-16 relative z-10">
      <!-- 右侧Logo区域 -->
      <div class="relative flex flex-col h-full items-center gap-8">
        <div
          class="bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl p-8 sticky top-8 min-h-[400px] flex items-center justify-center">
          <div v-if="currentDisplayImage.src" class="relative w-full h-30">
            <transition class="mt-[10px] mb-[100px]" name="image-fade" mode="out-in">
              <DynamicLogo :key="currentDisplayImage.src" :logo-src="currentDisplayImage.src"
                class="w-full  object-cover rounded-xl" />
            </transition>

            <!-- 图片标题覆盖层 -->
            <div class="absolute bottom-4 left-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg p-3">
              <transition name="text-fade" mode="out-in">
                <p :key="currentDisplayImage.alt" class="text-white text-sm font-light text-center">
                  {{ currentDisplayImage.alt }}
                </p>
              </transition>
            </div>
          </div>
          <div v-else class="text-white text-sm font-light">欢迎使用无痕加密系统</div>
        </div>

        <!-- 装饰性元素 -->
        <div class="absolute -top-8 -right-8 w-[100px] h-[100px] pointer-events-none">
          <div class="absolute w-[60px] h-[60px] border-2 border-cyan-400/30 rounded-full animate-spin-slow"></div>
          <div
            class="absolute top-1/2 left-1/2 w-[80px] h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent transform -translate-x-1/2 -translate-y-1/2 animate-pulse">
          </div>
        </div>
      </div>

      <!-- 左侧登录注册区域 -->
      <div class="grid grid-rows-[auto_1fr] gap-12">
        <!-- 登录注册表单 -->
        <div class="bg-black/20 backdrop-blur-xl border  border-white/10 rounded-xl p-8 min-h-[450px]">
          <LoginRegisterForm @image-change="handleImageChange" @form-submit="handleFormSubmit" />
        </div>
      </div>
    </div>

    <!-- 全局加载遮罩 -->
    <div v-if="isLoading" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20">
        <div class="flex items-center space-x-4">
          <div class="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-white font-light">{{ loadingText }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import DynamicLogo from '@/components/canvas-point-unit/DynamicLogo.vue'
import LoginRegisterForm from './LoginRegisterForm.vue'

const currentImageKey = ref<string>('welcome')
const isLoading = ref(false)
const loadingText = ref('')

// 图片映射
const imageMap: Record<string, { src: string; alt: string }> = {
  welcome: {
    src: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400',
    alt: '欢迎使用RAG-F01'
  },
  login: {
    src: 'https://pic2.zhimg.com/v2-e99667cad558acfb5be8572eb0c2b31b_r.jpg',
    alt: '登录'
  },
  register: {
    src: 'https://pic3.zhimg.com/v2-ffed82bbc3cccbede8c17ab1c4885c1c_r.jpg',
    alt: '注册'
  },
  forgot: {
    src: 'https://pic2.zhimg.com/v2-6ebd9fe3e9ae1b3421ae2b8f378c47dd_r.jpg',
    alt: '找回密码'
  },
  success: {
    src: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
    alt: '操作成功'
  }
}

// 计算当前应该显示的图片
const currentDisplayImage = computed(() => {
  return imageMap[currentImageKey.value] || imageMap.welcome
})

// 处理图片变化
const handleImageChange = (imageKey: string) => {
  currentImageKey.value = imageKey
}

// 处理表单提交
const handleFormSubmit = async (data: any) => {
  isLoading.value = true
  loadingText.value = data.type === 'login' ? '正在登录...' : '正在注册...'

  try {
    // token已经在handleSubmit中处理过了，直接使用
    if (data.token) {
      // 保存JWT token
      localStorage.setItem('jwt', data.token);

      if (data.type === 'login') {
        // 登录成功后跳转
        const redirectUrl = new URLSearchParams(window.location.search).get('redirect') || '/knowledge';
        window.location.href = redirectUrl;
      } else {
        // 注册成功后跳转到主页面
        window.location.href = '/knowledge';
      }
    } else {
      console.error(`${data.type === 'login' ? '登录' : '注册'}失败: 未获取到token`);
      alert(`${data.type === 'login' ? '登录' : '注册'}失败: 未获取到访问令牌`);
    }
  } catch (error) {
    console.error('认证失败:', error);
    alert('认证过程中发生错误，请稍后重试');
  } finally {
    isLoading.value = false
    loadingText.value = ''
  }
}

import VueTypewriterEffect from 'vue-typewriter-effect'

const typewriterStrings = computed(() => [
  `RAG-F智能知识库系统`,
  `安全、便捷、智能的知识管理解决方案`,
])
</script>

<style scoped>
/* 保持原有样式 */
.image-fade-enter-active,
.image-fade-leave-active {
  transition: all 0.4s ease-in-out;
}

.image-fade-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}

.image-fade-leave-to {
  opacity: 0;
  transform: scale(1.05) translateY(-10px);
}

.text-fade-enter-active,
.text-fade-leave-active {
  transition: all 0.3s ease;
}

.text-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.text-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@keyframes spin-slow {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 20s linear infinite;
}
</style>