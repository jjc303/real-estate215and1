<template>
  <div class="home-root">
    <div class="page-wrap">
    <!-- 首页主体内容 -->
    <div class="home-container">
        <div class="home-header">
            <img src="@/assets/images/csu-logo.png" alt="中南大学logo" class="csu-logo" />
            <img src="@/assets/images/csu-name.png" alt="中南大学logo" class="csu-name" />
            <div class="home-nav-wrap">
                <NavBar />
            </div>
            <div class="home-user">
              <UserButton />
            </div>
        </div>
        <div class="home-content">
          <div class="title-small">一席定境，一生从容</div>
          <div class="title-large">来中南找房寻找真正的家</div>
          <div class="home-searchBar">
              <SearchBar />
          </div>
        </div>
    </div>
  </div>
  <LoginModal/>
  <!-- 分类展区 -->
  <div class="sort-area">
    <div class="sort-item">
      <div class="sort-title-wrap">
        <div class="sort-big-title">户型多多</div>
        <div class="sort-small-title">一屋一形制，一生一归处</div>
      </div>
      <div class="sort-content">
        <!-- 这里可以放一些户型的图片或者介绍 -->
         <HouseCard 
            v-for="house in houseTypes" 
            :key="house.id" 
            :house="house"
            @click="goToDetail(house)"
          />
      </div>
    </div>
    <div class="sort-item">
      <div class="sort-title-wrap">
        <div class="sort-big-title">小区精选</div>
        <div class="sort-small-title">甄选一城佳境，安享一隅清欢</div>
      </div>
      <div class="sort-content">
        <!-- 这里可以放一些户型的图片或者介绍 -->
         <HouseCard 
            v-for="house in houseEstates" 
            :key="house.id" 
            :house="house"
            @click="goToDetail(house)"
          />
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import HouseCard from '@/components/HouseCard.vue';
import NavBar from '@/components/NavBar.vue';
import SearchBar from '@/components/SearchBar.vue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import UserButton from '@/components/UserButton.vue';
import LoginModal from '@/components/LoginModal.vue';
import { useUserStore } from '@/stores/user.js';
const router =useRouter();
const userStore = useUserStore();

const goToDetail=(house)=>{

}

//户型
const houseTypes = ref([
  { id: 1, 
    title: '一室一厅' ,
    image:'/images/type1.jpg',
    spec:'约60㎡ | 1室1厅1卫',
    price:'￥1000/月起',
    badge:'热销'
  },
  { id: 2, 
    title: '两室一厅' ,
    image:'/images/type2.jpg',
    spec:'约100㎡ | 2室1厅1卫',
    price:'￥2000/月起',
    badge:'特价'
  },
  { id: 3, 
    title: '三室一厅' ,
    image:'/images/type3.jpg',
    spec:'约140㎡ | 3室1厅2卫',
    price:'￥3000/月起',
    badge:'推荐'
  },
  { id: 4, 
    title: '四室一厅' ,
    image:'/images/type4.jpg',
    spec:'约180㎡ | 4室1厅2卫',
    price:'￥4000/月起',
    badge:'新上'
  },
]);
//住宅区
const houseEstates = ref([
  { id: 1, 
    title: '白沙苑' ,
    image:'/images/house1.jpg',
    spec:'舒适宜居住宅',
    price:'￥2000/月起',

  },
  { id: 2, 
    title: '山语城' ,
    image:'/images/house2.jpg',
    spec:'品质生活住宅',
    price:'￥3500/月起',
  },
  {
    id: 3, 
    title: '明昇壹城',
    image:'/images/house3.jpg',
    spec:'高端人气住宅',
    price:'￥5000/月起',
  },
  {
    id: 4, 
    title: '润和滨江湾',
    image:'/images/house4.jpg',
    spec:'豪华顶级住宅',
    price:'￥7000/月起',
  }
]);

</script>

<style>
/* 全局清除浏览器默认白边 */
* {
  margin: 0 ;
  padding: 0 ;
  box-sizing: border-box;
}
</style>
<style scoped>

.home-container {
  width: 1488px;
  height: 600px;
  margin: 0;
  padding: 0;
  background-image: url('@/assets/images/home.jpg');
  background-size: cover;
  background-position: 50% 68%;
  background-repeat: no-repeat;
  position: relative;
}

.csu-logo {
  position: absolute;
  top: 32px;
  left: 230px;
  height: 80px;
  object-fit: contain;
}

.csu-name {
  position: absolute;
  top: 44px;
  left: 310px;
  height: 50px;
  background: transparent;
  object-fit: contain;
}
.home-header {
  position: relative;
  height: 120px;
}
.home-nav-wrap {
  position: absolute;
  top: 40px;       /* 上下位置 */
  left: 460px;     /* 左右位置 */
  z-index: 100;    /* 保证在最上面 */

}
.home-user {
  position: absolute;
  top: 45px;
  right: 40px;
  display: flex;
  gap: 0px;
  align-items: center;
}
.home-content {
  position: absolute;
  top: 50%;
  left: 70%;
  transform: translate(-50%, -50%);
  text-align: left;
  color: #fff;
  width: 600px;
}
.title-small {
  font-size: 32px;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 400;
  letter-spacing: 2px;
  font-family: "Helvetica Neue", "PingFang SC", sans-serif;
  text-transform: uppercase; /* 可选，让文字更规整 */
}

.title-large {
  font-size: 52px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 3px;
  font-family: "Helvetica Neue", "PingFang SC", sans-serif;
  text-shadow: 0 3px 12px rgba(0, 0, 0, 0.25);
  line-height: 1.2;
  white-space: nowrap;
}
.home-searchBar {
  margin-top: 30px;
}

.sort-area {
  display: flex;
  width:1272px;
  flex-direction:column;
  gap: 90px;
  margin:90px  100px;
}
.sort-item {
  height: 400px;
  border-radius: 10px;
}
.sort-big-title {
  font-size: 40px;
  font-weight: 600;
  color: #333;
  text-align: left;
}
.sort-small-title {
  font-size: 18px;
  color: rgba(51, 51, 51, 0.7);
  text-align: left;
}
.sort-content {
  margin-top: 30px;
  display: flex;
  gap: 20px;
  align-items: stretch;
}
</style>