# DAL（データアクセス層）パターン

## 設計思想

JSONファイルを本番DBとして使いつつ、将来のRDB移行をゼロコード変更で実現する。
全データアクセスは必ず DAL インターフェース経由とし、直接ファイル操作を禁止する。

## PHP DAL インターフェース

```php
<?php
declare(strict_types=1);

interface DataStore
{
    /** コレクション内の全件取得（条件フィルタ可） */
    public function find(string $collection, array $criteria = []): array;

    /** 1件取得。見つからない場合は null */
    public function findOne(string $collection, array $criteria): ?array;

    /** 1件取得（IDで）。見つからない場合は null */
    public function findById(string $collection, string $id): ?array;

    /** 新規挿入。生成されたIDを返す */
    public function insert(string $collection, array $data): string;

    /** 更新。成功したら true */
    public function update(string $collection, string $id, array $data): bool;

    /** 削除。成功したら true */
    public function delete(string $collection, string $id): bool;
}
```

## JSON 実装（JsonDataStore）

```php
<?php
declare(strict_types=1);

class JsonDataStore implements DataStore
{
    public function __construct(
        private readonly string $basePath  // data/ ディレクトリの絶対パス
    ) {}

    private function collectionPath(string $collection): string
    {
        // パストラバーサル対策
        $safe = preg_replace('/[^a-z0-9\-_]/', '', $collection);
        return $this->basePath . '/' . $safe . '.json';
    }

    private function load(string $collection): array
    {
        $path = $this->collectionPath($collection);
        if (!file_exists($path)) return [];
        return json_decode(file_get_contents($path), true) ?? [];
    }

    private function save(string $collection, array $data): void
    {
        file_put_contents(
            $this->collectionPath($collection),
            json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE),
            LOCK_EX  // 排他ロック
        );
    }

    public function find(string $collection, array $criteria = []): array
    {
        $records = $this->load($collection);
        if (empty($criteria)) return $records;
        return array_values(array_filter($records, function ($r) use ($criteria) {
            foreach ($criteria as $k => $v) {
                if (($r[$k] ?? null) !== $v) return false;
            }
            return true;
        }));
    }

    public function findOne(string $collection, array $criteria): ?array
    {
        return $this->find($collection, $criteria)[0] ?? null;
    }

    public function findById(string $collection, string $id): ?array
    {
        return $this->findOne($collection, ['id' => $id]);
    }

    public function insert(string $collection, array $data): string
    {
        $records = $this->load($collection);
        $id = bin2hex(random_bytes(16)); // UUID相当
        $records[] = ['id' => $id, ...$data, 'createdAt' => date('c'), 'updatedAt' => date('c')];
        $this->save($collection, $records);
        return $id;
    }

    public function update(string $collection, string $id, array $data): bool
    {
        $records = $this->load($collection);
        foreach ($records as &$r) {
            if ($r['id'] === $id) {
                $r = array_merge($r, $data, ['updatedAt' => date('c')]);
                $this->save($collection, $records);
                return true;
            }
        }
        return false;
    }

    public function delete(string $collection, string $id): bool
    {
        $records = $this->load($collection);
        $filtered = array_values(array_filter($records, fn($r) => $r['id'] !== $id));
        if (count($filtered) === count($records)) return false;
        $this->save($collection, $filtered);
        return true;
    }
}
```

## コレクション（JSON ファイル）配置ルール

| パス | コレクション | 管理主体 |
|------|------------|---------|
| `src/system/data/users.json` | users | 共通基盤 |
| `src/system/data/sessions.json` | sessions | 共通基盤 |
| `src/system/data/apps.json` | apps | 共通基盤（manifest登録状態） |
| `src/apps/<name>/data/<name>.json` | アプリ固有 | 各アプリ |

## アプリ固有 DAL のインスタンス化

```php
// アプリは自分のデータディレクトリを指すDALインスタンスを使う
$appDataStore = new JsonDataStore(
    basePath: __DIR__ . '/data'  // apps/<name>/data/
);

// 共通基盤のデータには直接アクセスしない
// 必要なら共通APIを呼び出す
```
