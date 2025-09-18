<template>
  <div class="kline-container">
    <div class="header-section">
      <div class="title-area">
        <h2>{{ stockInfo.code }} {{ stockInfo.name }} K线图</h2>
        <span
          class="watchlist-star"
          :class="{ 'is-in-watchlist': isInWatchlist }"
          @click="toggleWatchlist"
          :title="isInWatchlist ? '从自选中移除' : '添加到自选股'"
        >
          ★
        </span>
        <button @click="updateCurrentStock" :disabled="isUpdating" class="update-single-btn">
          <span v-if="isUpdating">更新中...</span><span v-else>更新数据</span>
        </button>
      </div>
      <div class="controls-area">
        <div class="indicator-buttons" v-if="activePeriod === 'day'">
          <button @click="toggleIndicator('MA5')" :class="{active: visibleIndicators.includes('MA5')}">MA5</button>
          <button @click="toggleIndicator('MA10')" :class="{active: visibleIndicators.includes('MA10')}">MA10</button>
          <button @click="toggleIndicator('MA20')" :class="{active: visibleIndicators.includes('MA20')}">MA20</button>
        </div>
        <div class="period-buttons">
          <button :class="['period-btn', activePeriod === 'day' ? 'active' : '']" @click="changePeriod('day')">日线</button>
          <button :class="['period-btn', activePeriod === 'week' ? 'active' : '']" @click="changePeriod('week')">周线</button>
          <button :class="['period-btn', activePeriod === 'month' ? 'active' : '']" @click="changePeriod('month')">月线</button>
        </div>
      </div>
    </div>
    <p v-if="updateSingleMessage" class="update-message">{{ updateSingleMessage }}</p>

    <div class="stock-stats" v-if="!isLoading && !error && klineData.length">
      <div class="stat-item"><span class="stat-label">最新价</span><span class="stat-value" :class="lastPrice >= lastOpen ? 'up' : 'down'">{{ lastPrice.toFixed(2) }}</span></div>
      <div class="stat-item"><span class="stat-label">涨跌幅</span><span class="stat-value" :class="changePercent >= 0 ? 'up' : 'down'">{{ changePercent >= 0 ? '+' : '' }}{{ changePercent.toFixed(2) }}%</span></div>
      <div class="stat-item"><span class="stat-label">成交量</span><span class="stat-value">{{ lastVolume.toLocaleString() }} 手</span></div>
      <div class="stat-item"><span class="stat-label">今开</span><span class="stat-value">{{ lastOpen.toFixed(2) }}</span></div>
      <div class="stat-item"><span class="stat-label">最高</span><span class="stat-value">{{ lastHigh.toFixed(2) }}</span></div>
      <div class="stat-item"><span class="stat-label">最低</span><span class="stat-value">{{ lastLow.toFixed(2) }}</span></div>
    </div>

    <div v-if="isLoading" class="loading-container"><div class="spinner"></div><p>加载K线数据中...</p></div>
    <div v-else-if="error" class="error-message"><p>{{ error }}</p><button @click="fetchKlineData" class="retry-btn">重试</button></div>
    <div v-else-if="klineData.length" class="chart-container"><div id="klineChart" :style="{width: '100%', height: '500px'}"></div></div>
    <div v-else class="no-data"><p>未找到该股票的K线数据</p></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
// **注意：由于我们不再使用Vuex来判断自选状态，所以可以移除mapGetters**

