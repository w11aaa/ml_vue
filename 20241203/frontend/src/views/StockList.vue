<template>
  <div class="stock-list-container">
    <h1>股票列表</h1>

    <div class="toolbar-container">
      <div class="search-container">
        <input type="text" v-model="searchKeyword" placeholder="输入股票代码或名称搜索" @keyup.enter="fetchStockList(1)">
        <button @click="fetchStockList(1)">搜索</button>
      </div>
      <button @click="updateAllStocks" :disabled="isUpdatingAll" class="update-all-btn">
        <span v-if="isUpdatingAll">更新进行中...</span>
        <span v-else>全部更新</span>
      </button>
    </div>

    <div v-if="isUpdatingAll" class="progress-container">
      <div class="progress-bar-wrapper">
        <div class="progress-bar" :style="{ width: progressPercentage + '%' }"></div>
      </div>
      <div class="progress-text">{{ updateMessage }} ({{ updateProgress }}/{{ updateTotal }}) - {{ progressPercentage.toFixed(1) }}%</div>
    </div>
    <p v-else class="update-message-placeholder"></p>

    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>加载股票数据中...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchStockList(currentPage)" class="retry-btn">重试</button>
    </div>

    <table v-else-if="stocks.length" class="stock-table">
      <thead>
        <tr>
          <th>股票代码</th><th>股票名称</th><th>最新价格</th><th>涨跌幅</th><th>成交量（万手）</th><th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="stock in stocks" :key="stock.code" class="stock-item" @click="goToChart(stock.code)">
          <td>{{ stock.code }}</td>
          <td>{{ stock.name }}</td>
          <td :class="stock.price >= stock.prevPrice ? 'up' : 'down'">{{ stock.price.toFixed(2) }}</td>
          <td :class="stock.changePercent >= 0 ? 'up' : 'down'">{{ stock.changePercent >= 0 ? '+' : '' }}{{ stock.changePercent.toFixed(2) }}%</td>
          <td>{{ stock.volume || '0.00' }}</td>
          <td><button class="detail-btn" @click.stop="goToChart(stock.code)">查看详情</button></td>
        </tr>
      </tbody>
    </table>

    <div v-else class="no-data"><p>未找到股票数据</p></div>

    <div v-if="pagination.totalPages > 1 && !isLoading && !error" class="pagination">
      <button @click="fetchStockList(currentPage - 1)" :disabled="currentPage <= 1">上一页</button>
      <button v-for="page in visiblePageNumbers" :key="page" @click="fetchStockList(page)" :class="{ active: currentPage === page }">{{ page }}</button>
      <span v-if="currentPage + 4 < pagination.totalPages">...</span>
      <button @click="fetchStockList(currentPage + 1)" :disabled="currentPage >= pagination.totalPages">下一页</button>
      <span class="total-pages">共 {{ pagination.totalPages }} 页</span>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      stocks: [], isLoading: false, error: null, currentPage: 1, pageSize: 20,
      pagination: { has_more: false, total: 0, totalPages: 0 },
      searchKeyword: '', isUpdatingAll: false, updateProgress: 0,
      updateTotal: 0, updateMessage: '', updateInterval: null
    }
  },
  created() { this.fetchStockList(1); },
  computed: {
    visiblePageNumbers() {
      const pages = []; const startPage = this.currentPage;
      const endPage = Math.min(this.currentPage + 4, this.pagination.totalPages);
      for (let i = startPage; i <= endPage; i++) { pages.push(i); }
      return pages;
    },
    progressPercentage() {
      if (this.updateTotal === 0) return 0;
      return (this.updateProgress / this.updateTotal) * 100;
    }
  },
  methods: {
    async fetchStockList(page) {
      if (page < 1 || (page > this.pagination.totalPages && this.pagination.totalPages > 0)) return;
      this.isLoading = true; this.error = null; this.currentPage = page;
      try {
        const params = { page, pageSize: this.pageSize };
        if (this.searchKeyword) params.keyword = this.searchKeyword;
        const response = await this.$axios.get('http://127.0.0.1:5000/api/stocklist', { params });
        if (response.data && Array.isArray(response.data.data)) {
          this.stocks = response.data.data.map(stock => ({
            ...stock, price: parseFloat(stock.price) || 0,
            prevPrice: parseFloat(stock.prevPrice) || 0,
            changePercent: parseFloat(stock.changePercent) || 0
          }));
          this.pagination = response.data.pagination;
        } else {
          this.stocks = []; this.pagination = { has_more: false, total: 0, totalPages: 0 };
        }
      } catch (err) { this.error = '获取股票列表失败: ' + (err.message || '网络错误');
      } finally { this.isLoading = false; }
    },
    goToChart(stockCode) { if (stockCode) this.$router.push({ name: 'StockChart', query: { stockCode: stockCode } }); },
    async updateAllStocks() {
      if (this.isUpdatingAll) return;
      if (confirm('“全部更新”可能需要较长时间，确定要开始吗？')) {
        try {
          await this.$axios.post('http://127.0.0.1:5000/api/update_all_stocks');
          this.isUpdatingAll = true; this.updateMessage = '任务已启动，正在连接...';
          this.updateInterval = setInterval(this.checkUpdateStatus, 1500);
        } catch (err) {
          if (err.response && err.response.status === 409) alert('启动失败：已有更新任务正在运行中。');
          else alert('启动全部更新任务失败，请检查后端服务。');
        }
      }
    },
    async checkUpdateStatus() {
      try {
        const response = await this.$axios.get('http://127.0.0.1:5000/api/update_status');
        const status = response.data;
        this.updateProgress = status.progress; this.updateTotal = status.total;
        this.updateMessage = status.message;
        if (!status.running) {
          clearInterval(this.updateInterval); this.updateInterval = null;
          this.updateMessage = status.message || '更新完成！';
          setTimeout(() => { this.isUpdatingAll = false; this.fetchStockList(1); }, 3000);
        }
      } catch (err) {
        clearInterval(this.updateInterval); this.updateInterval = null;
        this.isUpdatingAll = false; alert('与服务器断开连接，已停止查询更新状态。');
      }
    }
  },
  beforeDestroy() { if (this.updateInterval) clearInterval(this.updateInterval); }
}
</script>

