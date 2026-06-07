<template>
    <div class="header">
        <div class="header-wrap">
            <div class="nav-wrap">
                <NavBar />
            </div>
            <div class="btn-wrap">
                <button class="ai-btn" @click="showAiChat = true" title="AI租房助手">
                    <i class="fa-solid fa-robot"></i>
                </button>
                <UserButton />
            </div>
        </div>

        <!-- AI 聊天弹窗 -->
        <AiChatDialog
            v-model:visible="showAiChat"
        />
    </div>
</template>
<script setup>
import { ref } from 'vue'
import NavBar from '@/components/NavBar.vue'
import UserButton from '@/components/UserButton.vue';
import AiChatDialog from '@/components/AiChatDialog.vue';

const showAiChat = ref(false)
</script>
<style scoped>
.header {
    width: 100%;
    height: 60px;
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    display: flex;
    align-items: center;
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.15);
    position: sticky;
    top: 0;
    z-index: 1000;
}
.header-wrap {
    display: flex;
    width: 1200px;
    margin: 0 auto;
}
.nav-wrap {
    flex: 1;
}
.btn-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
}

.ai-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: #fff;
    font-size: 18px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.25s ease;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.ai-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}
</style>