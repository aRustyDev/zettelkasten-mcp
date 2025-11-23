# CI/CD Documentation

This document describes the GitHub Actions workflows for the zettelkasten-mcp project.

## Overview

The project uses three main GitHub Actions workflows:
1. **Docker Build & Push** - Builds and publishes Docker images
2. **Linting** - Runs code quality checks
3. **Testing** - Executes the automated test suite

All workflows run automatically on push/pull requests to the `main` branch.

## Workflows

### 1. Docker Build and Push (`.github/workflows/docker-build.yml`)

**Purpose:** Build Docker image and push to container registries

**Triggers:**
- Push to `main` branch
- Pull requests to `main` (build only, no push)
- Manual workflow dispatch

**What it does:**
- Checks out the repository code
- Sets up Docker Buildx for multi-platform builds
- Logs in to GitHub Container Registry (ghcr.io)
- Logs in to Docker Hub (docker.io)
- Extracts image metadata and tags
- Builds the Docker image from `docker/Dockerfile.http`
- Pushes to both registries (only on merge to main)

**Image locations:**
- `ghcr.io/<owner>/<repo>:latest`
- `docker.io/<owner>/<repo>:latest`

**Tags created:**
- `latest` - Latest build from main branch
- `main` - Main branch builds
- `sha-<commit>` - Specific commit SHA
- `pr-<number>` - Pull request builds (not pushed)

### 2. Linting (`.github/workflows/lint.yml`)

**Purpose:** Enforce code quality standards

**Triggers:**
- Push to `main` branch
- Pull requests to `main`

**Linters:**
- **Python (ruff):** Fast Python linter and formatter
  - Checks code style and common errors
  - Verifies formatting compliance
- **Dockerfile (hadolint):** Dockerfile best practices
  - Checks Dockerfile syntax
  - Warns about potential issues
- **YAML (yamllint):** YAML file validation
  - Validates workflow files
  - Checks syntax and style
- **Markdown (markdownlint):** Markdown formatting
  - Ensures consistent documentation style
- **Docker Compose:** Validates compose files
  - Checks `docker-compose.http.yml` syntax

**Configuration files:**
- `.ci/yamllint.yaml` - YAML linting rules
- `.ci/ruff.toml` - Python linting/formatting rules
- `.ci/markdownlint.json` - Markdown linting rules
- `.markdownlint-cli2.yaml` - Markdown CLI2 configuration (root, references .ci/markdownlint.json)

### 3. Testing (`.github/workflows/test.yml`)

**Purpose:** Run automated test suite

**Triggers:**
- Push to `main` branch
- Pull requests to `main`

**What it does:**
- Tests on Python 3.11 and 3.12
- Installs dependencies using `uv`
- Runs pytest with coverage reporting
- Uploads coverage to Codecov (Python 3.11 only)
- Reports test results summary

**Test requirements:**
- All tests must pass
- Currently: 103 passing, 27 skipped, 0 failing

## Required GitHub Secrets

To use all workflow features, configure these secrets in your repository:

### Setting up secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

#### Required for Docker Hub

- **`DOCKERHUB_USERNAME`**
  - Your Docker Hub username
  - Example: `myusername`

- **`DOCKERHUB_TOKEN`**
  - Docker Hub access token (NOT your password)
  - Create at: https://hub.docker.com/settings/security
  - Click "New Access Token"
  - Name it "GitHub Actions"
  - Copy the token and add as secret

#### Optional

- **`CODECOV_TOKEN`**
  - Token for Codecov coverage reporting
  - Get from: https://codecov.io
  - Sign in with GitHub
  - Add repository and copy token
  - Optional - workflow works without this

**Note:** `GITHUB_TOKEN` is automatically provided by GitHub Actions - no setup needed.

## Running Workflows Manually

### Run Docker Build

1. Go to **Actions** tab in GitHub
2. Select "Build and Push Docker Image"
3. Click "Run workflow"
4. Select branch (usually `main`)
5. Click "Run workflow"

### Run Tests

1. Go to **Actions** tab
2. Select "Run Tests"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

### Run Linting

1. Go to **Actions** tab
2. Select "Lint Code"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

## Local Testing

### Test linting locally

```bash
# Install ruff
pip install ruff

# Run Python linter
ruff check .

# Run formatter check
ruff format --check .

# Auto-fix formatting
ruff format .
```

### Test with act (GitHub Actions locally)

Install `act`:
```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

Run workflows:
```bash
# Test linting workflow
act -j lint-python

# Test test workflow
act -j test

# Test Docker build (without pushing)
act -j build-and-push
```

## Troubleshooting

### Docker build fails

**Issue:** "failed to solve with frontend dockerfile.v0"

**Solution:**
- Check `docker/Dockerfile.http` syntax
- Ensure all required files exist
- Run hadolint locally to check Dockerfile

### Linting fails

**Issue:** Ruff reports errors

**Solution:**
```bash
# View errors locally
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Tests fail

**Issue:** Tests fail in CI but pass locally

**Solution:**
- Ensure all dependencies are in `pyproject.toml`
- Check Python version (CI uses 3.11 and 3.12)
- Run tests with same command: `uv run pytest tests/ -v`

### Docker Hub push fails

**Issue:** "unauthorized: authentication required"

**Solutions:**
1. Check `DOCKERHUB_USERNAME` secret is correct
2. Regenerate `DOCKERHUB_TOKEN`:
   - Go to https://hub.docker.com/settings/security
   - Delete old token
   - Create new token
   - Update secret in GitHub

3. Ensure token has write permissions

### YAML linting fails

**Issue:** yamllint reports errors in workflow files

**Solution:**
- Check indentation (must be 2 spaces)
- Run locally: `yamllint .github/workflows`
- Fix according to `.ci/yamllint.yaml` rules

## Workflow Status Badges

Add badges to your README to show workflow status:

```markdown
![Docker Build](https://github.com/<owner>/<repo>/actions/workflows/docker-build.yml/badge.svg)
![Tests](https://github.com/<owner>/<repo>/actions/workflows/test.yml/badge.svg)
![Lint](https://github.com/<owner>/<repo>/actions/workflows/lint.yml/badge.svg)
```

## Workflow Permissions

GitHub Actions workflows need specific permissions:

- **Docker Build workflow:**
  - `contents: read` - Read repository code
  - `packages: write` - Push to GitHub Container Registry

- **Test/Lint workflows:**
  - Default permissions (read-only)

These are configured in each workflow file.

## Best Practices

1. **Always test locally first**
   - Run `ruff check .` before committing
   - Run `pytest` to ensure tests pass
   - Use `act` to test workflows locally

2. **Don't commit secrets**
   - Never put tokens in code
   - Use GitHub Secrets for sensitive data

3. **Keep workflows updated**
   - Update action versions periodically
   - Check for security updates

4. **Monitor workflow runs**
   - Check Actions tab regularly
   - Fix failing workflows quickly
   - Don't ignore warnings

5. **Use pull requests**
   - All changes go through PR
   - Workflows run on PR before merge
   - Catch issues early

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
