<template>
	<div id="app">
		  <div id="myChart" :style="{width: '300px', height: '300px'}"></div>
	</div>
</template>

<script>
  export default {
	 mounted() {
	 	// 引入基本模板
	 	let echarts = require('echarts')
	 	let myChart =  echarts.init(document.getElementById('myChart'))
	 	// 绘制图表
	 	myChart.setOption({
			  title: { text: '在Vue中使用echarts' },
			  tooltip: {},
			  xAxis: {
				  data: ["衬衫","羊毛衫","雪纺衫","裤子","高跟鞋","袜子"]
			  },
			  yAxis: {},
			  series: [{
				  name: '销量',
				  type: 'bar',
				  data: [5, 20, 36, 10, 10, 20]
			  }]
	 	});
	 }
  } 
</script>