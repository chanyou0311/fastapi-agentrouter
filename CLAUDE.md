# FastAPI AgentRouter - Claude Development Guide

This guide is for future Claude instances working on the fastapi-agentrouter project. It contains critical information about the project architecture, development workflow, and common pitfalls to avoid.

## 🚨 Critical: Documentation Updates

**ALWAYS update documentation when making code changes!** This is frequently forgotten but essential:

1. **README.md** - Update examples and API references when changing public APIs
2. **MkDocs documentation** (`docs/` directory) - Keep all pages in sync with code changes
3. **Docstrings** - Update class and function docstrings for API documentation
4. **Type hints** - Ensure all public APIs have proper type annotations

### MkDocs Structure (i18n-enabled)
```
docs/
├── en/                             # English documentation (default)
│   ├── index.md                   # Home page (mirrors README)
│   ├── getting-started/
│   │   ├── installation.md        # Installation instructions
│   │   ├── quickstart.md          # Quick start guide
│   │   └── configuration.md       # Environment variables and setup
│   ├── integrations/
│   │   └── slack.md               # Slack-specific setup and usage
│   ├── api/
│   │   ├── core.md                # Core API reference
│   │   └── integrations.md        # Platform integrations API
│   ├── examples/
│   │   ├── basic.md               # Basic usage examples
│   │   └── advanced.md            # Advanced patterns
│   ├── contributing.md            # Contribution guidelines
│   └── changelog.md               # Release notes
├── ja/                             # Japanese documentation
│   ├── index.md                   # ホームページ
│   ├── getting-started/
│   │   ├── installation.md        # インストール手順
│   │   ├── quickstart.md          # クイックスタートガイド
│   │   └── configuration.md       # 環境変数と設定
│   ├── integrations/
│   │   └── slack.md               # Slack統合ガイド
│   ├── api/
│   │   ├── core.md                # コアAPIリファレンス
│   │   └── integrations.md        # 統合API
│   ├── examples/
│   │   ├── basic.md               # 基本的なサンプル
│   │   └── advanced.md            # 高度なサンプル
│   ├── contributing.md            # コントリビューション
│   └── changelog.md               # 変更履歴
└── [future languages]/             # Additional languages can be added
```

### i18n Configuration
The documentation uses `mkdocs-static-i18n` plugin for internationalization:
- **Default language**: English (`en`)
- **Supported languages**: English, Japanese (`ja`)
- **Folder structure**: Each language has its own folder under `docs/`
- **URL structure**: `/` for English, `/ja/` for Japanese

## 🏗️ Project Architecture

### High-Level Design
The library uses a **Protocol-based dependency injection pattern** with FastAPI's modular router architecture:

1. **AgentProtocol** - Defines the interface any agent must implement
2. **Dependency Injection** - Uses FastAPI's `dependency_overrides` for agent injection
3. **Modular Integration Architecture** - Separate integration modules per platform (Slack, Discord, etc.)
4. **Pydantic Settings Configuration** - Environment-based configuration using pydantic-settings
5. **Platform-specific Dependencies** - Optional dependencies for each integration (slack-bolt, PyNaCl, etc.)

### Directory Structure
```
src/fastapi_agentrouter/
├── __init__.py                    # Main exports: router, AgentProtocol, get_agent_placeholder
├── core/
│   ├── __init__.py               # Core module exports
│   ├── dependencies.py           # Core dependency module with AgentProtocol
│   └── settings.py               # Pydantic settings configuration
├── integrations/
│   ├── __init__.py               # Integration exports
│   └── slack/
│       ├── __init__.py           # Slack integration exports
│       ├── dependencies.py       # Slack-specific dependencies
│       └── router.py             # Slack endpoints using Slack Bolt
└── routers/
    └── __init__.py               # Combines all routers with /agent prefix
```

### Key Design Decisions
- **No base classes** - Uses Protocol for maximum flexibility
- **No setup functions** - Direct router inclusion via `app.include_router()`
- **Pydantic Settings** - Type-safe configuration management
- **Platform-specific Integration** - Each platform has its own integration module
- **Slack Bolt Integration** - Uses official Slack Bolt for Python for Slack features
- **404 for disabled platforms** - Not 501, as per user feedback

## 📝 Development Commands

