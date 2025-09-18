<template>
  <div class="stock-list-container">
    <h1>我的自选股</h1>
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>加载自选股列表中...</p>
    </div>
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
    <table v-else-if="stocks.length" class="stock-table">
      <thead>
        <tr>
          <th>股票代码</th>
          <th>股票名称</th>
          <th>最新价格</th>
          <th>涨跌幅</th>
          <th>成交量（万手）</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="stock in stocks" :key="stock.code" class="stock-item" @click="goToChart(stock.code)">
          <td>{{ stock.code }}</td>
          <td>{{ stock.name }}</td>
          <td :class="stock.price >= stock.prevPrice ? 'up' : 'down'">{{ stock.price.toFixed(2) }}</td>
          <td :class="stock.changePercent >= 0 ? 'up' : 'down'">{{ stock.changePercent.toFixed(2) }}%</td>
          <td>{{ (stock.volume || 0).toFixed(2) }}</td>
          <td>
            <button class="detail-btn remove" @click.stop="removeFromWatchlist(stock.code)">移除自选</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="no-data">
      <p>您的自选股列表为空，请在“个股行情”或K线图页面添加。</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      stocks: [],
      isLoading: false,
      error: null
    };
  },
  created() {
    this.fetchWatchlist();
  },
  methods: {
    async fetchWatchlist() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await this.$axios.get('http://127.0.0.1:5000/api/watchlist');
        this.stocks = response.data.map(stock => ({
            ...stock,
            price: parseFloat(stock.price) || 0,
            prevPrice: parseFloat(stock.prevPrice) || 0,
            changePercent: parseFloat(stock.changePercent) || 0
        }));
      } catch (err) {
        this.error = '加载自选股列表失败，请重新登录或稍后再试。';
      } finally {
        this.isLoading = false;
      }
    },
    goToChart(stockCode) {
      this.$router.push({ name: 'StockChart', query: { stockCode } });
    },
    async removeFromWatchlist(stockCode) {
      if (confirm(`确定要从自选中移除 ${stockCode} 吗？`)) {
        try {
          await this.$axios.delete(`http://127.0.0.1:5000/api/watchlist/${stockCode}`);
          // 从列表中移除，实现即时刷新
          this.stocks = this.stocks.filter(s => s.code !== stockCode);
        } catch (err) {
          alert('移除失败，请稍后再试。');
        }
      }
    }
  }
};
</script>

<style scoped>
/* 复用 StockList.vue 的样式 */
.stock-list-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
h1 { text-align: center; margin-bottom: 30px; color: #1e293b; }
.stock-table { width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
.stock-table th, .stock-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }
.stock-table th { background-color: #f1f5f9; font-weight: 600; color: #334155; }
.stock-item { transition: background-color 0.2s; cursor: pointer; }
.stock-item:hover { background-color: #f8fafc; }
.up { color: #dc2626; }
.down { color: #059669; }
.detail-btn.remove { background-color: #dc3545; }
.loading-container, .error-message, .no-data { text-align: center; padding: 50px 0; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top: 4px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.error-message { color: #dc2626; background-color: #fee2e2; padding: 15px; border-radius: 6px; }
</style>