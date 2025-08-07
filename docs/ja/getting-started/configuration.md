# 設定

FastAPI AgentRouterは設定に環境変数を使用します。すべての設定はオプションで適切なデフォルト値を持っているため、ライブラリは設定なしでそのまま動作します。

## 環境変数

このライブラリは設定管理に[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)を使用しています。環境変数を設定するか、プロジェクトルートの`.env`ファイルで設定できます。

### プラットフォーム制御

| 変数 | 型 | デフォルト | 説明 |
|----------|------|---------|-------------|
| `DISABLE_SLACK` | bool | `false` | Slack統合エンドポイントを無効化。`true`に設定すると、すべてのSlackエンドポイントは404を返します。 |
| `DISABLE_DISCORD` | bool | `false` | Discord統合エンドポイントを無効化。`true`に設定すると、すべてのDiscordエンドポイントは404を返します。 |
| `DISABLE_WEBHOOK` | bool | `false` | Webhookエンドポイントを無効化。`true`に設定すると、すべてのWebhookエンドポイントは404を返します。 |

## 設定例

### 環境変数の使用

```bash
# 特定の統合を無効化
export DISABLE_SLACK=true
export DISABLE_DISCORD=true

# アプリケーションを実行
python main.py
```

### .envファイルの使用

プロジェクトルートに`.env`ファイルを作成：

```env
# 特定の統合を無効化
DISABLE_SLACK=true
DISABLE_DISCORD=false
DISABLE_WEBHOOK=false
```

アプリケーション起動時に設定が自動的に読み込まれます。

### プログラムによる設定

設定にプログラムからアクセスして変更することもできます：

```python
from fastapi_agentrouter.core.settings import settings

# 現在の設定を確認
print(f"Slack無効化: {settings.disable_slack}")
print(f"Discord無効化: {settings.disable_discord}")
print(f"Webhook無効化: {settings.disable_webhook}")

# 設定は初期化後は読み取り専用
# オーバーライドするには、環境変数か.envファイルを使用
```

## デフォルトの動作

デフォルトでは、すべての統合が**有効**です：
- Slackエンドポイントは `/agent/slack/*` で利用可能
- Discordエンドポイントは `/agent/discord/*` で利用可能
- Webhookエンドポイントは `/agent/webhook/*` で利用可能

統合が無効化されている場合：
- 対応するエンドポイントはHTTP 404を返す
- エラーメッセージは統合が有効でないことを示す
- そのプラットフォームではエージェント処理は行われない

## 異なる設定でのテスト

テスト用に、pytestの`monkeypatch`を使用して設定をオーバーライドできます：

```python
def test_with_slack_disabled(monkeypatch):
    from fastapi_agentrouter.core.settings import settings

    # このテストのためにSlackを一時的に無効化
    monkeypatch.setattr(settings, "disable_slack", True)

    # テストコードをここに記述
    response = client.get("/agent/slack/")
    assert response.status_code == 404
```

## ブール値の解析

ライブラリはpydanticのブール値解析を使用し、様々な表現を受け入れます：
- True値: `true`, `True`, `TRUE`, `1`, `yes`, `Yes`, `YES`, `on`, `On`, `ON`
- False値: `false`, `False`, `FALSE`, `0`, `no`, `No`, `NO`, `off`, `Off`, `OFF`
- その他の値は検証エラーを発生させます

## 将来の設定オプション

将来のバージョンでは以下の追加設定オプションが追加される可能性があります：
- 認証設定
- レート制限
- ログレベル
- カスタムエンドポイントパス
- タイムアウト設定

新しい設定オプションの更新については[変更履歴](../changelog.md)を確認してください。
