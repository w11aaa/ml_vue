<template>
	<div class="body">
		<div class="container1"> <!-- 容器，用于包裹整个表单内容 -->
		    <h2>添加用户</h2> <!-- 页面标题 -->
		    <form action="#" method="post"> <!-- 表单，action="#"表示不提交到任何服务器地址，仅用于演示 -->
		        <!-- 用户名输入框 -->
		        <div class="form-group">
		            <label for="username">用户名:</label> <!-- 标签，for属性与输入框的id属性对应 -->
		            <input type="text" id="username" name="username" required> <!-- 输入框，用户输入用户名 -->
		        </div>
		        <!-- 密码输入框 -->
		        <div class="form-group">
		            <label for="password">密码:</label> <!-- 标签，for属性与输入框的id属性对应 -->
		            <input type="password" id="password" name="password" required> <!-- 输入框，用户输入密码，type="password"表示密码输入 -->
		        </div>
		        <!-- 提交按钮 -->
		        <button type="submit">提交</button> <!-- 按钮，点击后提交表单 -->
		    </form>
		</div>
	</div>
	
</template>

<script>
</script>


	<style type="text/css">
		/* 全局样式 */
		.body {
		    font-family: Arial, sans-serif; /* 设置字体 */
		    background-color: #f4f4f4; /* 设置背景颜色 */
		    margin: 0; /* 移除默认的外边距 */
		    padding: 0; /* 移除默认的内边距 */
		    display: flex; /* 使用Flexbox布局 */
		    justify-content: center; /* 水平居中 */
		    align-items: center; /* 垂直居中 */
		    height: 100vh; /* 设置高度为视口高度的100% */
		}
		
		/* 容器样式 */
		.container1 {
		    background-color: #fff; /* 设置背景颜色为白色 */
		    padding: 20px; /* 设置内边距 */
		    border-radius: 8px; /* 设置圆角 */
		    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); /* 设置阴影效果 */
		    width: 300px; /* 设置宽度 */
		    text-align: center; /* 设置文本居中 */
		}
		
		/* 标题样式 */
		h2 {
		    margin-bottom: 20px; /* 设置下边距 */
		    color: #333; /* 设置字体颜色 */
		}
		
		/* 表单组样式 */
		.form-group {
		    margin-bottom: 15px; /* 设置下边距 */
		    text-align: left; /* 设置文本左对齐 */
		}
		
		/* 标签样式 */
		label {
		    display: block; /* 设置为块级元素 */
		    margin-bottom: 5px; /* 设置下边距 */
		    font-weight: bold; /* 设置字体加粗 */
		}
		
		/* 输入框样式 */
		input[type="text"],
		input[type="password"] {
		    width: 100%; /* 设置宽度为父元素的100% */
		    padding: 8px; /* 设置内边距 */
		    box-sizing: border-box; /* 包括内边距和边框在内计算宽度 */
		    border: 1px solid #ccc; /* 设置边框 */
		    border-radius: 4px; /* 设置圆角 */
		}
		
		/* 按钮样式 */
		button {
		    width: 100%; /* 设置宽度为父元素的100% */
		    padding: 10px; /* 设置内边距 */
		    background-color: #007BFF; /* 设置背景颜色 */
		    color: #fff; /* 设置字体颜色 */
		    border: none; /* 移除边框 */
		    border-radius: 4px; /* 设置圆角 */
		    cursor: pointer; /* 设置鼠标悬停时显示为手型 */
		    font-size: 16px; /* 设置字体大小 */
		}
		
		/* 按钮悬停样式 */
		button:hover {
		    background-color: #0056b3; /* 鼠标悬停时改变背景颜色 */
		}
	</style>