<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="header-logo" @click="$router.push('/')" style="cursor:pointer">
        安租 · 租房风险体检
      </div>
      <nav class="header-nav">
        <router-link to="/">首页</router-link>
        <router-link to="/search">房源体检</router-link>
        <router-link to="/assess/new">新建评估</router-link>
        <router-link to="/favorites">收藏</router-link>
      </nav>
    </div>
  </header>
</template>
