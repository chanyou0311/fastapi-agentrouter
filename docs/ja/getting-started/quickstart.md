# クイックスタートガイド

このガイドでは、AIエージェントをFastAPIと数分で統合する方法を説明します。

## 基本的な統合

### ステップ1: エージェントの作成

まず、`stream_query`メソッドを実装したエージェントを作成します：

```python
class SimpleAgent:
    def stream_query(self, *, message: str, **kwargs):
        """メッセージを処理してレスポンスをストリーミング"""
        # エージェントのロジックをここに記述
        yield f"Echo: {message}"
```

### ステップ2: FastAPIとの統合

```python
from fastapi import FastAPI
from fastapi_agentrouter import get_agent_placeholder, router

def get_agent():
    return SimpleAgent()

app = FastAPI()

# エージェントでルーターを追加 - 2行だけ！
app.dependency_overrides[get_agent_placeholder] = get_agent
app.include_router(router)
```

### ステップ3: エージェントのテスト

サーバーを起動：

```bash
uvicorn main:app --reload
```

Webhookエンドポイントをテスト：

```bash
curl -X POST "http://localhost:8000/agent/webhook" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, agent!"}'
```

## Vertex AI ADKを使用する場合

### ステップ1: エージェントの定義

```python
from vertexai import Agent
from vertexai.preview import reasoning_engines

# エージェント用のツール（関数）を定義
def get_weather(city: str) -> dict:
    """都市の天気情報を取得"""
    return {
        "city": city,
        "temperature": 25,
        "condition": "sunny"
    }

# エージェントを作成
agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash-lite",
    description="便利な天気アシスタント",
    instruction="天気情報についてユーザーを支援します",
    tools=[get_weather]
)
```

### ステップ2: ADKアプリの作成と統合

```python
from fastapi import FastAPI
from fastapi_agentrouter import get_agent_placeholder, router

def get_adk_app():
    return reasoning_engines.AdkApp(
        agent=agent,
        enable_tracing=True  # オプション: トレーシングを有効化
    )

app = FastAPI()

# FastAPIと統合 - 2行だけ！
app.dependency_overrides[get_agent_placeholder] = get_adk_app
app.include_router(router)
```

### ステップ3: 環境の設定

Google Cloud認証情報を設定：

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

## プラットフォーム設定

プラットフォームを選択的に有効化/無効化できます：

```python
app.dependency_overrides[get_agent_placeholder] = get_agent
app.include_router(router)
```

## プラットフォーム統合

### Slack統合

1. Slack署名シークレットを設定：
```bash
export SLACK_SIGNING_SECRET="your-slack-signing-secret"
```

2. Slackアプリを設定：
   - イベントサブスクリプションURL: `https://your-domain.com/agent/slack/events`
   - SlashコマンドURL: `https://your-domain.com/agent/slack/events`

3. エージェントがSlackで利用可能になります！

### Discord統合

1. Discord公開鍵を設定：
```bash
export DISCORD_PUBLIC_KEY="your-discord-public-key"
```

2. Discordアプリを設定：
   - インタラクションエンドポイントURL: `https://your-domain.com/agent/discord/interactions`

3. エージェントがDiscordで利用可能になります！

## 完全なサンプル

すべての機能を含む完全なサンプル：

```python
from fastapi import FastAPI
from fastapi_agentrouter import get_agent_placeholder, router
from vertexai import Agent
from vertexai.preview import reasoning_engines
import os

# 環境変数を設定
os.environ["SLACK_SIGNING_SECRET"] = "your-secret"
os.environ["DISCORD_PUBLIC_KEY"] = "your-key"

# エージェントを作成
def search_web(query: str) -> dict:
    """ウェブで情報を検索"""
    return {"results": f"検索結果: {query}"}

agent = Agent(
    name="assistant",
    model="gemini-2.5-flash-lite",
    tools=[search_web]
)

def get_agent():
    return reasoning_engines.AdkApp(agent=agent)

# FastAPIアプリを作成
app = FastAPI(title="My Agent API")

# エージェントルーターを追加 - 2行だけ！
app.dependency_overrides[get_agent_placeholder] = get_agent
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 次のステップ

- [設定ガイド](configuration.md) - 詳細な設定オプション
- [APIリファレンス](../api/core.md) - 完全なAPIドキュメント
- [サンプル](../examples/basic.md) - より多くのサンプルとユースケース
