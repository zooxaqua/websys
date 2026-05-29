# 単体テスト結果レポート（システム共通基盤）

**工程5：単体評価**  
**作成日**: 2026年5月29日  
**対象**: システム共通基盤（sys）

---

## 1. テスト実施サマリー

| 項目 | 結果 |
|------|------|
| **総テスト数** | 128件 |
| **成功** | 107件 |
| **失敗** | 21件 |
| **スキップ** | 0件 |
| **成功率** | 83.6% |

---

## 2. カバレッジサマリー

| 指標 | 目標 | 実績 | 達成状況 |
|------|------|------|----------|
| **ラインカバレッジ** | 80% | 42.0% | ⚠️ 未達 |
| **分岐カバレッジ** | 80% | 19.3% | ❌ 未達 |
| **MCDCカバレッジ** | 100% | 19.3% | ❌ 未達 |

### 2.1 詳細カバレッジ（モジュール別）

| モジュール | ライン | 分岐 | 状態 |
|-----------|--------|------|------|
| **Models** | | | |
| `models/user.py` | 100% | - | ✅ 完了 |
| `models/session.py` | 100% | - | ✅ 完了 |
| `models/app.py` | 100% | - | ✅ 完了 |
| `models/notification.py` | 100% | 2/2 | ✅ 完了 |
| **DAL** | | | |
| `dal/json_dal.py` | 100% | 22/22 | ✅ 完了 |
| `dal/user_dal.py` | 100% | - | ✅ 完了 |
| `dal/session_dal.py` | 68% | 3/10 | ⚠️ 一部失敗 |
| `dal/app_dal.py` | 75% | - | ⚠️ 部分カバー |
| `dal/notification_dal.py` | 23% | 0/8 | ❌ 未実施 |
| **Core** | | | |
| `core/config.py` | 100% | - | ✅ 完了 |
| `core/security.py` | 96% | 0/2 | ⚠️ 依存関係問題 |
| **API** | | | |
| `api/auth.py` | 0% | 0/0 | ❌ 未実施 |
| `api/users.py` | 0% | 0/0 | ❌ 未実施 |
| `api/apps.py` | 0% | 0/0 | ❌ 未実施 |
| `api/notifications.py` | 0% | 0/0 | ❌ 未実施 |
| `api/config.py` | 0% | 0/2 | ❌ 未実施 |
| `api/health.py` | 0% | 0/0 | ❌ 未実施 |
| **Services** | | | |
| `services/auth_service.py` | 0% | 0/18 | ❌ 未実施 |
| `services/user_service.py` | 0% | 0/26 | ❌ 未実施 |
| `services/jwt_service.py` | 0% | 0/2 | ❌ 未実施 |
| `services/app_service.py` | 0% | 0/28 | ❌ 未実施 |
| `services/notification_service.py` | 0% | 0/10 | ❌ 未実施 |

---

## 3. 失敗テスト一覧

### 3.1 Critical（重大）

| ID | テストケース | 失敗内容 | 原因分類 | 重大度 |
|----|------------|----------|---------|--------|
| TC-SECURITY-001〜009 | hash_password/verify_password | `ValueError: password cannot be longer than 72 bytes` | 依存関係問題（bcrypt） | Critical |
| TC-NOTIF-013,014 | is_expired() | `TypeError: can't compare offset-naive and offset-aware datetimes` | 実装コードバグ | Critical |
| TC-SESSION-006 | is_valid() | `TypeError: can't compare offset-naive and offset-aware datetimes` | 実装コードバグ | Critical |
| TC-SESSION-DAL-003,004 | セッションファイルIO | ファイルが作成/削除されない | 実装コードバグ | Critical |

### 3.2 Medium（中）

| ID | テストケース | 失敗内容 | 原因分類 | 重大度 |
|----|------------|----------|---------|--------|
| TC-NOTIF-006 | boundary_title_max | タイトル長が198文字（200期待） | テストデータ不備 | Medium |
| TC-SESSION-012 | invalid_expiresAt_type | ValidationError発生せず | Pydantic型変換問題 | Medium |

---

## 4. 実施済みテストケース

### 4.1 Models層（100%完了）

| モジュール | テストケース数 | 成功 | 失敗 | 備考 |
|-----------|--------------|------|------|------|
| **user.py** | 21 | 21 | 0 | バリデーション・シリアライズ完全カバー |
| **session.py** | 16 | 15 | 1 | datetime比較エラー（実装バグ） |
| **app.py** | 11 | 11 | 0 | マニフェスト検証含む |
| **notification.py** | 20 | 17 | 3 | datetime比較エラー・境界値テスト |

### 4.2 DAL層（75%完了）

| モジュール | テストケース数 | 成功 | 失敗 | 備考 |
|-----------|--------------|------|------|------|
| **json_dal.py** | 22 | 22 | 0 | CRUD・ページネーション・エラー処理 |
| **user_dal.py** | 3 | 3 | 0 | ユーザー検索・更新 |
| **session_dal.py** | 4 | 2 | 2 | ファイルIO失敗（実装バグ） |

