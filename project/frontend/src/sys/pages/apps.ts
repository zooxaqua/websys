/**
 * アプリ管理ページ
 */
import { listApps, scanApps as scanAppsApi, enableApp as enableAppApi, disableApp as disableAppApi } from '../api/apps';
import { getMe } from '../api/auth';
import type { App } from '../api/apps';

export default () => ({
  apps: [] as App[],
  isAuthenticated: false,
  isAdmin: false,
  currentPage: 'portal',

  async init() {
    try {
      const currentUser = await getMe();
      this.isAuthenticated = true;
      this.isAdmin = currentUser.role === 'admin';
      
      if (this.isAdmin) {
        await this.loadApps();
      }
    } catch {
      this.isAuthenticated = false;
    }
  },

  async loadApps() {
    try {
      this.apps = await listApps();
    } catch (error) {
      alert('アプリ一覧の取得に失敗しました');
    }
  },

  async scanApps() {
    try {
      const result = await scanAppsApi();
      await this.loadApps();
      alert(result.message);
    } catch (error) {
      alert('アプリスキャンに失敗しました');
    }
  },

  async toggleApp(appId: string, currentlyEnabled: boolean) {
    try {
      if (currentlyEnabled) {
        await disableAppApi(appId);
      } else {
        await enableAppApi(appId);
      }
      await this.loadApps();
    } catch (error) {
      alert('アプリの状態変更に失敗しました');
    }
  },
});
