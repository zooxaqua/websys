/**
 * ナビゲーションコンポーネント
 */
import { getMe } from '../api/auth';
import { listApps } from '../api/apps';
import type { User } from '../api/auth';
import type { App } from '../api/apps';

export default () => ({
  isAuthenticated: false,
  isAdmin: false,
  apps: [] as App[],

  async init() {
    try {
      const user: User = await getMe();
      this.isAuthenticated = true;
      this.isAdmin = user.role === 'admin';
      
      // 有効なアプリのみ取得
      this.apps = await listApps(true);
    } catch {
      this.isAuthenticated = false;
    }
  },

  navigate(page: string) {
    // @ts-ignore
    window.Alpine.store('navigation').setCurrentPage(page);
  },
});
