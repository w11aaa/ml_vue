<template>
	<nav class="navbar">
		<div class="logo">
			<img src="../images/logo.jpg" alt="Logo">
			<span class="logo-text">Stock Predict</span>
		</div>
		<ul class="links" v-if="isAuthenticated">
			<li><a @click="showDashboard" :class="{active: activeMenu === 'dashboard'}">股市数据</a></li>
			<li><a @click="showAbout" :class="{active: activeMenu === 'about'}">关于我们</a></li>
		</ul>

		<div v-if="isAuthenticated" class="user-profile">
			<span class="username">欢迎, {{ username }}</span>
			<a @click="handleLogout" class="logout-btn">退出</a>
		</div>
		<div v-else class="auth-links">
			<router-link to="/login" class="auth-btn">登录</router-link>
			<router-link to="/register" class="auth-btn register">注册</router-link>
		</div>

	</nav>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  data() {
	  return {
		  activeMenu: 'dashboard'
	  }
  },
  computed: {
    ...mapGetters({
        isAuthenticated: 'isAuthenticated',
        username: 'getUsername'
    })
  },
  methods:{
    ...mapActions(['logout']),
	  setActive(menu){ this.activeMenu = menu; },
	  showDashboard(){
		   this.setActive('dashboard');
		   this.$store.commit("setMenus",[
         {menuName:'个股行情',link:'StockList'},
         {menuName:'K线图表',link:'StockChart'},
         {menuName:'我的自选',link:'Watchlist'}
       ]);
		   this.to("StockList", {}, "股市数据");
	  },
	  showAbout(){
		  this.setActive('about');
		  this.$store.commit("setMenus", []);
		  this.to("About", {}, "关于我们");
	  },
    handleLogout() {
      this.logout();
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>
	.navbar { display: flex; justify-content: space-between; align-items: center; background-color: var(--navbar-bg); padding: 0 2rem; height: 60px; color: white; box-shadow: 0 2px 10px rgba(0,0,0,0.2); flex-shrink: 0; }
	.logo { display: flex; align-items: center; }
	.logo img { height: 40px; border-radius: 50%; }
	.logo-text { font-size: 1.5rem; font-weight: bold; margin-left: 1rem; }
	.links { display: flex; list-style-type: none; margin: 0; padding: 0; }
	.links a { color: #a0aec0; text-decoration: none; padding: 10px 20px; display: block; position: relative; transition: color 0.3s; cursor: pointer; }
	.links a:hover, .links a.active { color: white; }
	.links a::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 0; height: 3px; background-color: var(--primary-color); transition: width 0.3s; }
	.links a:hover::after, .links a.active::after { width: 60%; }

  .user-profile { display: flex; align-items: center; gap: 15px; }
  .username { font-weight: bold; }
  .logout-btn { cursor: pointer; color: #a0aec0; transition: color 0.2s; }
  .logout-btn:hover { color: white; }
  .auth-links { display: flex; gap: 10px; margin-left: auto; }
  .auth-btn { padding: 8px 15px; border: 1px solid #a0aec0; border-radius: 5px; color: #a0aec0; text-decoration: none; transition: all 0.2s; }
  .auth-btn:hover { background-color: var(--primary-color); border-color: var(--primary-color); color: white; }
  .auth-btn.register { background-color: var(--primary-color); border-color: var(--primary-color); color: white; }
</style>