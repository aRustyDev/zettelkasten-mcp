---
id: 9DFCF576-4B99-4BB6-A705-C986CB6CE1F6
title: HTTP Transport Implementation - Phase 13: GitHub CI/CD Workflows
status: ✅ Completed
date: 2025-11-21
author: aRustyDev
---
# HTTP Transport Implementation - Phase 13: GitHub CI/CD Workflows

**Status:** ✅ COMPLETED
**Date:** 2025-11-21
**Commit:** 0418011
**Plan:** [Back to main plan](../HTTP_IMPLEMENTATION.md)

---


### Overview
Implement comprehensive GitHub Actions workflows for automated testing, linting, and Docker image builds/deployments. This ensures code quality and automates the deployment pipeline for the HTTP transport feature.

### Requirements
1. **Docker Build & Push**: Build Docker image on merge to main and push to both ghcr.io and docker.io
2. **Linting**: Run linters for Python, Dockerfile, docker-compose, YAML, and Markdown files
3. **Automated Tests**: Execute full test suite on merge events to prevent regressions
4. **Security**: Use GitHub secrets for Docker Hub credentials

### Step 13.1: Create Docker Build and Push Workflow
**File:** `.github/workflows/docker-build.yml`

**Workflow triggers:**
- Push to main branch
- Pull request to main branch (build only, no push)
- Manual workflow dispatch

**Implementation:**
```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

env:
  REGISTRY_GHCR: ghcr.io
  REGISTRY_DOCKERHUB: docker.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY_GHCR }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Log in to Docker Hub
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY_DOCKERHUB }}
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: |
            ${{ env.REGISTRY_GHCR }}/${{ env.IMAGE_NAME }}
            ${{ env.REGISTRY_DOCKERHUB }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/Dockerfile.http
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Required GitHub Secrets:**
- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

### Step 13.2: Create Linting Workflow
**File:** `.github/workflows/lint.yml`

**Linters to include:**
- **Python**: ruff (fast linter and formatter)
- **Dockerfile**: hadolint (Dockerfile linter)
- **Docker Compose**: docker-compose config validation
- **YAML**: yamllint
- **Markdown**: markdownlint

**Implementation:**
```yaml
name: Lint Code

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install ruff
        run: pip install ruff

      - name: Run ruff linter
        run: ruff check .

      - name: Run ruff formatter check
        run: ruff format --check .

  lint-dockerfile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run hadolint
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: docker/Dockerfile.http
          failure-threshold: warning

  lint-yaml:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run yamllint
        uses: ibiqlik/action-yamllint@v3
        with:
          file_or_dir: .github/workflows
          config_file: .yamllint

  lint-markdown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run markdownlint
        uses: DavidAnson/markdownlint-cli2-action@v15
        with:
          globs: '**/*.md'

  validate-docker-compose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate docker-compose
        run: docker-compose -f docker/docker-compose.http.yml config --quiet
```

### Step 13.3: Create Automated Test Workflow
**File:** `.github/workflows/test.yml`

**Tests to run:**
- Unit tests (pytest)
- Test coverage reporting
- Integration tests if applicable

**Implementation:**
```yaml
name: Run Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run pytest
        run: uv run pytest tests/ -v --tb=short --cov=src --cov-report=term --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.11'
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
          token: ${{ secrets.CODECOV_TOKEN }}

  test-results-summary:
    runs-on: ubuntu-latest
    needs: test
    if: always()
    steps:
      - name: Check test results
        run: |
          if [ "${{ needs.test.result }}" != "success" ]; then
            echo "Tests failed!"
            exit 1
          fi
          echo "All tests passed successfully!"
```

### Step 13.4: Create Linter Configuration Files

**File:** `.yamllint` (for yamllint)
```yaml
---
extends: default

rules:
  line-length:
    max: 120
    level: warning
  indentation:
    spaces: 2
  comments:
    min-spaces-from-content: 1
```

**File:** `ruff.toml` (for Python linting)
```toml
[lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "SIM"]
ignore = ["E501"]  # Line too long (handled by formatter)

[lint.per-file-ignores]
"tests/*" = ["F401", "F811"]  # Allow unused imports in tests

