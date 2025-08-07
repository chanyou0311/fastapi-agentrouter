# FastAPI AgentRouter - Claude Development Guide

This guide is for future Claude instances working on the fastapi-agentrouter project. It contains critical information about the project architecture, development workflow, and common pitfalls to avoid.

## 🚨 Critical: Documentation Updates

**ALWAYS update documentation when making code changes!** This is frequently forgotten but essential:

1. **README.md** - Update examples and API references when changing public APIs
2. **MkDocs documentation** (`docs/` directory) - Keep all pages in sync with code changes
3. **Docstrings** - Update class and function docstrings for API documentation
4. **Type hints** - Ensure all public APIs have proper type annotations

### MkDocs Structure
```
docs/
├── index.md                        # Home page (mirrors README)
├── getting-started/
│   ├── installation.md            # Installation instructions
│   ├── quickstart.md              # Quick start guide
│   └── configuration.md           # Environment variables and setup
├── integrations/
│   └── slack.md                   # Slack-specific setup and usage
├── api/
│   ├── core.md                    # Core API reference
│   └── integrations.md            # Platform integrations API
├── examples/
│   ├── basic.md                   # Basic usage examples
│   └── advanced.md                # Advanced patterns
├── contributing.md                # Contribution guidelines
└── changelog.md                   # Release notes
```

## 🏗️ Project Architecture

### High-Level Design
The library uses a **Protocol-based dependency injection pattern** with FastAPI's modular router architecture:

1. **AgentProtocol** - Defines the interface any agent must implement
2. **Dependency Injection** - Uses FastAPI's `dependency_overrides` for agent injection
3. **Modular Routers** - Separate router modules per platform (Slack)
4. **Environment-based Configuration** - Platforms can be disabled via environment variables

### Directory Structure
```
src/fastapi_agentrouter/
├── __init__.py                    # Main exports: router, AgentProtocol, get_agent_placeholder
├── dependencies.py                # Core dependency module with AgentProtocol
├── routers/
│   ├── __init__.py               # Combines all routers with /agent prefix
│   └── slack.py                  # Slack endpoints (mock implementation)
```

### Key Design Decisions
- **No base classes** - Uses Protocol for maximum flexibility
- **No setup functions** - Direct router inclusion via `app.include_router()`
- **Mock implementations** - Endpoints return simple status responses
- **404 for disabled platforms** - Not 501, as per user feedback

## 📝 Development Commands

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

# Build and serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
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
Platforms can be disabled via environment variables:
- `DISABLE_SLACK=true`

Disabled endpoints return 404 with appropriate error messages.

## ⚠️ Common Pitfalls

### 1. Documentation Sync
**Problem**: Code changes without updating docs
**Solution**: Always update:
- README.md examples
- MkDocs pages in `docs/`
- API reference documentation
- Docstrings

### 2. Test Structure
**Problem**: Tests not matching code structure
**Solution**: Mirror the code structure:
- `tests/routers/test_slack.py` for `src/fastapi_agentrouter/routers/slack.py`

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
├── test_dependencies.py           # Test dependencies module
├── test_router.py                 # Integration tests
└── routers/
    └── test_slack.py             # Slack router tests
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
3. **Follow existing patterns** in the codebase
4. **Write tests first** for new features
5. **Check CI status** before marking PR ready
6. **Use mock implementations** for platform endpoints
7. **Keep the integration simple** (2-line goal)
8. **Document environment variables** clearly
9. **Ensure files end with a newline** to avoid pre-commit failures
10. **Handle CI failures systematically** - See "Python Version Compatibility Testing" section above

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

## 🐛 Known Issues

- Codecov integration is disabled (to be enabled later)
- Documentation deployment needs GitHub Pages setup
- Example applications need expansion

## 📮 Contact

- Repository: https://github.com/chanyou0311/fastapi-agentrouter
- Issues: https://github.com/chanyou0311/fastapi-agentrouter/issues
- Documentation: https://chanyou0311.github.io/fastapi-agentrouter
