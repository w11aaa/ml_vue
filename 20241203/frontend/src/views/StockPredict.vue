<template>
	<div class="predict-container">
		<div class="form-card">
		    <h2>股票价格预测模型</h2>
			<p class="subtitle">输入当日的股票市场指标，我们将预测下一交易日的收盘价。</p>
		    <form @submit.prevent="predictPrice">
		        <div class="form-grid">
					<div class="form-group"><label for="open">开盘价:</label><input type="text" id="open" v-model="features.open" placeholder="例如: 10.8"></div>
					<div class="form-group"><label for="close">收盘价:</label><input type="text" id="close" v-model="features.close" placeholder="例如: 11.5"></div>
					<div class="form-group"><label for="high">最高价:</label><input type="text" id="high" v-model="features.high" placeholder="例如: 11.8"></div>
					<div class="form-group"><label for="low">最低价:</label><input type="text" id="low" v-model="features.low" placeholder="例如: 10.7"></div>
					<div class="form-group"><label for="volume">成交量:</label><input type="text" id="volume" v-model="features.volume" placeholder="例如: 150000"></div>
					<div class="form-group"><label for="turnover">换手率 (%):</label><input type="text" id="turnover" v-model="features.turnover" placeholder="例如: 1.5"></div>
				</div>
		        <button type="submit" class="submit-btn">
					<span v-if="!isLoading">开始预测</span>
					<span v-else>预测中...</span>
				</button>
		    </form>
		</div>

		<transition name="fade">
			<div v-if="predictedPrice" class="prediction-result-card">
				<div class="result-header">预测结果</div>
				<div class="result-body">
					<p class="predicted-value">{{ predictedPrice }}</p>
					<p class="result-label">预测收盘价 (RMB)</p>
				</div>
				<div class="result-footer">*此预测基于前端模拟，仅供参考，不构成投资建议。</div>
			</div>
		</transition>
	</div>
</template>

<script>
export default {
	data() { return { isLoading: false, features: { open: '', close: '', high: '', low: '', volume: '', turnover: '' }, predictedPrice: null } },
	methods: {
		predictPrice() {
			this.isLoading = true;
			this.predictedPrice = null;
			setTimeout(() => {
				const randomFactor = (Math.random() - 0.5) * 2;
				this.predictedPrice = (parseFloat(this.features.close || 0) * (1 + randomFactor / 10)).toFixed(2);
				this.isLoading = false;
			}, 1500);
		}
	}
}
</script>

<style scoped>
.predict-container { max-width: 800px; margin: 0 auto; }
.form-card { background: #fff; padding: 2.5rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; }
h2 { font-size: 2rem; margin-bottom: 0.5rem; }
.subtitle { color: #666; margin-bottom: 2.5rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; text-align: left; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }
.form-group input { width: 100%; padding: 12px 15px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; transition: border-color 0.3s, box-shadow 0.3s; }
.form-group input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2); }
.submit-btn { width: 100%; padding: 15px; background-color: var(--primary-color); color: #fff; border: none; border-radius: 8px; cursor: pointer; font-size: 1.1rem; font-weight: bold; margin-top: 2.5rem; transition: background-color 0.3s; }
.submit-btn:hover { background-color: #4338ca; }
.prediction-result-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-top: 2rem; border-radius: 15px; padding: 2rem; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
.result-header { font-size: 1.2rem; opacity: 0.8; }
.result-body .predicted-value { font-size: 3.5rem; font-weight: bold; margin: 0.5rem 0; }
.result-body .result-label { font-size: 1rem; opacity: 0.8; margin: 0; }
.result-footer { margin-top: 1.5rem; font-size: 0.8rem; opacity: 0.6; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s, transform 0.5s; }
.fade-enter, .fade-leave-to { opacity: 0; transform: translateY(20px); }
</style>