import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
	  users:[{id:1,name:'张三1'},{id:2,name:'张三2'}],
	  menus:[]
  },
  getters: {
	  getUsers(state){
		  return state.users
	  },
	  getMenus(state){
	  	return state.menus
	  }
  },
  mutations: {
	  setMenus(state,menus){
		  state.menus = menus
	  }
  },
  actions: {
  },
  modules: {
  }
})
