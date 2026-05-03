<template>
  <Header v-if="!route?.meta?.hideHeader" />

  <router-view />
  
</template>

<script setup>
import { useRoute } from 'vue-router';
import Header from '@/components/Header.vue';

const route=useRoute()

</script>

<style scoped>

</style>