[format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

**File:** `.markdownlint.json` (for Markdown linting)
```json
{
  "MD013": false,
  "MD033": false,
  "MD041": false
}
```

### Step 13.5: Update pyproject.toml with Test Dependencies
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.1.0",
]
```

### Step 13.6: Create CI/CD Documentation
**File:** `.github/CICD.md`

Document:
- Required GitHub secrets setup
- Workflow descriptions
- How to run workflows manually
- Troubleshooting common CI/CD issues
- How to add Docker Hub credentials

### Step 13.7: Test Workflows Locally (Optional)
Use `act` to test GitHub Actions locally:
```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test lint workflow
act -j lint-python

# Test test workflow
act -j test
```

### Implementation Time Estimate
- **Step 13.1:** Create Docker workflow (30 minutes)
- **Step 13.2:** Create linting workflow (30 minutes)
- **Step 13.3:** Create test workflow (20 minutes)
- **Step 13.4:** Configuration files (15 minutes)
- **Step 13.5:** Update pyproject.toml (5 minutes)
- **Step 13.6:** Documentation (20 minutes)
- **Step 13.7:** Local testing (optional, 20 minutes)

**Total:** ~2-2.5 hours

### Success Criteria
- ✅ Docker images build successfully on merge to main
- ✅ Images pushed to both ghcr.io and docker.io registries
- ✅ All linters pass without errors
- ✅ All automated tests pass (103+ passing, 27 skipped, 0 failing)
- ✅ Workflows run on every pull request
- ✅ Badge status visible in README (optional)
- ✅ Documentation complete for CI/CD setup

### GitHub Secrets Setup
Users need to configure these secrets in GitHub repository settings:

**Required:**
- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token (create at hub.docker.com/settings/security)

**Optional:**
- `CODECOV_TOKEN`: Codecov token for coverage reporting

**Steps to add secrets:**
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with its value

### Commit Message Template
```
ci: Add GitHub Actions workflows for CI/CD

Implement comprehensive CI/CD pipelines for automated testing, linting,
and Docker image builds.

Workflows:
- .github/workflows/docker-build.yml: Build and push to ghcr.io and docker.io
- .github/workflows/lint.yml: Multi-language linting (Python, Dockerfile, YAML, Markdown)
- .github/workflows/test.yml: Automated test suite with coverage

Configuration:
- .yamllint: YAML linting configuration
- ruff.toml: Python linting and formatting rules
- .markdownlint.json: Markdown linting rules

Features:
- Docker images built on merge to main
- Pushed to GitHub Container Registry and Docker Hub
- Comprehensive linting across all file types
- Automated test suite runs on every PR/push
- Test coverage reporting with Codecov
- Multi-version Python testing (3.11, 3.12)

Required Secrets:
- DOCKERHUB_USERNAME: Docker Hub username
- DOCKERHUB_TOKEN: Docker Hub access token
- CODECOV_TOKEN: Optional, for coverage reporting

Documentation:
- .github/CICD.md: Complete CI/CD setup guide

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Potential Issues and Solutions

### Issue 1: Port Already in Use
**Solution:** Make port configurable (already planned) and document how to change it.

### Issue 2: CORS Preflight Failures
**Solution:** Ensure proper CORS headers and OPTIONS handling (implemented in Phase 3).

### Issue 3: Session Management
**Solution:** Use `stateless_http=true` for production deployments.

### Issue 4: Authentication
**Future Enhancement:** Add API key or OAuth support if needed for production.

---

## Future Enhancements

1. **Authentication/Authorization**
   - API key support
   - OAuth integration
   - JWT tokens

2. **Monitoring/Observability**
   - Prometheus metrics endpoint
   - Health check endpoint
   - Request logging

3. **Rate Limiting**
   - Per-client rate limits
   - DDoS protection

4. **Load Balancing**
   - Multiple server instances
   - Session affinity

5. **WebSocket Support**
   - Real-time updates
   - Bi-directional streaming

---

## References

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP HTTP Transport Guide](https://modelcontextprotocol.io/docs/tools/http-servers)
- [Starlette Documentation](https://www.starlette.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

## Notes

- FastMCP's built-in HTTP support makes this implementation straightforward
- Backward compatibility is maintained - existing STDIO usage is unaffected
- Production deployments should use `stateless_http=true` for scalability
- CORS should only be enabled when necessary (browser clients)
