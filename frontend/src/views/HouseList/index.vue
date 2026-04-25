<template>
    <div>
        <div class="header">
            <div class="header-wrap">
                <div class="nav-wrap">
                    <NavBar />
                </div>
                <div class="btn-wrap">
                    <UserButton 
                    :isLoggedIn="isLoggedIn" 
                    :userName="userName" 
                    @login="openLoginModal" 
                    @register="openRegisterModal" 
                    @logout="goLogout" />
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import NavBar from '@/components/NavBar.vue'
import SearchBar from '@/components/SearchBar.vue';
import { ref } from 'vue';
import UserButton from '@/components/UserButton.vue';

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
    background-color: #333;
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
</style>