<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="header-logo" @click="$router.push('/')" style="cursor:pointer">
        🏠 应届生租房防坑决策引擎
      </div>
      <nav class="header-nav">
        <router-link to="/">首页</router-link>
        <router-link to="/search">搜索房源</router-link>
      </nav>
    </div>
  </header>
</template>