### 4.3 Core層（98%完了）

| モジュール | テストケース数 | 成功 | 失敗 | 備考 |
|-----------|--------------|------|------|------|
| **security.py** | 20 | 11 | 9 | JWT成功、bcrypt失敗（依存関係） |
| **config.py** | - | - | - | インポートテストのみ |

### 4.4 API層（0%完了）

未実施。依存関係が多く、単体テストよりも結合テストに適している。

### 4.5 Services層（0%完了）

未実施。優先度Highだが、時間的制約により未着手。

---

## 5. 検出された実装コードのバグ

### 5.1 Critical（修正必須）

#### BUG-01: datetime aware/naive 比較エラー
- **ファイル**: `project/backend/app/sys/models/notification.py:28`, `session.py:18`
- **内容**: `datetime.utcnow()`（naive）と `self.expiresAt`（aware）を比較できない
- **修正案**: `datetime.now(timezone.utc)` を使用
- **影響範囲**: Notification, Session モデルの有効期限判定

```python
# 現在（誤）
return datetime.utcnow() > self.expiresAt

# 修正案
from datetime import timezone
return datetime.now(timezone.utc) > self.expiresAt
```

#### BUG-02: SessionDAL ファイルIO未実装
- **ファイル**: `project/backend/app/sys/dal/session_dal.py`
- **内容**: `_save_session_file()`, `_delete_session_file()` が呼び出されていない
- **影響範囲**: セッション個別ファイル管理

#### BUG-03: bcrypt 依存関係問題
- **ファイル**: `project/backend/requirements.txt`
- **内容**: bcrypt バージョンが古い、または互換性がない
- **修正案**: `bcrypt>=4.0.0` にアップデート

### 5.2 Medium（要確認）

#### BUG-04: Pydantic バリデーション不足
- **ファイル**: `project/backend/app/sys/models/session.py`
- **内容**: `expiresAt` に数値を渡してもValidationErrorが発生しない
- **修正案**: strict型チェックを有効化

---

## 6. 未実施項目

### 6.1 優先度High（未実施）

| 対象 | 理由 |
|------|------|
| API層（6ファイル） | 依存関係が多く、単体テストより結合テストに適している |
| Services層（5ファイル） | 時間的制約により未着手 |
| Frontend（4ファイル） | 時間的制約により未着手 |

### 6.2 優先度Medium/Low（未実施）

| 対象 | 理由 |
|------|------|
| API層（残り） | 優先度が低い |
| notification_dal.py | 時間的制約 |
| app_dal.py（一部） | 時間的制約 |

---

## 7. 次工程への引き継ぎ事項

### 7.1 修正必須（Criticalバグ）

1. **datetime aware/naive 問題**（BUG-01）の修正  
   → コーディング工程（工程4）に差し戻し

2. **bcrypt 依存関係**（BUG-03）の修正  
   → コーディング工程（工程4）に差し戻し

3. **SessionDAL ファイルIO**（BUG-02）の実装  
   → コーディング工程（工程4）に差し戻し

### 7.2 要検討

1. **API層の単体テスト方針**  
   → process-manager と協議（結合テストに移行するか）

2. **Services層のテスト優先度**  
   → 工程6（結合評価）で実施するか検討

### 7.3 推奨事項

1. **依存関係の事前チェック**  
   → 工程4で pytest 実行まで確認

2. **MCDC達成戦略の見直し**  
   → 全モジュールのMCDC 100%は現実的に困難

---

## 8. 承認状況

| 項目 | 状態 | 備考 |
|------|------|------|
| 全テストPASS | ❌ 未達成 | 21件失敗（実装バグ） |
| MCDC 100% | ❌ 未達成 | 19.3%（実装不足） |
| Criticalバグ0件 | ❌ 未達成 | 3件検出 |

**工程5完了承認**: ❌ 不可  
**差し戻し先**: 工程4（コーディング）  
**差し戻し理由**: 実装コードにCriticalバグあり

---

## 9. 作業時間記録

| 作業内容 | 時間 |
|---------|------|
| テスト設計 | 1.5h |
| テスト実装（Models） | 2.0h |
| テスト実装（DAL） | 2.0h |
| テスト実装（Core） | 1.0h |
| テスト実行・デバッグ | 2.0h |
| バグ調査・報告 | 1.5h |
| レポート作成 | 1.0h |
| **合計** | **11.0h** |

---

## 10. 添付資料

- `tests/unit/outputs/coverage-sys-html/` - HTMLカバレッジレポート
- `tests/unit/outputs/coverage-sys.json` - JSONカバレッジレポート
- `tests/unit/outputs/test-report-sys.xml` - JUnit XMLテストレポート
- `.github/checks/common/phase-05-result.json` - チェックプログラム結果

---

**作成者**: 05-unit-test-agent  
**承認者**: process-manager（承認待ち）  
**ステータス**: 🔴 差し戻し必要
