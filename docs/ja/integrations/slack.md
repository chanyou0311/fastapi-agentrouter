# Slack統合

FastAPI AgentRouterは[Slack Bolt for Python](https://tools.slack.dev/bolt-python/)を使用したフル機能のSlack統合を提供し、AIエージェントが様々なイベントタイプを通じてSlackワークスペースと対話できるようにします。

## 機能

- **アプリメンション** - ボットがメンションされた時に応答
- **スレッドモード** - コンテキスト永続性を持つ自動スレッドベースの会話
- **ダイレクトメッセージ** - ボットへのDMを処理
- **Slashコマンド** - カスタムSlashコマンドをサポート
- **インタラクティブコンポーネント** - ボタンクリックや選択メニューを処理
- **OAuthフロー** - 内蔵OAuthインストールサポート
- **セッション管理** - スレッドごとに会話コンテキストを維持
- **遅延リスナー** - サーバーレス環境向けに最適化

## インストール

Slackエクストラを含めてインストール：

```bash
pip install fastapi-agentrouter[slack]
```

## 前提条件

1. **Slackアプリの作成**
   - [api.slack.com/apps](https://api.slack.com/apps)にアクセス
   - 「Create New App」→「From scratch」をクリック
   - アプリ名を入力してワークスペースを選択

2. **OAuth & Permissionsの設定**
   - 以下のBot Token Scopesを追加：
     - `app_mentions:read` - アプリへのメンションを読む
     - `chat:write` - アプリとしてメッセージを送信
     - `im:history` - ダイレクトメッセージを読む
     - `channels:history` - パブリックチャンネルのメッセージを読む（必要な場合）
   - ワークスペースにアプリをインストール
   - **Bot User OAuth Token**（`xoxb-`で始まる）をコピー

3. **Event Subscriptionsの設定**
   - Eventsを有効化
   - Request URLを設定: `https://your-domain.com/agent/slack/events`
   - ボットイベントをサブスクライブ：
     - `app_mention` - アプリがメンションされた時
     - `message.im` - アプリへのダイレクトメッセージ（オプション）
   - 変更を保存

4. **Interactivity & Shortcutsの設定**（インタラクティブコンポーネント使用時）
   - Interactivityを有効化
   - Request URLを設定: `https://your-domain.com/agent/slack/events`
   - 変更を保存

5. **Slashコマンドの設定**（コマンド使用時）
   - 新しいコマンドを作成
   - Request URLを設定: `https://your-domain.com/agent/slack/events`
   - 保存

6. **Signing Secretの取得**
   - Basic Informationに移動
   - **Signing Secret**をコピー

## 設定

必要な環境変数を設定：

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_SIGNING_SECRET="your-signing-secret"
```

## 基本的な使い方

```python
from fastapi import FastAPI
from fastapi_agentrouter import router, get_agent_placeholder

# エージェントの実装
class MyAgent:
    def stream_query(self, *, message: str, **kwargs):
        # メッセージを処理してレスポンスを生成
        yield f"あなたは言いました: {message}"

# FastAPIアプリを作成
app = FastAPI()

# エージェント依存関係を設定
app.dependency_overrides[get_agent_placeholder] = lambda: MyAgent()

# ルーターを含める
app.include_router(router)
```

## エンドポイント

Slack統合は単一のエンドポイントを提供：

| エンドポイント | メソッド | 説明 |
|----------|--------|-------------|
| `/agent/slack/events` | POST | すべてのSlackイベント、インタラクション、コマンドを処理 |

## イベント処理

### アプリメンション

ボットがメンションされると、自動的にスレッドを作成または継続：

```python
# ユーザーがチャンネルでボットをメンション: @YourBot 何か手伝ってください
# ボットは新しいスレッドで応答

# エージェントが受け取る内容:
# message: "@YourBot 何か手伝ってください"
# user_id: "1234567890.123456"  # コンテキスト用のスレッドタイムスタンプ
# session_id: "1234567890.123456"  # スレッドコンテキスト用にuser_idと同じ
# platform: "slack"
# channel: "C789"
# thread_ts: "1234567890.123456"
```

### スレッドメッセージ

最初のメンション後、ユーザーはボットをメンションせずに継続可能：

```python
# ユーザーがスレッドでフォローアップ: "エラー処理についてはどうですか？"
# (@YourBot メンション不要)

# エージェントが受け取る内容:
# message: "エラー処理についてはどうですか？"
# user_id: "1234567890.123456"  # 元のスレッドタイムスタンプ
# session_id: "1234567890.123456"  # 同じセッションが継続
# platform: "slack"
# channel: "C789"
# thread_ts: "1234567890.123456"
```

### ダイレクトメッセージ

ユーザーがボットにダイレクトメッセージを送信した時：

```python
# ボットは自動的にDMに応答
# ダイレクトメッセージチャンネルではメンション不要
```

## エージェントコンテキスト

エージェントは`stream_query`のkwargsで追加のSlack固有コンテキストを受け取ります：

- `platform`: 常に"slack"
- `channel`: SlackチャンネルID
- `thread_ts`: 会話コンテキストを維持するためのスレッドタイムスタンプ
- `user_id`: SlackユーザーID
- `session_id`: チャンネルとスレッドを組み合わせたユニークなセッション識別子

## レスポンス処理

統合はエージェントからの様々なレスポンス形式をサポート：

### シンプルな文字列レスポンス

```python
def stream_query(self, **kwargs):
    yield "シンプルなテキストレスポンス"
```

### 構造化レスポンス

```python
def stream_query(self, **kwargs):
    yield {
        "content": {
            "parts": [
                {"text": "レスポンスのパート1"},
                {"text": "レスポンスのパート2"}
            ]
        }
    }
```

### ストリーミングレスポンス

```python
def stream_query(self, **kwargs):
    for word in ["こんにちは", " ", "エージェント", " ", "です"]:
        yield word
```

## スレッドモード

統合はインテリジェントなスレッドベースの会話を提供：

### 自動スレッド作成
ユーザーがボットをメンションすると、レスポンスは自動的にスレッド返信として送信：
- メンションがメインチャンネルの場合は新しいスレッドを作成
- メンションが既にスレッド内の場合は既存のスレッドを継続

### コンテキスト永続性
各スレッドは独自の会話コンテキストを維持：
- スレッドタイムスタンプ（`thread_ts`）が`session_id`と`user_id`の両方として使用される
- これにより複数のユーザーが同じスレッド会話に参加可能
- エージェントはスレッド内のすべてのメッセージにわたってコンテキストを維持

### スレッド継続
スレッドでボットが一度メンションされると、ユーザーは再度メンションせずに会話を継続可能：
1. ユーザーがボットをメンション: `@YourBot Pythonについて教えて`
2. ボットがスレッドで応答
3. ユーザーは同じスレッドでフォローアップ可能: `非同期処理については？`（メンション不要）
4. ボットは完全なコンテキストで会話を継続

### 実装の詳細
- **session_id**: スレッドタイムスタンプ（例: "1234567890.123456"）
- **user_id**: 一貫したコンテキストのためスレッドタイムスタンプも使用
- 初期のボットメンションがないスレッドのメッセージは無視される
- ループを防ぐためボットメッセージは自動的にフィルタリング

## サーバーレスデプロイ

統合は遅延リスナーを使用してサーバーレス環境向けに最適化：

- 3秒以内にSlackイベントを確認応答
- 非同期でレスポンスを処理
- AWS Lambda、Google Cloud Runなどに適している

## エラー処理

エラーは適切に処理されユーザーに報告：

- 環境変数の欠落は明確なエラーメッセージを返す
- エージェントエラーはキャッチされSlackに報告される
- インポートエラーはインストール手順を提案

## Slackの無効化

Slackエンドポイントを無効化（404を返す）：

```bash
export DISABLE_SLACK=true
```

## 統合のテスト

1. **URL検証**
   ```bash
   curl -X POST http://localhost:8000/agent/slack/events \
     -H "Content-Type: application/json" \
     -d '{"type": "url_verification", "challenge": "test_challenge"}'
   ```

2. **Slackでテスト**
   - ボットをメンション: `@YourBot こんにちは`
   - ボットにダイレクトメッセージを送信
   - Slashコマンドを使用（設定済みの場合）

## セキュリティの考慮事項

- **Signing Secret**: 常に署名シークレットを使用してリクエストを検証
- **トークン保存**: トークンをバージョン管理にコミットしない
- **HTTPS**: 本番環境では常にHTTPSを使用
- **スコープ**: 必要なOAuthスコープのみをリクエスト

## トラブルシューティング

### ボットが応答しない

1. 環境変数が正しく設定されているか確認
2. SlackでEvent Subscriptions URLが検証されているか確認
3. アプリがワークスペースにインストールされているか確認
4. ボットトークンのスコープを確認

### 500エラー: slack-boltが見つからない

Slack依存関係をインストール：
```bash
pip install fastapi-agentrouter[slack]
```

### Request URL検証が失敗する

アプリが実行中で、Slackに提供した公開URLでアクセス可能であることを確認。

## 高度な設定

### カスタムセッション管理

```python
class MyAgent:
    def stream_query(self, *, session_id: str, **kwargs):
        # session_idを使用して会話状態を維持
        # フォーマット: "slack_{channel}_{thread_ts}"
        channel = session_id.split("_")[1]
        thread = session_id.split("_")[2]
        # セッションロジックを実装
        ...
```

### プラットフォーム固有のロジック

```python
class MyAgent:
    def stream_query(self, *, platform: str, **kwargs):
        if platform == "slack":
            # Slack固有のフォーマット
            yield "*太字テキスト* と _斜体テキスト_"
        else:
            # 汎用レスポンス
            yield "太字テキスト と 斜体テキスト"
```

## 関連ドキュメント

- [Slack Bolt for Python](https://tools.slack.dev/bolt-python/)
- [Slack APIドキュメント](https://api.slack.com/)
- [Slack Events API](https://api.slack.com/events-api)
- [Slack OAuth](https://api.slack.com/authentication/oauth-v2)
