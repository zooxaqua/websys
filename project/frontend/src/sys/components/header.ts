/**
 * ヘッダーコンポーネント
 */
import { getMe, logout as logoutApi } from '../api/auth';
import type { User } from '../api/auth';

export default () => ({
  user: null as User | null,

  async init() {
    try {
      this.user = await getMe();
    } catch {
      this.user = null;
    }
  },

  async logout() {
    try {
      await logoutApi();
      this.user = null;
      window.location.reload();
    } catch (error) {
      alert('ログアウトに失敗しました');
    }
  },
});
