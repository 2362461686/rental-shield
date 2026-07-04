import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SearchView from '../views/SearchView.vue'
import DetailView from '../views/DetailView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/search', name: 'search', component: SearchView },
  { path: '/house/:id', name: 'detail', component: DetailView, props: true },
  { path: '/favorites', name: 'favorites', component: () => import('../views/FavoritesView.vue') },
  { path: '/assess/new', name: 'assessNew', component: () => import('../views/AssessView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
