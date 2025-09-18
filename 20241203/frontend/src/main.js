import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import routerSupport from './router/routerSupport'
import axios from 'axios'

Vue.prototype.$axios = axios
Vue.config.productionTip = false
Vue.prototype.to = routerSupport

// **核心修正：使用Axios请求拦截器来动态设置Token**
axios.interceptors.request.use(
  config => {
    // 在发送请求之前，从localStorage中获取token
    const token = localStorage.getItem('token');

    // 如果token存在，则将其添加到请求的Authorization头中
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
  },
  error => {
    // 对请求错误做些什么
    return Promise.reject(error);
  }
);

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')