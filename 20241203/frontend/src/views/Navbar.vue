<template>
	<nav class="navbar">
		<div class="logo">
			<img src="../images/logo.jpg" alt="Logo">
			<span class="logo-text">Stock Predict</span>
		</div>
		<ul class="links">
			<li><a @click="showDashboard" :class="{active: activeMenu === 'dashboard'}">股市数据</a></li>
			<li><a @click="showPrediction" :class="{active: activeMenu === 'prediction'}">股票预测</a></li>
			<li><a @click="showHistory" :class="{active: activeMenu === 'history'}">历史数据</a></li>
			<li><a @click="showAbout" :class="{active: activeMenu === 'about'}">关于我们</a></li>
		</ul>
		<div class="user-profile">
			<img src="https://i.pravatar.cc/150?img=32" alt="用户头像">
		</div>
	</nav>
</template>

<script>
export default {
  data() {
	  return {
		  activeMenu: 'dashboard'
	  }
  },
  methods:{
	  setActive(menu){ this.activeMenu = menu; },
	  showDashboard(){
		   this.setActive('dashboard');
		   this.$store.commit("setMenus",[{menuName:'大盘指数',link:'StockChart'}, {menuName:'个股行情',link:'StockList'}]);
		   this.to("StockChart", {id:1}, "股市数据");
	  },
	  showPrediction(){
		    this.setActive('prediction');
		    this.$store.commit("setMenus", [{menuName:'价格预测',link:'StockPredict'}]);
	  		this.to("StockPredict", {id:1}, "股票预测");
	  },
	  showHistory(){
		  this.setActive('history');
		  this.$store.commit("setMenus", [{menuName:'历史查询',link:'StockList'}]);
		  this.to("StockList", {id:1}, "历史数据");
	  },
	  showAbout(){
		  this.setActive('about');
		  this.$store.commit("setMenus", []);
		  this.to("About", {id:1}, "关于我们");
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
	.user-profile img { border-radius: 50%; width: 40px; height: 40px; object-fit: cover; cursor: pointer; }
</style>