# PHP コーディング規約

## 基本設定

```php
<?php
declare(strict_types=1);
```
全 PHP ファイルの先頭に必須。

## 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| クラス | PascalCase | `UserAuthService` |
| メソッド | camelCase | `findByUsername()` |
| 変数 | camelCase | `$userId` |
| 定数 | UPPER_SNAKE | `MAX_LOGIN_ATTEMPTS` |
| ファイル | クラス名.php | `UserAuthService.php` |

## PSR-12 準拠チェックポイント

- インデント: スペース4つ
- 行末: LF
- 1ファイル1クラス
- 型宣言: メソッド引数・戻り値に型を付ける

```php
public function findUser(string $username): ?array
{
    // ...
}
```

## セキュリティ規則

### XSS 防止（出力エスケープ必須）

```php
// NG
echo $userInput;

// OK
echo htmlspecialchars($userInput, ENT_QUOTES, 'UTF-8');
```

### パスワード管理

```php
// 保存
$hash = password_hash($password, PASSWORD_BCRYPT);

// 検証
if (!password_verify($inputPassword, $storedHash)) {
    throw new AuthException('Invalid credentials');
}
```

### CSRF 対策

```php
// セッションにトークン生成
$_SESSION['csrf_token'] = bin2hex(random_bytes(32));

// リクエスト検証
if (!hash_equals($_SESSION['csrf_token'], $request->getCsrfToken())) {
    throw new SecurityException('CSRF token mismatch');
}
```

### パストラバーサル対策

```php
$base = realpath('/var/websys/data/');
$path = realpath($base . '/' . $userInput);
if ($path === false || strpos($path, $base) !== 0) {
    throw new SecurityException('Invalid path');
}
```

## DAL 経由アクセスの徹底

```php
// NG: 直接ファイル操作
$data = json_decode(file_get_contents('data/users.json'), true);

// OK: DAL 経由
$user = $this->dataStore->findOne('users', ['username' => $username]);
```

## エラーハンドリング

```php
// 本番環境ではスタックトレースを露出しない
set_exception_handler(function (Throwable $e) {
    error_log($e->getMessage()); // ログ記録
    http_response_code(500);
    echo json_encode(['error' => ['code' => 'INTERNAL_ERROR', 'message' => 'Internal server error']]);
});
```
