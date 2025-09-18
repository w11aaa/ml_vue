import Vue from 'vue'
import VueRouter from 'vue-router'
import StockList from '../views/StockList.vue'
import StockChart from '../views/StockChart.vue'
import Login from '../views/Login.vue'
// **已修正此处的路径**
import Register from '../views/Register.vue'
import Watchlist from '../views/Watchlist.vue'
import About from '../views/About.vue'
import store from '../store'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'StockList',
    component: StockList,
    meta: { requiresAuth: true }
  },
  {
    path: '/chart',
    name: 'StockChart',
    component: StockChart,
    props: (route) => ({ stockCode: route.query.stockCode }),
    meta: { requiresAuth: true }
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: Watchlist,
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '*',
    redirect: '/'
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const loggedIn = store.getters.isAuthenticated;
  if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router