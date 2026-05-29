/**
 * ログインページ
 */
import { login as loginApi } from '../api/auth';

export default () => ({
  username: '',
  password: '',
  error: '',
  isAuthenticated: false,

  async login() {
    try {
      this.error = '';
      await loginApi(this.username, this.password);
      this.isAuthenticated = true;
      window.location.reload();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'ログインに失敗しました';
    }
  },
});
