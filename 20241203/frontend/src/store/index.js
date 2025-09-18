import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    menus:[],
    // 新增：认证状态
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
  },
  getters: {
    getMenus(state){
      return state.menus
    },
    // 新增：获取认证状态
    isAuthenticated: state => !!state.token,
    getUsername: state => state.username,
  },
  mutations: {
    setMenus(state,menus){
      state.menus = menus
    },
    // 新增：认证相关的 mutations
    AUTH_SUCCESS(state, { token, username }) {
      state.token = token;
      state.username = username;
    },
    LOGOUT(state) {
      state.token = '';
      state.username = '';
    }
  },
  actions: {
    // 新增：登录 action
    async login({ commit }, credentials) {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/login', credentials);
        const { token, username } = response.data;

        localStorage.setItem('token', token);
        localStorage.setItem('username', username);

        // 设置 axios 的默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        commit('AUTH_SUCCESS', { token, username });
      } catch (error) {
        // 清除可能存在的无效 token
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        commit('LOGOUT');
        // 抛出错误，让组件可以捕获
        throw (error.response && error.response.data) || { message: '登录请求失败' };
      }
    },
    // 新增：登出 action
    logout({ commit }) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      // 移除 axios 的默认请求头
      delete axios.defaults.headers.common['Authorization'];
      commit('LOGOUT');
    }
  },
  modules: {}
})