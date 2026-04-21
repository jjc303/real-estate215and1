<template>
  <div class="search-bar">
    <input 
      type="text" 
      placeholder="搜索房源..." 
      v-model="searchText"
      @keyup.enter="handleSearch" 
    />
    
    <button 
      class="search-btn" 
      @click="handleSearch"
      aria-label="搜索"
    >
      <i class="fa-solid fa-magnifying-glass"></i>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 绑定输入框文字
const searchText = ref('');

// 搜索逻辑（可对接后端接口）
const handleSearch = () => {
  if (!searchText.value.trim()) {
    alert('请输入搜索内容！');
    return;
  }
  console.log('正在搜索：', searchText.value);
  // 这里后续对接你的搜索接口
  //例： fetchSearchData(searchText.value)
};
</script>

<style scoped>
.search-bar {
  width: 600px;
  height: 56px;
  background: rgba(255, 255, 255, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px; /* 输入框和按钮的间距 */
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

/* 聚焦时整体高亮 */
.search-bar:focus-within {
  background: rgba(255, 255, 255, 0.35);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* 输入框：占满剩余空间 */
.search-bar input {
  flex: 1;
  height: 100%;
  background: transparent;
  border: none;
  outline: none;
  font-size: 16px;
  color: #fff;
  padding-left: 8px;
}

/* 提示文字 */
.search-bar input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}


.search-btn {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%; /* 圆形按钮，更精致 */
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

/* 按钮 hover 效果 */
.search-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  color: #fff;
  transform: scale(1.05); /* 轻微放大，互动感更强 */
}

/* 按钮点击效果 */
.search-btn:active {
  transform: scale(0.95);
}
</style>