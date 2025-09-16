<template>
	<aside class="sidebar">
		<h2 class="sidebar-title">功能菜单</h2>
		<ul>
			<li v-for="menu in $store.getters.getMenus" :key="menu.link">
				<a @click="toPage(menu.link)" :class="{active: isActive(menu.link)}">
					{{menu.menuName}}
				</a>
			</li>
		</ul>
	</aside>
</template>

<script>
	export default{
		computed: {
			currentRoute() { return this.$route.path.replace("/", ""); }
		},
		methods:{
			toPage(link){ this.to(link, {id:1}, "跳转") },
			isActive(link) { return this.currentRoute === link; }
		}
	}
</script>

<style scoped>
	.sidebar { background-color: var(--sidebar-bg); padding: 20px 0; height: 100%; color: white; }
	.sidebar-title { text-align: center; margin-bottom: 2rem; font-size: 1.2rem; color: #a0aec0; }
	.sidebar ul { list-style-type: none; padding: 0; margin: 0; }
	.sidebar ul li a { cursor: pointer; text-decoration: none; color: #a0aec0; display: block; padding: 15px 30px; transition: all 0.3s ease; position: relative; }
	.sidebar ul li a:hover { background-color: #4a5568; color: white; }
	.sidebar ul li a.active { background-color: var(--primary-color); color: white; font-weight: bold; }
	.sidebar ul li a.active::before { content: ''; position: absolute; left: 0; top: 0; height: 100%; width: 5px; background-color: #a0aec0; }
</style>