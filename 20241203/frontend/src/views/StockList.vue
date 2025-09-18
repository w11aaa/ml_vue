<template>
  <div class="stock-list-container">
    <h1>股票列表</h1>

    <!-- 搜索框 -->
    <div class="search-container">
      <input
        type="text"
        v-model="searchKeyword"
        placeholder="输入股票代码或名称搜索"
        @keyup.enter="fetchStockList(1)"
      >
      <button @click="fetchStockList(1)">搜索</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>加载股票数据中...</p>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchStockList(currentPage)" class="retry-btn">重试</button>
    </div>

    <!-- 股票列表 -->
    <table v-else-if="stocks.length" class="stock-table">
      <thead>
        <tr>
          <th>股票代码</th>
          <th>股票名称</th>
          <th>最新价格</th>
          <th>涨跌幅</th>
          <th>成交量（手）</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="stock in stocks"
          :key="stock.code"
          class="stock-item"
          @click="goToChart(stock.code)"
        >
          <td>{{ stock.code }}</td>
          <td>{{ stock.name }}</td>
          <td :class="stock.price >= stock.prevPrice ? 'up' : 'down'">
            {{ stock.price.toFixed(2) }}
          </td>
          <td :class="stock.changePercent >= 0 ? 'up' : 'down'">
            {{ stock.changePercent >= 0 ? '+' : '' }}{{ stock.changePercent.toFixed(2) }}%
          </td>
          <td>{{ stock.volume || '0.00' }}</td>
          <td>
            <button class="detail-btn" @click.stop="goToChart(stock.code)">
              查看详情
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 无数据状态 -->
    <div v-else-if="!isLoading && !error" class="no-data">
      <p>未找到股票数据</p>
    </div>

    <!-- 分页控件 -->
    <div v-if="stocks.length && !isLoading && !error" class="pagination">
      <button
        @click="fetchStockList(currentPage - 1)"
        :disabled="currentPage <= 1"
      >
        上一页
      </button>
      <span>
        第 {{ currentPage }} 页
      </span>
      <button
        @click="fetchStockList(currentPage + 1)"
        :disabled="!pagination.has_more"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      stocks: [],
      isLoading: false,
      error: null,
      currentPage: 1,
      pageSize: 20,
      pagination: {
        has_more: false
      },
      searchKeyword: ''
    }
  },
  created() {
    // 页面加载时获取第一页数据
    this.fetchStockList(1)
  },
  methods: {
    async fetchStockList(page) {
      if (page < 1) return

      this.isLoading = true
      this.error = null
      this.currentPage = page

      try {
        // 构建请求参数
        const params = {
          page,
          pageSize: this.pageSize
        }

        // 如果有搜索关键词，添加到参数中
        if (this.searchKeyword) {
          params.keyword = this.searchKeyword
        }

        // 调用股票列表API
        const response = await this.$axios.get('http://127.0.0.1:5000/api/stocklist', {
          params,
          timeout: 10000
        })

        if (response.data && Array.isArray(response.data.data)) {
          this.stocks = response.data.data.map(stock => ({
            ...stock,
            // 确保数值类型正确
            price: parseFloat(stock.price) || 0,
            prevPrice: parseFloat(stock.prevPrice) || 0,
            changePercent: parseFloat(stock.changePercent) || 0
          }))

          this.pagination = response.data.pagination || {
            has_more: false
          }
        } else {
          this.stocks = []
          this.pagination.has_more = false
        }

      } catch (err) {
        console.error('获取股票列表失败:', err)
        this.error = '获取股票列表失败: ' + (err.message || '网络错误')
        this.stocks = []
      } finally {
        this.isLoading = false
      }
    },

    // 跳转到K线图页面
    goToChart(stockCode) {
      if (!stockCode) {
        console.error('股票代码为空，无法跳转')
        return
      }

      try {
        // 使用路由跳转，传递股票代码参数
        this.$router.push({
          name: 'StockChart',
          query: {
            stockCode: stockCode
          }
        })

        // 调试信息
        console.log(`跳转到K线图，股票代码: ${stockCode}`)
      } catch (err) {
        console.error('路由跳转失败:', err)
        // 备用方案：使用window.location跳转
        window.location.href = `/chart?stockCode=${encodeURIComponent(stockCode)}`
      }
    }
  }
}
</script>

<style scoped>
.stock-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #1e293b;
}

.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-container input {
  flex: 1;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 16px;
}

.search-container button {
  padding: 10px 20px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.stock-table th,
.stock-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.stock-table th {
  background-color: #f1f5f9;
  font-weight: 600;
  color: #334155;
}

.stock-item {
  transition: background-color 0.2s;
  cursor: pointer;
}

.stock-item:hover {
  background-color: #f8fafc;
}

.up {
  color: #dc2626;
}

.down {
  color: #059669;
}

.detail-btn {
  padding: 6px 12px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  background-color: #e2e8f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination button:hover:not(:disabled) {
  background-color: #cbd5e1;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #dc2626;
  background-color: #fee2e2;
  padding: 15px;
  border-radius: 6px;
  text-align: center;
  margin-bottom: 20px;
}

.retry-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.no-data {
  text-align: center;
  padding: 50px 0;
  color: #64748b;
}

@media (max-width: 768px) {
  .stock-table {
    font-size: 14px;
  }

  .stock-table th,
  .stock-table td {
    padding: 8px 10px;
  }

  .detail-btn {
    padding: 4px 8px;
    font-size: 12px;
  }
}
</style>
