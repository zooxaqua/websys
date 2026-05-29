/**
 * ポータルページ
 */
import { getMe } from '../api/auth';
import { listApps } from '../api/apps';
import type { User } from '../api/auth';
import type { App } from '../api/apps';

export default () => ({
  user: null as User | null,
  apps: [] as App[],
  isAuthenticated: false,
  currentPage: 'portal',

  async init() {
    try {
      this.user = await getMe();
      this.apps = await listApps(true);
      this.isAuthenticated = true;
    } catch {
      this.isAuthenticated = false;
    }
  },
});