export default {
  data() {
    return {
      chart: null, isLoading: false, error: null, stockCode: '',
      stockInfo: {code: '', name: ''}, activePeriod: 'day',
      klineData: [], dates: [], volumes: [], predictionData: [],
      lastPrice: 0, lastOpen: 0, lastHigh: 0, lastLow: 0, lastVolume: 0, changePercent: 0,
      colors: {up: '#dc2626', down: '#059669'}, monthColors: {up: '#059669', down: '#dc2626'},
      isUpdating: false, updateSingleMessage: '',
      indicatorData: {}, visibleIndicators: ['MA5', 'MA10', 'MA20'],
      isInWatchlist: false
    }
  },
  watch: {
    '$route.query.stockCode': {
      handler(newCode) {
        if (newCode && newCode !== this.stockCode) {
          this.stockCode = newCode;
          this.fetchKlineData();
          this.checkWatchlistStatus();
        }
      },
      immediate: true
    },
    activePeriod() {
      this.fetchKlineData();
    }
  },
  created() {
    this.stockCode = this.$route.query.stockCode || '';
    if (this.stockCode) {
      // created 钩子中不再调用 fetchKlineData，由 watch 的 immediate: true 触发
    } else {
      this.error = '未指定股票代码';
    }
  },
  mounted() {
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    if (this.chart) {
        this.chart.dispose();
    }
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    async fetchKlineData() {
      this.isLoading = true;
      this.error = null;
      // 在请求新数据前重置所有数据状态
      this.klineData = [];
      this.dates = [];
      this.volumes = [];
      this.predictionData = [];
      this.indicatorData = {};

      try {
        const response = await this.$axios.get('http://127.0.0.1:5000/api/stockkline', {
          params: {stockCode: this.stockCode, period: this.activePeriod, pageSize: 200}
        });
        if (!response.data) throw new Error('服务器返回空数据');
        this.stockInfo = response.data.stockInfo || {code: this.stockCode, name: '未知股票'};
        if (Array.isArray(response.data.predictionData)) this.predictionData = response.data.predictionData;

        const rawData = response.data.data;
        if (!Array.isArray(rawData) || rawData.length === 0) {
            // 如果没有数据，确保图表被清空（如果存在）
            if(this.chart) this.chart.clear();
            return;
        }

        this.indicatorData = {
          MA5: rawData.map(item => item.SMA_5),
          MA10: rawData.map(item => item.SMA_10),
          MA20: rawData.map(item => item.SMA_20),
        };
        rawData.forEach(item => {
          this.klineData.push([
            this.parseNumber(item.open), this.parseNumber(item.price),
            this.parseNumber(item.low), this.parseNumber(item.high)
          ]);
          this.dates.push(item.date);
          this.volumes.push(this.parseNumber(item.volume));
        });

        this.setLastData();
        this.renderChart(); // **恢复直接调用**
      } catch (err) {
        this.error = '加载K线数据失败: ' + (err.message || '未知错误');
      } finally {
        this.isLoading = false;
      }
    },
    toggleIndicator(name) {
      const index = this.visibleIndicators.indexOf(name);
      if (index > -1) this.visibleIndicators.splice(index, 1);
      else this.visibleIndicators.push(name);
      this.renderChart(); // **恢复直接调用**
    },
    async updateCurrentStock() {
      this.isUpdating = true;
      this.updateSingleMessage = `正在为 ${this.stockCode} 更新最新数据...`;
      try {
        await this.$axios.post('http://127.0.0.1:5000/api/update_stock', {stockCode: this.stockCode});
        this.updateSingleMessage = '后台更新任务已启动，等待2秒后自动刷新图表...';
        setTimeout(() => { this.updateSingleMessage = ''; this.fetchKlineData(); }, 2000);
      } catch (err) {
        this.updateSingleMessage = '更新失败，请检查后端服务。';
      } finally {
        setTimeout(() => { this.isUpdating = false; }, 2000);
      }
    },
    async checkWatchlistStatus() {
      if (!this.stockCode) return;
      try {
        // **注意：由于移除了Vuex，这里直接请求API获取状态**
        const response = await this.$axios.get('/api/watchlist/status', {
          params: {stockCodes: this.stockCode}
        });
        this.isInWatchlist = response.data[this.stockCode];
      } catch (err) {
        console.error("检查自选状态失败:", err);
      }
    },
    async toggleWatchlist() {
      try {
        if (this.isInWatchlist) {
          await this.$axios.delete(`/api/watchlist/${this.stockCode}`);
        } else {
          await this.$axios.post('/api/watchlist', {stockCode: this.stockCode});
        }
        this.isInWatchlist = !this.isInWatchlist; // 直接切换本地状态
      } catch (err) {
        alert("操作失败，请稍后再试");
      }
    },
    renderChart() {
      this.$nextTick(() => {
        const chartDom = document.getElementById('klineChart');
        if (!chartDom) return;

        // 如果 chart 实例不存在则初始化，否则直接使用
        if (!this.chart) {
            this.chart = echarts.init(chartDom);
        }

        const currentColors = this.activePeriod === 'month' ? this.monthColors : this.colors;
        const hasPrediction = this.predictionData && this.predictionData.length > 0;
        const indicatorSeries = [];
        const indicatorColors = {MA5: '#3498db', MA10: '#f1c40f', MA20: '#9b59b6'};
        this.visibleIndicators.forEach(name => {
          if (this.indicatorData[name]) {
            indicatorSeries.push({
              name: name, type: 'line', data: this.indicatorData[name],
              smooth: true, symbol: 'none', lineStyle: {color: indicatorColors[name], width: 1.5}
            });
          }
        });
        const predictionDates = hasPrediction ? this.predictionData.map(p => p.date) : [];
        const predictionPrices = hasPrediction ? this.predictionData.map(p => p.price) : [];
        const combinedDates = [...this.dates, ...predictionDates];
        const lastHistoricalPrice = this.klineData.length > 0 ? this.klineData[this.klineData.length - 1][1] : 0;
        const predictionSeriesData = hasPrediction ? [...Array(this.dates.length - 1).fill('-'), lastHistoricalPrice, ...predictionPrices] : [];
        const markPointData = (hasPrediction && this.dates.length > 0) ? [{
          name: '预测起点',
          coord: [this.dates[this.dates.length - 1], lastHistoricalPrice],
          value: '预测',
          symbolOffset: [0, -20],
          label: {position: 'top', color: '#fff', backgroundColor: '#663399', padding: [5, 10], borderRadius: 5},
          itemStyle: {color: '#663399'}
        }] : [];

        const option = {
          backgroundColor: '#fff', tooltip: {trigger: 'axis', axisPointer: {type: 'cross'}},
          legend: {data: ['K线', '预测线', ...this.visibleIndicators], top: 10},
          grid: [{left: '10%', right: '8%', top: '15%', height: '50%'}, {
            left: '10%',
            right: '8%',
            top: '70%',
            height: '15%'
          }],
          xAxis: [{
            type: 'category',
            data: combinedDates,
            boundaryGap: false,
            axisLabel: {interval: Math.ceil(combinedDates.length / 10), rotate: 30}
          }, {type: 'category', gridIndex: 1, data: combinedDates, show: false}],
          yAxis: [{type: 'value', scale: true, name: '价格', splitLine: {lineStyle: {color: '#eee'}}}, {
            type: 'value',
            gridIndex: 1,
            scale: true,
            show: false
          }],
          series: [
            {
              name: 'K线', type: 'candlestick', data: this.klineData,
              itemStyle: {color: currentColors.up, color0: currentColors.down, borderColor: currentColors.up, borderColor0: currentColors.down},
              markPoint: {symbol: 'pin', symbolSize: 50, data: markPointData}
            },
            {
              name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: this.volumes,
              itemStyle: {color: params => { const [open, close] = this.klineData[params.dataIndex]; return close >= open ? currentColors.up : currentColors.down; }}
            },
            ...indicatorSeries,
            ...(hasPrediction ? [{
              name: '预测线', type: 'line', data: predictionSeriesData,
              smooth: true, symbol: 'none', lineStyle: {type: 'dashed', color: '#663399', width: 2}
            }] : [])
          ],
          dataZoom: [{type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100}, {
            type: 'slider',
            xAxisIndex: [0, 1],
            bottom: 5
          }]
        };
        this.chart.setOption(option, {notMerge: true});
      });
    },
    parseNumber(value, defaultValue = 0) {
      const num = Number(value);
      return isNaN(num) ? defaultValue : num;
    },
    setLastData() {
      if (!this.klineData.length) return;
      const last = this.klineData[this.klineData.length - 1];
      this.lastOpen = last[0]; this.lastPrice = last[1];
      this.lastLow = last[2]; this.lastHigh = last[3];
      this.lastVolume = this.volumes[this.volumes.length - 1] || 0;
      this.changePercent = this.lastOpen > 0 ? ((this.lastPrice - this.lastOpen) / this.lastOpen) * 100 : 0;
    },
    changePeriod(period) {
      this.activePeriod = period;
    },
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    }
  }
}
</script>

