<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>登录您的账户</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input type="text" id="username" v-model="username" required placeholder="请输入用户名">
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" id="password" v-model="password" required placeholder="请输入密码">
        </div>
        <p v-if="error" class="error-message">{{ error }}</p>
        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading">登录中...</span>
          <span v-else>登录</span>
        </button>
      </form>
      <div class="switch-link">
        还没有账户? <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      isLoading: false,
      error: ''
    };
  },
  methods: {
    async handleLogin() {
      this.isLoading = true;
      this.error = '';
      try {
        // 调用 Vuex action 进行登录
        await this.$store.dispatch('login', {
          username: this.username,
          password: this.password
        });
        // 登录成功后跳转到首页
        this.$router.push('/');
      } catch (err) {
        this.error = err.message || '登录失败，请稍后重试。';
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
/* 共享的认证页面样式 */
.auth-container { display: flex; justify-content: center; align-items: center; padding-top: 50px; }
.auth-card { background: #fff; padding: 2.5rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
h2 { font-size: 1.8rem; margin-bottom: 2rem; }
.form-group { text-align: left; margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
.form-group input { width: 100%; padding: 12px 15px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
.submit-btn { width: 100%; padding: 15px; background-color: var(--primary-color); color: #fff; border: none; border-radius: 8px; cursor: pointer; font-size: 1.1rem; font-weight: bold; margin-top: 1rem; }
.submit-btn:disabled { background-color: #6c757d; }
.error-message { color: #dc3545; margin-top: 1rem; }
.switch-link { margin-top: 1.5rem; color: #6c757d; }
.switch-link a { color: var(--primary-color); text-decoration: none; font-weight: bold; }
</style>