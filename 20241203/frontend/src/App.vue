<template>
  <div id="app-container">
    <div class="background-overlay"></div>
    <div id="app">
      <navbar></navbar>
      <div class="main-content-wrapper">
        <div class="left-sidebar-container">
          <leftnavbar></leftnavbar>
        </div>
        <div class="right-content-area">
          <router-view/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
	export default {
	   components:{
		   navbar: () => import('./views/Navbar.vue'),
		   leftnavbar: () => import('./views/Left.vue')
	   }
	}
</script>

<style>
	:root {
		--primary-color: #4f46e5;
		--background-color: #f0f2f5;
		--card-background-color: rgba(255, 255, 255, 0.7);
		--text-color: #333;
		--sidebar-bg: #2d3748;
		--navbar-bg: #1a202c;
	}

	body {
		margin: 0;
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
		background-color: var(--background-color);
	}

	#app-container {
		position: relative;
		min-height: 100vh;
	}
	
	.background-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
		filter: blur(20px);
		z-index: -1;
	}

	#app {
		display: flex;
		flex-direction: column;
		height: 100vh;
	}

	.main-content-wrapper {
		display: flex;
		flex: 1;
		overflow: hidden;
	}

	.left-sidebar-container {
		width: 220px;
		flex-shrink: 0;
		background: var(--sidebar-bg);
		box-shadow: 2px 0 10px rgba(0,0,0,0.1);
	}

	.right-content-area {
		flex: 1;
		padding: 2rem;
		overflow-y: auto;
		background: var(--card-background-color);
		backdrop-filter: blur(10px);
		border-left: 1px solid rgba(255, 255, 255, 0.2);
		margin: 20px;
		border-radius: 15px;
	}
	
	.right-content-area::-webkit-scrollbar { width: 8px; }
	.right-content-area::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 10px; }
	.right-content-area::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.3); border-radius: 10px; }
	.right-content-area::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.5); }
</style>