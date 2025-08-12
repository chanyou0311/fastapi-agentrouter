# Release Please CI Setup

This document explains how to configure release-please to trigger CI workflows on its PRs.

## Background

By default, when release-please creates PRs using the default `GITHUB_TOKEN`, GitHub doesn't trigger workflows on those PRs for security reasons. This causes required CI checks to remain in "Expected" state, blocking the PRs.

## Solution

We've implemented a two-part solution:

### 1. CI Workflow Updates

The CI workflow (`ci.yml`) has been updated to:
- Also trigger on `pull_request_target` events
- Include security checks to only run on legitimate release-please PRs
- Properly checkout the PR's code when running in `pull_request_target` mode

### 2. Personal Access Token (Optional but Recommended)

For the best experience, configure a Personal Access Token:

1. Create a new Personal Access Token (PAT) with `repo` and `workflow` permissions:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Create a token with `repo` and `workflow` scopes

2. Add the token as a repository secret:
   - Go to repository Settings → Secrets and variables → Actions
   - Create a new secret named `RELEASE_PLEASE_TOKEN`
   - Paste your PAT as the value

3. The `release-please.yml` workflow will automatically use this token if available

## How It Works

- **With PAT**: Release-please creates PRs using the PAT, which triggers CI workflows normally
- **Without PAT (Fallback)**: The CI workflow uses `pull_request_target` to run on release-please PRs created by github-actions[bot]

## Security

The `pull_request_target` trigger includes security checks:
- Only runs for PRs from `github-actions[bot]` or `release-please[bot]`
- Only runs for PRs with branch names matching the release-please pattern
- Checks out the PR's head SHA to test the actual PR code

## Verification

After setup, release-please PRs should show all required CI checks running instead of being stuck in "Expected" state.