<style scoped>
/* (样式不变) */
.kline-container { padding: 20px; background-color: #f8fafc; min-height: 100vh; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }
.title-area { display: flex; align-items: center; gap: 20px; }
.watchlist-star { font-size: 24px; color: #ccc; cursor: pointer; transition: all 0.2s; }
.watchlist-star:hover { transform: scale(1.2); }
.watchlist-star.is-in-watchlist { color: #ffc107; }
.update-single-btn { padding: 6px 12px; font-size: 14px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.update-single-btn:disabled { background-color: #6c757d; cursor: not-allowed; }
.update-message { color: #007bff; margin-bottom: 15px; height: 1em; }
.controls-area { display: flex; align-items: center; gap: 20px; }
.indicator-buttons { display: flex; gap: 10px; background-color: #e2e8f0; padding: 4px; border-radius: 6px; }
.indicator-buttons button { padding: 4px 12px; border: none; background-color: transparent; border-radius: 4px; cursor: pointer; font-size: 14px; color: #4a5568; }
.indicator-buttons button.active { background-color: #fff; color: #2d3748; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.period-buttons { display: flex; gap: 10px; }
.period-btn { padding: 8px 16px; border: none; background-color: #e2e8f0; border-radius: 4px; cursor: pointer; }
.period-btn.active { background-color: #3b82f6; color: white; }
.stock-stats { display: flex; flex-wrap: wrap; gap: 20px; padding: 15px; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
.stat-item { display: flex; flex-direction: column; }
.stat-label { font-size: 14px; color: #64748b; margin-bottom: 5px; }
.stat-value { font-size: 18px; font-weight: 500; }
.stat-value.up { color: #dc2626; }
.stat-value.down { color: #059669; }
.chart-container { background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 15px; }
.loading-container, .error-message, .no-data { text-align: center; padding: 50px 0; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top: 4px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.error-message { color: #dc2626; background-color: #fee2e2; padding: 15px; border-radius: 6px; }
.retry-btn { background-color: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-top: 10px; }
</style>