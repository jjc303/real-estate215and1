<template>
    <div class="house-detail">
        <div class="title-section">
            <button class="back-btn" @click="goBack">
                <i class="fa-solid fa-arrow-left"></i>
                <span>返回</span>
            </button>
            <h1 class="house-title">{{ house.title }}</h1>
        </div>

        <div class="main-section">
            <div class="gallery-section">
                <div class="gallery-main">
                    <img v-if="activeMediaType === 'image'" 
                        :src="getCurrentMainImage()" 
                        alt="房源主图"
                        @error="$event.target.src = getDefaultHouseImage(house.id)"
                    />
                    <video v-else :src="house.videoList[currentVideoIndex]?.url" controls class="gallery-video" key="video-player"></video>
                </div>
                <div class="gallery-thumbs">
                    <div 
                        v-for="(img, index) in (house.images && house.images.length > 0 ? house.images : [1])" 
                        :key="'img-' + index"
                        class="thumb-item"
                        :class="{ active: activeMediaType === 'image' && currentImgIndex === index }"
                        @click="activeMediaType = 'image'; currentImgIndex = index"
                    >
                        <img 
                            :src="house.images && house.images.length > 0 ? img : getDefaultHouseImage(house.id)" 
                            :alt="`图片${index + 1}`" 
                            @error="$event.target.src = getDefaultHouseImage(house.id)"
                        />
                    </div>
                    <div 
                        v-for="(video, index) in house.videoList" 
                        :key="'vid-' + index"
                        class="thumb-item thumb-video" 
                        :class="{ active: activeMediaType === 'video' && currentVideoIndex === index }" 
                        @click="activeMediaType = 'video'; currentVideoIndex = index"
                    >
                        <i class="fa-solid fa-play"></i>
                        <span>视频{{ house.videoList.length > 1 ? index + 1 : '' }}</span>
                    </div>
                </div>
            </div>

            <div class="info-section">
                <div class="house-price">
                    <span class="price-value">{{ house.price }}</span>
                    <span class="price-unit">元/月</span>
                </div>
                <div class="house-meta">
                    <div class="meta-item">
                        <span class="meta-label">位置</span>
                        <span class="meta-value">{{ house.district || '无' }} · {{ house.businessArea || '无' }}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">户型</span>
                        <span class="meta-value">{{ house.room === '无' ? '无' : `${house.room}` }} · {{ house.area === 0 ? '无' : `${house.area}㎡` }}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">朝向</span>
                        <span class="meta-value">{{ house.orientation }}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">楼层</span>
                        <span class="meta-value">{{ house.floor || '无' }}</span>
                    </div>
                </div>
                <div class="house-tags">
                    <span v-for="tag in (house.tags || [])" :key="tag" class="tag">{{ tag }}</span>
                </div>
                <div class="info-actions">
                    <button class="btn btn-primary chat-btn" @click="openChat">
                        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                        联系房东
                    </button>
                    <button 
                        class="btn btn-reserve"
                        @click="handleReserve"
                    >
                        <i class="fa-solid fa-calendar-check"></i>
                        预约看房
                    </button>
                    <button 
                        class="btn btn-outline collect-btn" 
                        :class="{ active: house.isCollect }"
                        @click="handleCollect"
                    >
                        {{ house.isCollect ? '★ 已收藏' : '☆ 收藏' }}
                    </button>
                    <button 
                        class="btn btn-ai"
                        @click="showAiChat = true"
                    >
                        <i class="fa-solid fa-robot"></i>
                        问问AI
                    </button>
                </div>
            </div>
        </div>

        <div class="detail-section">
            <h2 class="section-title">房源描述</h2>
            <div class="detail-content">
                {{ house.description || '暂无详细描述' }}
            </div>
        </div>

        <div class="params-section">
            <h2 class="section-title">房源参数</h2>
            <div class="params-grid">
                <div class="param-item">
                    <span class="param-label">建筑面积</span>
                    <span class="param-value">{{ house.area === 0 ? '无' : `${house.area}㎡` }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">户型</span>
                    <span class="param-value">{{ house.room || '无' }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">朝向</span>
                    <span class="param-value">{{ house.orientation || '无' }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">楼层</span>
                    <span class="param-value">{{ house.floor || '无' }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">装修</span>
                    <span class="param-value">{{ house.decoration || '无' }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">地址</span>
                    <span class="param-value">{{ house.address || '无' }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">租金</span>
                    <span class="param-value">{{ house.price === 0 ? '无' : `${house.price}元/月` }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">押金</span>
                    <span class="param-value">{{ house.deposit === 0 ? '无' : `${house.deposit}元` }}</span>
                </div>
            </div>
        </div>

        <ChatPopup 
            :visible="showChat" 
            :house-id="house.id"
            @update:visible="showChat = $event" 
        />

        <!-- 预约看房弹窗 -->
        <ReserveDialog
            v-model:visible="reserveDialogVisible"
            :house-info="houseInfo"
        />

        <!-- AI 聊天弹窗 -->
        <AiChatDialog
            v-model:visible="showAiChat"
            :house-id="house.id"
        />
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user.js';
import { ElMessage } from 'element-plus';
import ChatPopup from '@/components/ChatPopup.vue';
import ReserveDialog from '@/components/ReserveDialog.vue';
import AiChatDialog from '@/components/AiChatDialog.vue';
import { getHouseImage, getDefaultHouseImage } from '@/utils/tools.js';
import { getHouseDetail } from '@/api/house.js';
import { addFavorite, removeFavorite } from '@/api/favorite.js';
import { getHouseVideos } from '@/api/houseVideo.js';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const house = ref({});
const currentImgIndex = ref(0);
const activeMediaType = ref('image'); // 'image' | 'video'
const currentVideoIndex = ref(0);
const showChat = ref(false);
const showAiChat = ref(false);

// 预约相关
const reserveDialogVisible = ref(false);

const houseInfo = computed(() => {
    if (!house.value.id) return null;
    return {
        id: house.value.id,
        title: house.value.title,
        price: house.value.price,
        room: house.value.room,
        area: house.value.area
    };
});

const getCurrentMainImage = () => {
    const images = house.value.images || [];
    if (images.length > 0 && currentImgIndex.value < images.length && images[currentImgIndex.value]) {
        return images[currentImgIndex.value];
    }
    if (house.value.cover_image_url) {
        return house.value.cover_image_url;
    }
    return getDefaultHouseImage(house.value.id);
};

const goBack = () => {
    router.back();
};

const handleCollect = async () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录');
        return;
    }

    try {
        if (house.value.isCollect) {
            // 取消收藏
            const res = await removeFavorite(house.value.id);
            if (res.code === 0) {
                house.value.isCollect = false;
                ElMessage.success('已取消收藏');
            } else {
                ElMessage.error(res.message || '取消收藏失败');
            }
        } else {
            // 添加收藏
            const res = await addFavorite(house.value.id);
            if (res.code === 0) {
                house.value.isCollect = true;
                ElMessage.success('收藏成功');
            } else {
                ElMessage.error(res.message || '收藏失败');
            }
        }
    } catch (error) {
        console.error('收藏操作失败:', error);
        ElMessage.error('收藏失败，请重试');
    }
};

const openChat = () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录');
        return;
    }
    showChat.value = true;
};

const handleReserve = () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录');
        return;
    }
    reserveDialogVisible.value = true;
};

const fetchHouseDetail = async () => {
    try {
        const houseId = parseInt(route.params.id);
        const res = await getHouseDetail(houseId);
        
        if (res.code === 0) {
            const data = res.data;
            house.value = {
                id: data.id,
                title: data.title || '无',
                price: parseFloat(data.rent) || 0,
                deposit: parseFloat(data.deposit) || 0,
                district: data.region || '无',
                businessArea: data.community || '无',
                area: parseFloat(data.area) || 0,
                room: data.house_type || '无',
                orientation: data.orientation || '无',
                floor: data.floor || '无',
                decoration: data.decoration || '无',
                description: data.description || '无',
                status: data.status || '无',
                address: data.address || '无',
                images: data.images || [],
                cover_image_url: data.cover_image_url || null,
                videoList: [],
                tags: [],
                isCollect: false
            };

            // 加载房源视频列表
            try {
                const videosRes = await getHouseVideos(houseId)
                if (videosRes.code === 0) {
                    house.value.videoList = (videosRes.data || []).map(v => ({
                        url: v.url,
                        name: v.url.split('/').pop()
                    }))
                }
            } catch (e) {
                console.error('获取视频列表失败:', e)
            }
        } else {
            ElMessage.error(res.message || '获取房源详情失败');
            house.value = {
                id: houseId,
                title: '房源不存在',
                price: 0,
                district: '',
                businessArea: '',
                area: 0,
                room: 0,
                orientation: '',
                floor: 0,
                description: '',
                images: [],
                tags: []
            };
        }
    } catch (error) {
        ElMessage.error('获取房源详情失败');
        console.error(error);
        house.value = {
            id: parseInt(route.params.id),
            title: '房源不存在',
            price: 0,
            district: '',
            businessArea: '',
            area: 0,
            room: 0,
            orientation: '',
            floor: 0,
            description: '',
            images: [],
            tags: []
        };
    }
};

onMounted(() => {
    fetchHouseDetail();
});
</script>

<style scoped>
.house-detail {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.title-section {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eee;
}

.back-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    margin-bottom: 12px;
    background: #f8fafc;
    color: #64748b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.back-btn:hover {
    background: #e2e8f0;
    color: #475569;
    border-color: #cbd5e1;
}

.back-btn i {
    font-size: 13px;
}

.house-title {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    line-height: 1.4;
    margin: 0;
}

.main-section {
    display: flex;
    gap: 30px;
    margin-bottom: 30px;
}

.gallery-section {
    width: 500px;
    flex-shrink: 0;
}

.gallery-main {
    width: 100%;
    height: 320px;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.gallery-main img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.gallery-thumbs {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 4px;
}

.gallery-thumbs::-webkit-scrollbar {
    height: 4px;
}

.gallery-thumbs::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 2px;
}

.thumb-item {
    width: 70px;
    height: 52px;
    border-radius: 6px;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s;
    flex-shrink: 0;
}

.thumb-item.active {
    border-color: #006cd8;
}

.thumb-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.thumb-item:hover {
    border-color: #006cd8;
}

.info-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 30px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.house-price {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eee;
}

.price-value {
    font-size: 32px;
    font-weight: 700;
    color: #f56c6c;
}

.price-unit {
    font-size: 14px;
    color: #f56c6c;
    margin-left: 4px;
}

.house-meta {
    margin-bottom: 12px;
}

.meta-item {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.meta-label {
    width: 50px;
    font-size: 13px;
    color: #999;
    flex-shrink: 0;
}

.meta-value {
    font-size: 13px;
    color: #333;
}

.house-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
}

.tag {
    padding: 3px 10px;
    background: #e8f4fd;
    color: #006cd8;
    border-radius: 4px;
    font-size: 12px;
}

.info-actions {
    display: flex;
    gap: 10px;
    margin-top: auto;
    padding-top: 16px;
}

.btn {
    padding: 10px 24px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 6px;
    border: none;
}

.btn-primary {
    background: linear-gradient(135deg, #006cd8 0%, #0088ff 100%);
    color: #fff;
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 10px rgba(0, 108, 216, 0.3);
}

.btn-reserve {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: #fff;
}

.btn-reserve:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
}

.btn-reserve i {
    font-size: 14px;
}

.btn-outline {
    background: #fff;
    color: #666;
    border: 1px solid #ddd;
}

.btn-outline:hover {
    border-color: #006cd8;
    color: #006cd8;
}

.btn-outline.active {
    background: #006cd8;
    color: #fff;
    border-color: #006cd8;
}

.btn-ai {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
}

.btn-ai:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.btn-ai i {
    margin-right: 6px;
}

.btn-icon {
    width: 20px;
    height: 20px;
}

.detail-section,
.params-section {
    background: #fff;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    margin-bottom: 30px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #f0f0f0;
}

.detail-content {
    font-size: 15px;
    line-height: 1.8;
    color: #666;
}

.params-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
}

.param-item {
    display: flex;
    flex-direction: column;
    padding: 15px;
    background: #fafafa;
    border-radius: 8px;
}

.param-label {
    font-size: 13px;
    color: #999;
    margin-bottom: 8px;
}

.param-value {
    font-size: 15px;
    font-weight: 500;
    color: #333;
}

@media (max-width: 768px) {
    .main-section {
        flex-direction: column;
    }
    .gallery-section {
        width: 100%;
    }
    .params-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* 图库视频 */
.gallery-video {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 8px;
    outline: none;
    background: #000;
}

/* 视频缩略图 */
.thumb-video {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    background: #f5f5f5;
    cursor: pointer;
    font-size: 12px;
    color: #666;
    border: 2px solid transparent;
}

.thumb-video i {
    font-size: 20px;
    color: #3072f6;
}

.thumb-video.active {
    border-color: #3072f6;
    color: #3072f6;
}
</style>
