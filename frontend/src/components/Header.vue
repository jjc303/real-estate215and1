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
</style>