### Installation Options
```bash
# Basic installation
pip install fastapi-agentrouter

# With Slack support (includes slack-bolt)
pip install "fastapi-agentrouter[slack]"

# With Discord support (includes PyNaCl)
pip install "fastapi-agentrouter[discord]"

# With Vertex AI support
pip install "fastapi-agentrouter[vertexai]"

# All integrations
pip install "fastapi-agentrouter[all]"

# Development installation with uv (recommended)
uv sync --all-extras --dev
```

### Essential Commands
```bash
# Install dependencies with uv (recommended)
uv sync --all-extras --dev

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Lint and format code
ruff check src tests
ruff format src tests

# Type checking
mypy src

# Run pre-commit hooks
pre-commit run --all-files

# Build and serve documentation locally (with i18n)
mkdocs serve  # Access at http://localhost:8000 (English) and http://localhost:8000/ja/ (Japanese)

# Build documentation (builds all languages)
mkdocs build

# Test specific language
mkdocs serve --config-file mkdocs.yml  # Then navigate to /ja/ for Japanese
```

### CI/CD Pipeline
The project uses GitHub Actions for CI with these checks:
- Python 3.9, 3.10, 3.11, 3.12 compatibility
- Linting with Ruff
- Type checking with MyPy
- Test coverage reporting
- Documentation building
- Pre-commit hooks validation

## 🔑 Key Patterns

### 1. Two-Line Integration
Users can integrate the library in just 2 lines:
```python
from fastapi_agentrouter import router, get_agent_placeholder
app.dependency_overrides[get_agent_placeholder] = your_get_agent_function
app.include_router(router)
```

### 2. Agent Protocol
Any agent must implement the `stream_query` method:
```python
class AgentProtocol(Protocol):
    def stream_query(
        self, *,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> Any:
        """Stream responses from the agent."""
```

### 3. Platform Enable/Disable
Platforms can be disabled via environment variables managed through pydantic-settings:
- `DISABLE_SLACK=true` - Disable Slack integration
- `DISABLE_DISCORD=true` - Disable Discord integration (when implemented)

Configuration is managed through the `Settings` class in `core/settings.py` using pydantic-settings for type-safe environment variable handling.

Disabled endpoints return 404 with appropriate error messages.

### 4. Slack Integration with Slack Bolt
The Slack integration now uses the official Slack Bolt for Python library:
```python
# Installation with Slack support
pip install "fastapi-agentrouter[slack]"
```

This provides:
- Event handling for Slack events
- Interactive components support
- Slash commands
- OAuth flow handling (if needed)

## ⚠️ Common Pitfalls

### 1. Documentation Sync (Multi-language)
**Problem**: Code changes without updating docs
**Solution**: Always update:
- README.md examples
- MkDocs pages in `docs/en/` for English
- **IMPORTANT**: Also update `docs/ja/` for Japanese translations
- API reference documentation in both languages
- Docstrings (English only, as they're in code)

**i18n-specific notes**:
- When adding new documentation pages, create them in BOTH `en/` and `ja/` folders
- When modifying existing docs, update BOTH language versions
- Keep the same file structure in all language folders
- Japanese translations should maintain technical accuracy while being natural

### 2. Test Structure
**Problem**: Tests not matching code structure
**Solution**: Mirror the code structure:
- `tests/core/test_dependencies.py` for `src/fastapi_agentrouter/core/dependencies.py`
- `tests/core/test_settings.py` for `src/fastapi_agentrouter/core/settings.py`
- `tests/integrations/slack/test_router.py` for `src/fastapi_agentrouter/integrations/slack/router.py`

### 3. Import Style
**Problem**: Using old-style imports (`from typing import Dict`)
**Solution**: Use built-in types (`dict`, `list`, `tuple`) for Python 3.9+

### 4. Pre-commit Failures
**Problem**: CI fails on formatting/linting
**Solution**: Always run `uv run pre-commit run --all-files` before committing
- Pre-commit hooks may auto-fix files (formatting, line endings, etc.)
- Always add auto-fixed files to your commit after running pre-commit
- Keep running until no files are modified

### 5. Line Length
**Problem**: E501 line too long errors
**Solution**: Keep lines under 88 characters (Ruff configuration)

### 6. File Endings
**Problem**: CI fails with "end-of-file-fixer" pre-commit hook
**Solution**: **ALWAYS ensure all files end with exactly one newline character**
- This includes all source files (`.py`), documentation (`.md`), and configuration files
- The pre-commit hook `end-of-file-fixer` will fail if files don't end with a newline
- When editing files with Claude Code, double-check that the file ends with a newline

## 🔄 Workflow for Changes

1. **Before Starting**
   ```bash
   git pull origin main
   uv sync --all-extras --dev
   pre-commit install
   ```

2. **Make Changes**
   - Write/update code
   - Add/update tests
   - **Update documentation** (README, MkDocs)
   - Update docstrings

3. **Validate Changes**
   ```bash
   # Run tests
   pytest

   # Check formatting and linting
   ruff check src tests
   ruff format src tests

   # Type checking
   mypy src

   # Pre-commit hooks - MUST pass before committing
   uv run pre-commit run --all-files

   # Build docs to check for errors
   mkdocs build --strict
   ```

   **Important**: Handling pre-commit hook failures:
   - If pre-commit hooks fail, they may **automatically fix files** (e.g., `end-of-file-fixer`, `ruff format`)
   - When files are modified by hooks:
     1. Review the changes made by pre-commit
     2. **Add the fixed files to your commit**: `git add .`
     3. Run `uv run pre-commit run --all-files` again
     4. Repeat until all checks pass (no files modified)
   - CI will fail if these checks don't pass, so always ensure pre-commit succeeds locally

4. **Verify CI Will Pass**
   ```bash
   # Simulate CI checks locally
   uv run pre-commit run --all-files
   uv run pytest
   uv run mypy src
   uv run ruff check src tests

   # If any of these fail, fix the issues before committing
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "feat: descriptive message"
   ```

## 📚 References

### External Documentation
- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) - Pattern we follow
- [Vertex AI ADK Documentation](https://cloud.google.com/vertex-ai/docs) - For agent integration
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/) - Core pattern