<style scoped>
.stock-list-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
h1 { text-align: center; margin-bottom: 30px; color: #1e293b; }
.toolbar-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.search-container { display: flex; gap: 10px; flex-grow: 1; }
.search-container input { flex: 1; padding: 10px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 16px; }
.search-container button { padding: 10px 20px; background-color: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer; }
.update-all-btn { padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 20px; white-space: nowrap; }
.update-all-btn:disabled { background-color: #6c757d; cursor: not-allowed; }
.update-message-placeholder { height: 45px; margin-bottom: 15px; }
.progress-container { margin-bottom: 15px; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f8f9fa; height: 45px; box-sizing: border-box; }
.progress-bar-wrapper { width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }
.progress-bar { height: 100%; background-color: #007bff; transition: width 0.4s ease; border-radius: 10px; }
.progress-text { text-align: center; margin-top: 5px; font-size: 14px; color: #495057; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stock-table { width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden; }
.stock-table th, .stock-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }
.stock-table th { background-color: #f1f5f9; font-weight: 600; color: #334155; }
.stock-item { transition: background-color 0.2s; cursor: pointer; }
.stock-item:hover { background-color: #f8fafc; }
.up { color: #dc2626; }
.down { color: #059669; }
.detail-btn { padding: 6px 12px; background-color: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 8px; margin-top: 20px; }
.pagination button { padding: 8px 12px; background-color: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 4px; cursor: pointer; }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.pagination button:hover:not(:disabled) { background-color: #cbd5e1; }
.pagination button.active { background-color: #3b82f6; color: white; border-color: #3b82f6; }
.pagination .total-pages { margin-left: 15px; color: #64748b; font-size: 14px; }
.loading-container, .error-message, .no-data { text-align: center; padding: 50px 0; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top: 4px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.error-message { color: #dc2626; background-color: #fee2e2; padding: 15px; border-radius: 6px; }
.retry-btn { background-color: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-top: 10px; }
</style>