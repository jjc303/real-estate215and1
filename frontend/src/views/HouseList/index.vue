<template>
    <div class="header">
        <div class="header-wrap">
            <div class="nav-wrap">
                <NavBar />
            </div>
            <div class="btn-wrap">
                <UserButton />
            </div>
        </div>
    </div>
    <div class="title">
        <div class="img-wrap">
            <img src="@/assets/images/csu-logo.png" alt="中南大学logo" class="csu-logo" />
            <img src="@/assets/images/csu-name.png" alt="中南大学logo" class="csu-name" />
        </div>
        <div class="searchBar-wrap">
            <SearchBar/>
        </div>
    </div>
    <div class="filter-area">
        <!--面包屑导航-->
        <div class="breadcrumb-nav">
            <!--自动生成路由层级-->
            <template v-for="(item,idx) in route.matched" :key="item.path">
                <router-link :to="item.path" class="breadcrumb-link">
                    {{ item.meta.title }}
                </router-link>
                <span v-if="idx < route.matched.length-1" class="breadcrumb-divider">></span>
            </template>
            
            <!--动态追加筛选条件-->
            <template v-if="selectedDistrict&&selectedDistrict!=='不限'">
                <span class="breadcrumb-divider">></span>
                <router-link :to="`/houseList?district=${selectedDistrict}`" class="breadcrumb-link">
                    {{ selectedDistrict }}租房
                </router-link>
            </template>
        </div>
        <div class="filter-wrap">
             
            <!--区域筛选-->
            <div class="filter-row">
                <span class="filter-label">区域</span>
                <div class="filter-option">
                    <span
                        v-for="d in districts"
                        :key="d"
                        :class="{active:selectedDistrict===d}"
                        @click="selectDistrict(d),setFilter('area',d)"
                    >
                        {{ d }}
                    </span>
                </div>
                
            </div>
            <!--方式筛选-->
            <div class="filter-row">
                <span class="filter-label">方式</span>
                <div class="filter-option">
                    <span
                        v-for="type in rentTypes"
                        :key="type"
                        :class="{active:selectedRentType===type}"
                        @click="selectRentType(type),setFilter('type',type)"
                    >
                        {{ type }}
                    </span>
                </div>
            </div>
            <!--租金筛选-->
             <div class="filter-row">
                <span class="filter-label">租金</span>
                <div class="filter-option">
                    <span
                        v-for="p in prices"
                        :key="p.value"
                        :class="{active:filter.price.includes(p.value)}"
                        @click="setFilter('price',p.value)"
                    >
                        {{ p.label }}
                    </span>
                </div>
                
            </div>
            <!--户型筛选-->
             <div class="filter-row">
                <span class="filter-label">户型</span>
                <div class="filter-option">
                    <span
                        v-for="r in rooms"
                        :key="r.value"
                        :class="{active:filter.room.includes(r.value)}"
                        @click="setFilter('room',r.value)"
                    >
                        {{ r.label }}
                    </span>
                </div>
            </div>
            <!--朝向筛选-->
             <div class="filter-row">
                <span class="filter-label">朝向</span>
                <div class="filter-option">
                    <span
                        v-for="o in orientations"
                        :key="o"
                        :class="{active:filter.orientation.includes(o)}"
                        @click="setFilter('orientation',o)"
                    >
                        {{ o }}
                    </span>    
                </div>
            </div>
        
        </div>
    </div>
    <LoginModal/>
</template>
<script setup>
import NavBar from '@/components/NavBar.vue'
import SearchBar from '@/components/SearchBar.vue';
import { ref,reactive } from 'vue';
import UserButton from '@/components/UserButton.vue';
import LoginModal from '@/components/LoginModal.vue';
import { useUserStore } from '@/stores/user.js';
import { useRoute,useRouter} from 'vue-router';


const userStore = useUserStore();
const route=useRoute();
const router=useRouter();

// 控制更多筛选显示/隐藏
const showMore = ref(false)
const districts=['不限','雨花','岳麓','天心','开福','芙蓉','望城','宁乡市','浏阳','长沙县'];
const selectedDistrict=ref('');
// 租赁方式
const rentTypes = ['不限', '整租', '合租']
const selectedRentType = ref('不限')
const prices = ref([
  { label: '1000以下', value: '1000' },
  { label: '1000-2000', value: '1000-2000' },
  { label: '2000-3000', value: '2000-3000' },
  { label: '5000以上', value: '5000' },
])

const rooms = ref([
  { label: '一室', value: '1' },
  { label: '二室', value: '2' },
  { label: '三室', value: '3' },
  { label: '四室以上', value: '4+' },
])
const orientations = ref([ '东', '南', '西', '北', '南北'])
const filterConfig = {
  area: 'single',       // 区域 单选
  type: 'single',       // 方式 单选
  price: 'multiple',    // 租金 多选
  room: 'multiple',     // 户型 多选
  orientation: 'multiple' // 朝向 多选
}
const filter = reactive({
  area: '',
  price: [],
  room: [],
  orientation: [],
  type: '',
})
const selectDistrict = (d) => {
  selectedDistrict.value = d
}
const selectRentType = (type) => {
  selectedRentType.value = type
}
const setFilter=(key,value)=>{
    const type = filterConfig[key]
    if(type==='single'){
         filter[key] = filter[key] === value ? '' : value
    }
    else if(type==='multiple'){
        let arr=filter[key]
        if(arr.includes(value)){
            filter[key]=arr.filter(i=>i!==value)//取消
        }else{
            filter[key].push(value)//选中
        }
    }
}
</script>

<style>
*{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
</style>
<style scoped>
.header {
    width: 100%;
    height: 60px;
    background-color:rgb(186,194,203);
    display: flex;
    align-items: center;
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
    gap: 10px;
}
.title{
    background-color: rgba(160,160,160,0.4);
    display: flex;
    height: 170px;
    flex-direction: column;
    padding:0 140px;
}
.csu-logo {
    height: 60px;
    object-fit: contain;
}
.csu-name {
    height: 40px;
    background: transparent;
    object-fit: contain;
}
.img-wrap{
    flex:1;
    display: flex;
    align-items: center;
    margin-top: 20px;
}
.searchBar-wrap{
    flex: 1;
    display: flex;
    align-items: center;
    margin-bottom:20px;
}
.filter-area{
    padding:0 140px;
}
.breadcrumb-nav{
    display: flex;
    align-items: center;
    font-size: 14px;
    color: #666;
    margin: 16px 0;
    gap: 6px;
}
.breadcrumb-link{
    color: #666;
    text-decoration: none;
}
.breadcrumb-link:hover {
    color: #006cd8;
}
.breadcrumb-divider{
    color:#999;
}
.filter-area{
    display: flex;
    flex-direction: column;
    justify-content: left;
}
.filter-row{
    display: flex;
    gap:20px;
    align-items: center;
    margin-bottom: 12px;
}
.filter-label{
    width: 50px;
    font-weight: 500;
    color: #333;
}
.filter-option{
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
}
.filter-option span {
  cursor: pointer;
  color: #666;
}
.filter-option span.active {
  color: #006cd8;
  font-weight: bold;
}
</style>