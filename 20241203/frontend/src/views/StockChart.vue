<template>
  <div class="chart-page-container">
   <div class="chart-header">
    <h1>股票数据实时看板</h1>
    <div v-if="error" class="error-message">{{ error }}</div>
   </div>
   <div class="chart-wrapper">
    <div v-if="isLoading" class="loading-spinner">正在从数据库加载数据...</div>
    <div id="myChart" :style="{width: '100%', height: '600px'}"></div>
   </div>
  </div>
</template>

<script>
  export default {
   data() {
    return {
     myChart: null,
     isLoading: true,
     error: null
    }
   },
   async mounted() {
     let echarts = require('echarts');
     this.myChart = echarts.init(document.getElementById('myChart'));
     await this.fetchDataAndRenderChart();
   },
   methods: {
    async fetchDataAndRenderChart() {
     this.isLoading = true;
     this.error = null;
     try {
      const response = await this.$axios.get('http://127.0.0.1:5000/api/stockdata');
      const data = response.data;
      if (data && data.dates) {
       this.renderChart(data);
      } else {
       throw new Error(data.error || "返回的数据格式不正确");
      }
     } catch (err) {
      console.error("获取数据失败:", err);
      this.error = "无法连接后端服务。请确保后端已启动且数据库配置正确。";
      this.myChart.clear();
     } finally {
      this.isLoading = false;
     }
    },
    renderChart(data) {
        let option = {
         title: { text: '实时K线与成交量' },
         tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            // 【核心修改】使用 formatter 自定义提示框内容
            formatter: function (params) {
                // params 是一个数组，包含了当前鼠标位置下的所有系列数据
                // 我们主要关心第一个系列，即K线图
                const kLineData = params[0];
                const date = kLineData.axisValue; // 获取X轴的日期
                const values = kLineData.data;   // 获取数据 [开, 收, 低, 高]

                // 自定义显示格式
                let tooltipHtml = `${date}<br/>`; // 日期
                tooltipHtml += `<strong>开盘:</strong> <span style="color: ${values[1] >= values[0] ? 'red' : 'green'};">${values[0]}</span><br/>`;
                tooltipHtml += `<strong>收盘:</strong> <span style="color: ${values[1] >= values[0] ? 'red' : 'green'};">${values[1]}</span><br/>`;
                tooltipHtml += `<strong>最低:</strong> <span style="color: green;">${values[2]}</span><br/>`;
                tooltipHtml += `<strong>最高:</strong> <span style="color: red;">${values[3]}</span><br/>`;

                // 如果有成交量数据（第二个系列），也一并显示
                if (params[1]) {
                    const volumeData = params[1];
                    tooltipHtml += `<strong>成交量:</strong> ${volumeData.data}手<br/>`;
                }

                return tooltipHtml;
            }
         },
         legend: { data: ['K线', '成交量'] },
         grid: [
          { left: '10%', right: '8%', height: '50%' },
          { left: '10%', right: '8%', top: '65%', height: '15%' }
         ],
         xAxis: [
          { type: 'category', data: data.dates, scale: true, boundaryGap: false, axisLine: { onZero: false } },
          { type: 'category', gridIndex: 1, data: data.dates, scale: true, boundaryGap: false, axisLine: { onZero: false }, axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false } }
         ],
         yAxis: [
          { scale: true, splitArea: { show: true } },
          { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false } }
         ],
         dataZoom: [
          { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
          { show: true, xAxisIndex: [0, 1], type: 'slider', top: '85%', start: 50, end: 100 }
         ],
         series: [
          { name: 'K线', type: 'candlestick', data: data.klineData, itemStyle: { color: '#ec0000', color0: '#00da3c', borderColor: '#8A0000', borderColor0: '#008F28' } },
          { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: data.volumes }
         ]
        };
        this.myChart.setOption(option);
    }
   }
  }
</script>

<style scoped>
.chart-page-container { display: flex; flex-direction: column; height: 100%; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.chart-header h1 { font-size: 1.8rem; margin: 0; color: var(--text-color); }
.chart-wrapper { position: relative; flex: 1; background-color: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); min-height: 640px; }
.loading-spinner { position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; justify-content: center; align-items: center; background: rgba(255,255,255,0.8); font-size: 1.2rem; }
.error-message { color: #e53e3e; background-color: #fff5f5; padding: 1rem; border-radius: 8px; border: 1px solid #e53e3e; }
</style>