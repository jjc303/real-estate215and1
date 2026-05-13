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
</template>
<script setup>
import NavBar from '@/components/NavBar.vue'
import UserButton from '@/components/UserButton.vue';

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
    align-items: center;
    gap: 10px;
}
</style>