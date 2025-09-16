<template>
	<div class="list-container">
	  <div class="card">
	    <div class="card-content">
	        <h2 class="card-title">主要股票行情</h2>
			<table>
				<thead>
					<tr>
						<th>股票代码</th>
						<th>股票名称</th>
						<th>最新价</th>
						<th>涨跌幅</th>
						<th>成交量 (手)</th>
						<th>成交额 (亿)</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="stock in stocks" :key="stock.code">
						<td>{{ stock.code }}</td>
						<td>{{ stock.name }}</td>
						<td :class="stock.changePercent > 0 ? 'red' : 'green'">{{ stock.price }}</td>
						<td :class="stock.changePercent > 0 ? 'red' : 'green'">
							{{ stock.changePercent > 0 ? '+' : '' }}{{ stock.changePercent.toFixed(2) }}%
						</td>
						<td>{{ (stock.volume / 100).toFixed(2) }}万</td>
						<td>{{ (stock.turnover / 100000000).toFixed(2) }}</td>
					</tr>
				</tbody>
			</table>
	    </div>
	</div>
	</div>
</template>

<script>
export default {
	data() {
		return {
			stocks: [
				{ code: '000001', name: '平安银行', price: 10.45, changePercent: 1.26, volume: 1234567, turnover: 1290123456 },
				{ code: '600519', name: '贵州茅台', price: 1675.00, changePercent: -0.59, volume: 45678, turnover: 765432109 },
				{ code: '000858', name: '五粮液', price: 152.88, changePercent: 0.25, volume: 98765, turnover: 1509876543 },
				{ code: '601318', name: '中国平安', price: 41.86, changePercent: -1.02, volume: 234567, turnover: 981234567 }
			]
		}
	}
}
</script>

<style scoped>
.card { background-color: #fff; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); width: 100%; text-align: center; padding: 2rem; }
.card-title { margin: 0 0 1.5rem 0; font-size: 1.8em; color: #333; text-align: left; }
table { width: 100%; border-collapse: collapse; font-size: 1rem; text-align: left; }
th, td { padding: 15px; border-bottom: 1px solid #ddd; }
th { background-color: #f8f9fa; font-weight: 600; }
tr:hover { background-color: #f5f5f5; }
.red { color: #e53e3e; }
.green { color: #38a169; }
</style>