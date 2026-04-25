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
    <div class="sort-wrap">

    </div>
    <LoginModal/>
</template>
<script setup>
import NavBar from '@/components/NavBar.vue'
import SearchBar from '@/components/SearchBar.vue';
import { ref } from 'vue';
import UserButton from '@/components/UserButton.vue';
import LoginModal from '@/components/LoginModal.vue';

import { useUserStore } from '@/stores/user.js';
const userStore = useUserStore();

</script>

<style>
*{
    margin: 0;
    padding: 0;
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
</style>