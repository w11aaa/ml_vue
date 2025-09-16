import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import routerSupport from './router/routerSupport'
import axios from 'axios'
Vue.prototype.$axios = axios
Vue.config.productionTip = false
Vue.prototype.to = routerSupport

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
