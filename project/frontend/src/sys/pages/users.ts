/**
 * ユーザー管理ページ
 */
import { listUsers, createUser, deleteUser as deleteUserApi } from '../api/users';
import { getMe } from '../api/auth';
import type { User } from '../api/auth';

export default () => ({
  users: [] as User[],
  isAuthenticated: false,
  isAdmin: false,
  currentPage: 'portal',

  async init() {
    try {
      const currentUser = await getMe();
      this.isAuthenticated = true;
      this.isAdmin = currentUser.role === 'admin';
      
      if (this.isAdmin) {
        await this.loadUsers();
      }
    } catch {
      this.isAuthenticated = false;
    }
  },

  async loadUsers() {
    try {
      const response = await listUsers();
      this.users = response.users;
    } catch (error) {
      alert('ユーザー一覧の取得に失敗しました');
    }
  },

  showCreateDialog() {
    const username = prompt('ユーザー名:');
    if (!username) return;
    
    const password = prompt('パスワード:');
    if (!password) return;
    
    const displayName = prompt('表示名:');
    if (!displayName) return;
    
    const email = prompt('メールアドレス:');
    if (!email) return;
    
    const role = confirm('管理者権限を付与しますか?') ? 'admin' : 'user';
    
    this.createUser(username, password, displayName, email, role);
  },

  async createUser(username: string, password: string, displayName: string, email: string, role: string) {
    try {
      await createUser({
        username,
        password,
        displayName,
        role,
        email,
      });
      await this.loadUsers();
      alert('ユーザーを作成しました');
    } catch (error) {
      alert('ユーザーの作成に失敗しました');
    }
  },

  async deleteUser(userId: string) {
    if (!confirm('本当に削除しますか?')) return;
    
    try {
      await deleteUserApi(userId);
      await this.loadUsers();
      alert('ユーザーを削除しました');
    } catch (error) {
      alert('ユーザーの削除に失敗しました');
    }
  },
});
