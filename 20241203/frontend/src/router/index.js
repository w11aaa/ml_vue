import Vue from 'vue'
import VueRouter from 'vue-router'
import StockList from '../views/StockList.vue'
import StockChart from '../views/StockChart.vue'

// 安装路由插件
Vue.use(VueRouter)

// 路由配置
const routes = [
  {
    path: '/',
    name: 'StockList',
    component: StockList
  },
  {
    path: '/chart',
    name: 'StockChart',
    component: StockChart,
    // 接收股票代码参数
    props: (route) => ({
      stockCode: route.query.stockCode
    })
  },
  // 重定向所有未匹配的路径到股票列表
  {
    path: '*',
    redirect: '/'
  }
]

// 创建路由实例
const router = new VueRouter({
  mode: 'history',  // 使用history模式，URL中不显示#
  base: process.env.BASE_URL,
  routes
})

export default router
