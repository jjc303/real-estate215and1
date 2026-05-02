<template>
    <div class="house-bar-wrap">
        <!-- 左侧房源图片 -->
        <div class="house-img">
            <img 
              :src="house.images?.length?house.images[0]:defaultImg" 
              alt="房源封面" 
              @error="$event.target.src = defaultImg"
            />
        </div>
        <!-- 中间：房源信息 -->
        <div class="house-info">
            <div class="house-title">{{ house.title }}</div>
            <div class="house-desc">
                {{ house.district }} · {{ house.businessArea }} · {{ house.area }}㎡
                · {{ house.room }} · {{ house.orientation }}
            </div>
            <div class="house-tags">
                <span v-for="tag in house.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
            <div class="house-time">
                {{ house.updateTime }}
            </div>
        </div>
        <!-- 右侧：价格 + 收藏 -->
        <div class="house-right">
            <div class="house-price">
                <span class="price-text">{{ house.price }}</span>
                <span class="unit">元/月</span>
            </div>
            <!-- 收藏按钮 星星样式 -->
            <div
                class="collect-btn"
                :class="{ active: house.isCollect }"
                @click.stop="$emit('collect', house)"
            >
                {{ house.isCollect ? '★ 已收藏' : '☆ 收藏' }}
            </div>
        </div>
    </div>
</template>
<script setup>
import defaultImg from '@/assets/images/default-house.png'

defineProps({
    house:{
        type:Object,
        required:true,
        default:()=>({})
    }
})
// 向外派发收藏事件 父组件处理收藏接口
defineEmits(['collect'])
</script>

<style scoped>
.house-bar-wrap {
  display: flex;
  align-items: stretch;
  gap: 18px;
  padding: 20px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}
.house-bar-wrap:hover {
  background-color: #fafafa;
}

/* 左侧图片 */
.house-img {
  width: 200px;
  height: 140px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}
.house-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 中间信息 */
.house-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4px 0;
}
.house-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}
.house-desc {
  font-size: 14px;
  color: #666;
  margin: 8px 0;
}
.house-tags {
  display: flex;
  gap: 10px;
}
.tag {
  padding: 2px 10px;
  background: #f5f7fa;
  color: #666;
  border-radius: 4px;
  font-size: 12px;
}
.house-time {
  font-size: 12px;
  color: #999;
}

/* 右侧价格+收藏 */
.house-right {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  min-width: 110px;
}
.house-price .price-text {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
}
.house-price .unit {
  font-size: 14px;
  color: #f56c6c;
  margin-left: 2px;
}

/* 收藏按钮 */
.collect-btn {
  padding: 3px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  transition: all 0.2s;
}
.collect-btn.active {
  border-color: #006cd8;
  background-color: #006cd8;
  color: #fff;
}
.collect-btn:hover:not(.active) {
  border-color: #006cd8;
  color: #006cd8;
}
</style>