### Internal Documentation
- [README.md](README.md) - User-facing documentation
- [docs/](docs/) - MkDocs source files
- [examples/](examples/) - Example implementations

## 🎯 Testing Guidelines

### Test Organization
```
tests/
├── conftest.py                    # Shared fixtures
├── test_router.py                 # Integration tests
├── core/
│   ├── test_dependencies.py      # Test core dependencies
│   └── test_settings.py          # Test pydantic settings
└── integrations/
    └── slack/
        ├── test_dependencies.py  # Test Slack dependencies
        └── test_router.py        # Slack router tests
```

### Writing Tests
- Use function-based tests with fixtures (not class-based)
- Test both enabled and disabled states for each platform
- Mock external dependencies appropriately
- Ensure 100% coverage for public APIs

## 🚀 Release Process

The project uses `release-please` for automated releases:
1. Merge PRs to main with conventional commit messages
2. Release Please creates/updates a release PR
3. Merging the release PR triggers:
   - Version bump
   - CHANGELOG update
   - PyPI publication
   - GitHub release creation

## 💡 Tips for Success

1. **Always run pre-commit** before pushing
2. **Update docs immediately** when changing APIs
3. **Update BOTH language versions** when modifying documentation (en/ and ja/)
4. **Follow existing patterns** in the codebase
5. **Write tests first** for new features
6. **Check CI status** before marking PR ready
7. **Use mock implementations** for platform endpoints
8. **Keep the integration simple** (2-line goal)
9. **Document environment variables** clearly
10. **Ensure files end with a newline** to avoid pre-commit failures
11. **Handle CI failures systematically** - See "Python Version Compatibility Testing" section above
12. **Maintain i18n consistency** - Same structure and content coverage across languages

## 🧪 Python Version Compatibility Testing

### Context
Local development typically uses Python 3.11, but CI tests against Python 3.9, 3.10, 3.11, and 3.12. Version differences can cause CI failures that pass locally.

### CI Failure Workflow for Claude Code

**IMPORTANT**: When CI fails due to Python version differences, follow this exact workflow:

#### Step 1: Identify Failed CI Jobs
```bash
# Get the latest CI run URL from the PR
gh pr checks --watch  # Shows live CI status

# Or get detailed job information
gh run list --limit 3  # List recent runs
gh run view <run-id> --json jobs --jq '.jobs[] | select(.conclusion == "failure") | {name: .name, conclusion: .conclusion}'
```

#### Step 2: View Failure Details
```bash
# Get the specific error from failed job
gh run view <run-id> --log-failed

# Or view specific job log
gh run view <run-id> --job <job-id> --log
```

