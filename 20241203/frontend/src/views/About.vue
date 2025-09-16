<template>
    <div class="about-container card">
        <h1>关于股票信息展示及预测系统</h1>
        <p>
            本项目是一个基于Vue.js构建的前端应用，旨在提供一个现代化、用户友好的界面，用于展示股票数据并提供基于机器学习的价格预测功能。
        </p>
        <p>
            后端采用轻量级的Python Flask框架，通过SQLAlchemy连接MySQL数据库，为前端提供稳定、高效的数据接口。前端通过Axios与后端进行异步通信，并使用ECharts库进行专业的数据可视化。
        </p>
        <h2>核心技术栈</h2>
        <div class="tech-stack">
			<div class="tech-item"><strong>前端:</strong> Vue.js, Vue Router, Vuex, Axios, ECharts</div>
			<div class="tech-item"><strong>后端:</strong> Python, Flask, SQLAlchemy, Pandas</div>
			<div class="tech-item"><strong>数据库:</strong> MySQL</div>
		</div>
    </div>
</template>

<style scoped>
.card { background-color: #fff; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); width: 100%; padding: 2.5rem; }
h1 { font-size: 2rem; color: #333; }
p { line-height: 1.8; color: #666; font-size: 1.1rem; }
h2 { margin-top: 2rem; color: #333; border-bottom: 2px solid var(--primary-color); padding-bottom: 0.5rem; display: inline-block; }
.tech-stack { margin-top: 1rem; }
.tech-item { background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; font-size: 1.1rem; }
</style>