<template>
    <!-- 分页控件 -->
        <div class="pagination">
            <button 
                @click="changePage(1)" 
                :disabled="pageNum === 1"
                class="page-btn"
            >
                首页
            </button>
            <button 
                @click="changePage(pageNum-1)" 
                :disabled="pageNum === 1"
                class="page-btn"
            >
                上一页
            </button>
            <span class="page-info">
                第 {{ pageNum }} 页 / 共 {{ totalPages }} 页
            </span>
            <button 
                @click="changePage(pageNum+1)" 
                :disabled="pageNum >=totalPages"
                class="page-btn"
            >
                下一页
            </button>
            <button 
                @click="changePage(totalPages)" 
                :disabled="pageNum >= totalPages"
                class="page-btn"
            >
                尾页
            </button>
        </div>
</template>
<script setup>
import { computed } from 'vue'
const props=defineProps({
    pageNum:{type:Number,default:1},
    pageSize:{type:Number,default:10},
    total:{type:Number,default:0}
})
const emit = defineEmits(['change'])
const totalPages = computed(() => {
  return Math.ceil(props.total / props.pageSize) || 1
})
// 页码改变触发
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  emit('change', page)
}
</script>

<style scoped>
.pagination {
  text-align: center;
  margin: 40px 0;
}
.page-btn {
  padding: 6px 16px;
  margin: 0 5px;
  border: 1px solid #ccc;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #333;
}
.page-btn:hover:not(:disabled) {
  border-color: #006cd8;
  color: #006cd8;
}
.page-btn:disabled {
  background: #f5f5f5;
  color: #bbb;
  cursor: not-allowed;
  border-color: #eee;
}
.page-info {
  margin: 0 12px;
  font-size: 14px;
  color: #666;
}
</style>