#### Step 3: Reproduce Locally
```bash
# If Python 3.9 failed in CI, test locally with that version
uv run --python 3.9 pytest -xvs  # -x stops at first failure, -v verbose, -s shows print statements

# For specific test that failed
uv run --python 3.9 pytest tests/test_specific.py::TestClass::test_method -xvs
```

#### Step 4: Fix and Verify
After fixing the issue:
```bash
# Test with the previously failed version
uv run --python 3.9 pytest

# Optionally test all versions before pushing
for v in 3.9 3.10 3.11 3.12; do
    echo "Testing Python $v..."
    uv run --python $v pytest || break
done
```

#### Step 5: Push Fix and Monitor
```bash
# Push the fix
git add -A
git commit -m "fix: Python 3.9 compatibility issue"
git push

# Watch CI status
gh pr checks --watch
```

### Quick Commands Reference

```bash
# Test with specific Python version
uv run --python 3.9 pytest    # Run all tests with Python 3.9
uv run --python 3.10 pytest   # Run all tests with Python 3.10
uv run --python 3.11 pytest   # Run all tests with Python 3.11
uv run --python 3.12 pytest   # Run all tests with Python 3.12

# Check which Python versions are available locally
uv python list | grep -v "download available"

# Install missing Python version if needed
uv python install 3.9  # Install Python 3.9 if not available
```

### Best Practices

1. **Default testing**: Use `pytest` with your default Python (usually 3.11)
2. **After CI failure**: ALWAYS reproduce with the exact failed Python version
3. **Before final PR push**: Consider testing with `uv run --python 3.9 pytest` (oldest supported)
4. **Monitor CI**: Use `gh pr checks --watch` to see real-time CI status

## 🌐 i18n Maintenance Guide

### Adding New Documentation
When adding new documentation files:
1. Create the file in `docs/en/` first (English)
2. Copy the file to `docs/ja/` and translate it
3. Maintain the same file name and path structure
4. Update both versions when making changes

### Translation Guidelines
- **Technical terms**: Keep widely-used English terms (API, FastAPI, webhook, etc.)
- **Code examples**: Keep code blocks in English (comments can be translated)
- **File paths**: Keep as-is, don't translate
- **URLs**: Keep as-is
- **Consistency**: Use consistent translations for recurring terms

### Testing i18n
```bash
# Install documentation dependencies
uv sync --extra docs

# Serve documentation locally
uv run mkdocs serve

# Test English version at http://localhost:8000
# Test Japanese version at http://localhost:8000/ja/
```

### Adding New Languages
To add a new language (e.g., Chinese):
1. Add the language to `mkdocs.yml` under `plugins.i18n.languages`
2. Create a new folder `docs/zh/` with the same structure as `docs/en/`
3. Translate all documentation files
4. Test the new language locally

## 🚀 Recent Architecture Updates (v0.3.0+)

### Major Changes
1. **Modular Integration Architecture**: Moved from simple routers to a full integration module system
   - Each platform now has its own integration package
   - Better separation of concerns and maintainability

2. **Pydantic Settings Integration**: Migrated from simple environment variables to pydantic-settings
   - Type-safe configuration
   - Better validation and error messages
   - Centralized settings management in `core/settings.py`

3. **Slack Bolt Integration**: Replaced mock Slack implementation with Slack Bolt for Python
   - Full support for Slack events and interactivity
   - OAuth flow support
   - Better event handling architecture

4. **i18n Documentation**: Added multi-language support for documentation
   - English and Japanese documentation
   - MkDocs with static i18n plugin
   - Consistent documentation structure across languages

5. **Enhanced Testing**: Improved Python version compatibility testing
   - CI tests against Python 3.9, 3.10, 3.11, and 3.12
   - Better local testing commands with uv
   - Comprehensive test coverage requirements

## 🐛 Known Issues

- Codecov integration is disabled (to be enabled later)
- Documentation deployment needs GitHub Pages setup
- Example applications need expansion
- i18n: Some documentation pages (examples, API reference) are placeholders waiting for content
- Discord integration implementation pending (structure ready)

## 📮 Contact

- Repository: https://github.com/chanyou0311/fastapi-agentrouter
- Issues: https://github.com/chanyou0311/fastapi-agentrouter/issues
- Documentation: https://chanyou0311.github.io/fastapi-agentrouter
