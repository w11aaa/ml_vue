<template>
	
	
	<div>
		
	<!-- 卡片容器 -->
	  <div class="card">
	    <!-- 卡片内容区域 -->
	    <div class="card-content">
	        <!-- 卡片标题 -->
	        <h2 class="card-title">卡片标题</h2>
	        <!-- 卡片描述文本 -->
	        <p class="card-text">
				<table>
				    <thead>
				        <tr>
				            <th>姓名</th>
				            <th>年龄</th>
				            <th>城市</th>
				        </tr>
				    </thead>
				    <tbody>
				        <tr>
				            <td>张三</td>
				            <td>28</td>
				            <td>北京</td>
				        </tr>
				        <tr>
				            <td>李四</td>
				            <td>22</td>
				            <td>上海</td>
				        </tr>
				        <tr>
				            <td>王五</td>
				            <td>34</td>
				            <td>广州</td>
				        </tr>
				        <tr>
				            <td>赵六</td>
				            <td>25</td>
				            <td>深圳</td>
				        </tr>
				    </tbody>
				</table>
					
				
			</p>
	        <!-- 卡片链接 -->
	        <a href="#" class="card-link">了解更多</a>
	    </div>
	</div>
	</div>
</template>

<script>
</script>

<style>
	/* 设置卡片的样式 */
	.card {
		margin-top: 80px;
	    background-color: #fff; /* 设置背景颜色为白色 */
	    border-radius: 10px; /* 设置圆角 */
	    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
	    width: 100%; /* 设置宽度 */
	    text-align: center; /* 设置文本居中对齐 */
	    padding: 20px; /* 添加内边距（这里也可以直接在.card-content中添加） */
	    transition: transform 0.2s; /* 设置过渡效果，用于悬停时的动画 */
	}
	
	
	/* 设置卡片标题的样式 */
	.card-title {
	    margin: 0; /* 移除默认外边距 */
	    font-size: 1.5em; /* 设置字体大小 */
	    color: #333; /* 设置字体颜色 */
	}
	
	/* 设置卡片描述文本的样式 */
	.card-text {
	    color: #666; /* 设置字体颜色 */
	    font-size: 1em; /* 设置字体大小 */
	    margin-top: 10px; /* 添加上边距（与标题分开） */
	}
	
	/* 设置卡片链接的样式 */
	.card-link {
	    text-decoration: none; /* 移除下划线 */
	    color: #007bff; /* 设置链接颜色 */
	    font-weight: bold; /* 设置字体加粗 */
	    transition: color 0.2s; /* 设置过渡效果，用于颜色变化时的动画 */
	}
	
	table {
		width: 100%;
		border-collapse: collapse;
		margin: 20px 0;
		font-size: 18px;
		text-align: left;
	}
	th, td {
		padding: 12px;
		border-bottom: 1px solid #ddd;
	}
	th {
		background-color: #fff;
	}
	tr:hover {
		background-color: #f5f5f5;
	}
	
</style>
