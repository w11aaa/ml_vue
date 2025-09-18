<template>
  <div class="kline-container">
    <!-- 头部信息和周期选择 -->
    <div class="header-section">
      <h2>
        {{ stockInfo.code }} {{ stockInfo.name }} K线图
      </h2>
      <div class="period-buttons">
        <button
          :class="['period-btn', activePeriod === 'day' ? 'active' : '']"
          @click="changePeriod('day')"
        >
          日线
        </button>
        <button
          :class="['period-btn', activePeriod === 'week' ? 'active' : '']"
          @click="changePeriod('week')"
        >
          周线
        </button>
        <button
          :class="['period-btn', activePeriod === 'month' ? 'active' : '']"
          @click="changePeriod('month')"
        >
          月线
        </button>
      </div>
    </div>

    <!-- 股票关键数据指标 -->
    <div class="stock-stats" v-if="!isLoading && !error && klineData.length">
      <div class="stat-item">
        <span class="stat-label">最新价</span>
        <span class="stat-value" :class="lastPrice >= lastOpen ? 'up' : 'down'">
          {{ lastPrice.toFixed(2) }}
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">涨跌幅</span>
        <span class="stat-value" :class="changePercent >= 0 ? 'up' : 'down'">
          {{ changePercent >= 0 ? '+' : '' }}{{ changePercent.toFixed(2) }}%
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">成交量</span>
        <span class="stat-value">{{ lastVolume.toLocaleString() }} 手</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">今开</span>
        <span class="stat-value">{{ lastOpen.toFixed(2) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">最高</span>
        <span class="stat-value">{{ lastHigh.toFixed(2) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">最低</span>
        <span class="stat-value">{{ lastLow.toFixed(2) }}</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>加载K线数据中...</p>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <p v-if="errorDetails" class="error-details">{{ errorDetails }}</p>
      <button @click="fetchKlineData" class="retry-btn">重试</button>
    </div>

    <!-- K线图容器 -->
    <div v-else-if="klineData.length" class="chart-container">
      <div id="klineChart" :style="{width: '100%', height: '500px'}"></div>
    </div>

    <!-- 无数据状态 -->
    <div v-else-if="!isLoading && !error" class="no-data">
      <p>未找到该股票的K线数据</p>
      <p>可能原因：</p>
      <ul>
        <li>该股票没有历史交易数据</li>
        <li>选择的周期内无交易记录</li>
        <li>数据库中未存储该股票信息</li>
      </ul>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  data() {
    return {
      chart: null,
      isLoading: false,
      error: null,
      errorDetails: null,
      stockCode: '',
      stockInfo: {
        code: '',
        name: ''
      },
      activePeriod: 'day',
      klineData: [], // K线数据 [open, close, low, high]
      dates: [],     // 日期数组
      volumes: [],   // 成交量数组

      // 股票最新数据
      lastPrice: 0,
      lastOpen: 0,
      lastHigh: 0,
      lastLow: 0,
      lastVolume: 0,
      changePercent: 0
    }
  },
  created() {
    // 初始化时获取股票代码
    this.stockCode = this.$route.query.stockCode || ''
    if (this.stockCode) {
      this.fetchKlineData()
    } else {
      this.error = '未指定股票代码，请从股票列表选择股票'
    }
  },
  watch: {
    '$route.query.stockCode': {
      handler(newCode) {
        if (newCode && newCode !== this.stockCode) {
          this.stockCode = newCode
          this.fetchKlineData()
        }
      }
    },
    activePeriod() {
      // 周期改变时重新加载数据
      this.fetchKlineData()
    }
  },
  methods: {
    async fetchKlineData() {
      if (!this.stockCode) {
        this.error = "未指定股票代码"
        return
      }

      this.isLoading = true
      this.error = null
      this.errorDetails = null
      this.klineData = []
      this.dates = []
      this.volumes = []

      try {
        // 调用K线数据接口
        const response = await this.$axios.get('http://127.0.0.1:5000/api/stockkline', {
          params: {
            stockCode: this.stockCode,
            period: this.activePeriod,
            pageSize: 200
          },
          timeout: 10000 // 10秒超时
        })

        // 验证响应数据
        if (!response.data) {
          throw new Error('服务器返回空数据')
        }

        // 存储股票基本信息
        this.stockInfo = response.data.stockInfo || {
          code: this.stockCode,
          name: '未知股票'
        }

        // 验证数据数组
        if (!Array.isArray(response.data.data)) {
          throw new Error('K线数据格式错误，预期为数组')
        }

        const rawData = response.data.data

        if (rawData.length === 0) {
          this.error = `未找到 ${this.stockCode} 的${this.getPeriodText()}K线数据`
          return
        }

        // 处理K线数据 - 严格验证每个数据点
        rawData.forEach((item, index) => {
          // 验证必要字段是否存在
          if (!item.date || item.price === undefined) {
            console.warn(`跳过无效数据项 #${index}:`, item)
            return
          }

          // 转换并验证数值
          const open = this.parseNumber(item.open, `开盘价 #${index}`)
          const close = this.parseNumber(item.price, `收盘价 #${index}`)
          const low = this.parseNumber(item.low, `最低价 #${index}`, Math.min(open, close))
          const high = this.parseNumber(item.high, `最高价 #${index}`, Math.max(open, close))
          const volume = this.parseNumber(item.volume, `成交量 #${index}`, 0)

          // 确保价格有效
          if (open <= 0 || close <= 0) {
            console.warn(`无效价格数据 #${index}，使用默认值`, item)
            const defaultPrice = index > 0 ? this.klineData[index-1][1] : 10.0
            this.klineData.push([defaultPrice, defaultPrice, defaultPrice, defaultPrice])
            this.volumes.push(0)
            this.dates.push(item.date)
            return
          }

          // 添加到数据数组
          this.klineData.push([open, close, low, high])
          this.dates.push(item.date)
          this.volumes.push(volume)
        })

        // 检查处理后的数据是否有效
        if (this.klineData.length === 0) {
          throw new Error('所有K线数据均无效，无法渲染图表')
        }

        // 设置最新数据
        this.setLastData()

        // 渲染图表
        this.renderChart()

      } catch (err) {
        console.error('K线数据加载错误:', err)
        this.error = '加载K线数据失败'

        // 详细错误信息
        if (err.message.includes('Network Error')) {
          this.errorDetails = '无法连接到服务器，请检查后端服务是否已启动（端口5000）'
        } else if (err.message.includes('timeout')) {
          this.errorDetails = '请求超时，请稍后重试'
        } else {
          this.errorDetails = err.message
        }
      } finally {
        this.isLoading = false
      }
    },

    // 安全解析数字，处理无效值
    parseNumber(value, fieldName, defaultValue = 0) {
      if (value === null || value === undefined) {
        console.warn(`${fieldName} 为null，使用默认值 ${defaultValue}`)
        return defaultValue
      }

      const num = Number(value)
      if (isNaN(num)) {
        console.warn(`${fieldName} 不是有效数字 (${value})，使用默认值 ${defaultValue}`)
        return defaultValue
      }

      return num
    },

    // 设置最新数据
    setLastData() {
      if (this.klineData.length === 0) return

      // 获取最后一条数据
      const lastIndex = this.klineData.length - 1
      const [open, close, low, high] = this.klineData[lastIndex]

      this.lastPrice = close
      this.lastOpen = open
      this.lastHigh = high
      this.lastLow = low
      this.lastVolume = this.volumes[lastIndex] || 0
      this.changePercent = ((close - open) / open) * 100 || 0
    },

    // 渲染K线图
    renderChart() {
      // 确保DOM已准备好
      this.$nextTick(() => {
        // 销毁已有图表
        if (this.chart) {
          this.chart.dispose()
        }

        // 获取图表容器
        const chartDom = document.getElementById('klineChart')
        if (!chartDom) {
          this.error = '图表容器不存在，无法渲染K线图'
          return
        }

        try {
          // 初始化图表
          this.chart = echarts.init(chartDom)

          // 设置图表配置
          const option = {
            backgroundColor: '#fff',
            tooltip: {
              trigger: 'axis',
              axisPointer: {
                type: 'cross'
              },
              formatter: params => this.formatTooltip(params)
            },
            grid: [
              { left: '10%', right: '8%', top: '15%', height: '50%' },
              { left: '10%', right: '8%', top: '70%', height: '15%' }
            ],
            xAxis: [
              {
                type: 'category',
                data: this.dates,
                boundaryGap: false,
                axisLabel: {
                  interval: Math.ceil(this.dates.length / 10),
                  rotate: 30
                }
              },
              {
                type: 'category',
                gridIndex: 1,
                data: this.dates,
                show: false
              }
            ],
            yAxis: [
              {
                type: 'value',
                scale: true,
                name: '价格',
                splitLine: { lineStyle: { color: '#eee' } }
              },
              {
                type: 'value',
                gridIndex: 1,
                scale: true,
                show: false
              }
            ],
            series: [
              {
                name: 'K线',
                type: 'candlestick',
                data: this.klineData,
                itemStyle: {
                  color: '#dc2626',       // 上涨颜色
                  color0: '#059669',      // 下跌颜色
                  borderColor: '#dc2626',
                  borderColor0: '#059669'
                }
              },
              {
                name: '成交量',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: this.volumes,
                itemStyle: {
                  color: params => {
                    const [open, close] = this.klineData[params.dataIndex]
                    return close >= open ? '#dc2626' : '#059669'
                  }
                }
              }
            ],
            dataZoom: [
              {
                type: 'inside',
                xAxisIndex: [0, 1],
                start: 50,
                end: 100
              },
              {
                type: 'slider',
                xAxisIndex: [0, 1],
                bottom: 5
              }
            ]
          }

          // 设置配置并渲染
          this.chart.setOption(option)

          // 监听窗口大小变化
          window.addEventListener('resize', this.handleResize)

        } catch (err) {
          console.error('渲染K线图失败:', err)
          this.error = '渲染K线图失败: ' + err.message
        }
      })
    },

    // 格式化提示框内容
    formatTooltip(params) {
      if (!params || params.length === 0) return ''

      const klineParam = params.find(p => p.seriesName === 'K线')
      const volumeParam = params.find(p => p.seriesName === '成交量')

      if (!klineParam) return '无K线数据'

      const [open, close, low, high] = klineParam.data || [0, 0, 0, 0]
      const volume = volumeParam ? volumeParam.data : 0
      const isUp = close >= open

      return `
        <div style="padding: 8px; font-size: 14px;">
          <div style="font-weight: bold; margin-bottom: 5px;">${klineParam.name}</div>
          <div>开盘: ${open.toFixed(2)}</div>
          <div style="color: ${isUp ? '#dc2626' : '#059669'}">
            收盘: ${close.toFixed(2)}
          </div>
          <div>最低: ${low.toFixed(2)}</div>
          <div>最高: ${high.toFixed(2)}</div>
          <div>成交量: ${volume.toLocaleString()} 手</div>
        </div>
      `
    },

    handleResize() {
      if (this.chart) {
        this.chart.resize()
      }
    },

    changePeriod(period) {
      this.activePeriod = period
    },

    getPeriodText() {
      switch(this.activePeriod) {
        case 'day': return '日'
        case 'week': return '周'
        case 'month': return '月'
        default: return '日'
      }
    }
  },
  beforeDestroy() {
    // 清理图表和事件监听
    if (this.chart) {
      this.chart.dispose()
    }
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.kline-container {
  padding: 20px;
  background-color: #f8fafc;
  min-height: 100vh;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.period-buttons {
  display: flex;
  gap: 10px;
}

.period-btn {
  padding: 8px 16px;
  border: none;
  background-color: #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.period-btn.active {
  background-color: #3b82f6;
  color: white;
}

.period-btn:hover:not(.active) {
  background-color: #cbd5e1;
}

.stock-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 18px;
  font-weight: 500;
}

.stat-value.up {
  color: #dc2626;
}

.stat-value.down {
  color: #059669;
}

.chart-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 15px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 500px;
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

.error-details {
  font-size: 14px;
  margin: 10px 0;
}

.retry-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background-color: #2563eb;
}

.no-data {
  text-align: center;
  padding: 50px 0;
  color: #64748b;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-data ul {
  text-align: left;
  max-width: 300px;
  margin: 15px auto;
  padding-left: 20px;
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .stock-stats {
    gap: 15px;
    padding: 10px;
  }

  .stat-value {
    font-size: 16px;
  }
}
</style>
