<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="header-logo" @click="$router.push('/')" style="cursor:pointer">
        安租 · AI 风险评估
      </div>
      <!-- Mobile hamburger -->
      <button class="hamburger" @click="menuOpen = !menuOpen" aria-label="Toggle menu">
        <span :class="{ open: menuOpen }"></span>
        <span :class="{ open: menuOpen }"></span>
        <span :class="{ open: menuOpen }"></span>
      </button>
      <!-- Desktop nav -->
      <nav class="header-nav" :class="{ open: menuOpen }">
        <router-link to="/" @click="menuOpen = false">首页</router-link>
        <router-link to="/assess/new" @click="menuOpen = false">风险评估</router-link>
        <router-link to="/search" @click="menuOpen = false">房源浏览</router-link>
        <router-link to="/favorites" @click="menuOpen = false">收藏</router-link>
      </nav>
      <!-- Mobile overlay -->
      <div v-if="menuOpen" class="nav-overlay" @click="menuOpen = false"></div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
const menuOpen = ref(false)
</script>
