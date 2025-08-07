# インストール

## 要件

- Python 3.9以上
- FastAPI 0.100.0以上

## 基本インストール

コアパッケージをインストール：

```bash
pip install fastapi-agentrouter
```

これにはコア機能とFastAPIの依存関係が含まれます。

## プラットフォーム別インストール

### Slack統合の場合

```bash
pip install "fastapi-agentrouter[slack]"
```

以下がインストールされます：
- `slack-bolt` - Slackアプリ機能用

### Discord統合の場合

```bash
pip install "fastapi-agentrouter[discord]"
```

以下がインストールされます：
- `PyNaCl` - Discord署名検証用

### Vertex AI ADKの場合

```bash
pip install "fastapi-agentrouter[vertexai]"
```

以下がインストールされます：
- `google-cloud-aiplatform` - ADKサポート付き

### すべてのプラットフォーム

```bash
pip install "fastapi-agentrouter[all]"
```

すべてのオプション依存関係をインストールします。

## 開発用インストール

開発とテスト用：

```bash
# リポジトリをクローン
git clone https://github.com/chanyou0311/fastapi-agentrouter.git
cd fastapi-agentrouter

# uv使用（推奨）
uv sync --all-extras --dev

# またはpip使用
pip install -e ".[all,dev,docs]"
```

## インストールの確認

```python
import fastapi_agentrouter
print(fastapi_agentrouter.__version__)
```

## 次のステップ

- [クイックスタートガイド](quickstart.md) - 最初のエージェント統合を作成
- [設定](configuration.md) - プラットフォーム統合の設定
