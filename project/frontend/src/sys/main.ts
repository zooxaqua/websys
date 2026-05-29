/**
 * エントリーポイント
 */
import Alpine from 'alpinejs';
import 'bootstrap';

// コンポーネント
import header from './components/header';
import navigation from './components/navigation';

// ページ
import loginPage from './pages/login';
import portalPage from './pages/portal';
import usersPage from './pages/users';
import appsPage from './pages/apps';

// Alpine.js にコンポーネントを登録
Alpine.data('header', header);
Alpine.data('navigation', navigation);
Alpine.data('loginPage', loginPage);
Alpine.data('portalPage', portalPage);
Alpine.data('usersPage', usersPage);
Alpine.data('appsPage', appsPage);

// ナビゲーションストア
Alpine.store('navigation', {
  currentPage: 'portal',
  setCurrentPage(page: string) {
    this.currentPage = page;
  },
});

// Alpine.js 起動
Alpine.start();

// グローバルに Alpine を公開（デバッグ用）
(window as any).Alpine = Alpine;
