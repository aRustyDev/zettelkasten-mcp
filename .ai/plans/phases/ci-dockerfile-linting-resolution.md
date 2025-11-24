---
id: 16F718B1-EB5F-4568-854A-5F8B84B58306
title: Phase 3 - Dockerfile Linting Resolution
status: ✅ Completed
date: 2025-11-23
author: aRustyDev
related:
  - 689D75AC-45F1-4CA3-BB4C-AC767EB9BD63  # CI Failure Resolution Plan
  - D45D37BA-511C-42BE-A164-C8D4D40E5E07  # Phase 2: Python Linting
---

# Phase 3 - Dockerfile Linting Resolution

## Status
✅ **Completed** - 2025-11-23

## Objective
Resolve hadolint warnings in `docker/Dockerfile` to pass the lint-dockerfile CI job.

## Prerequisites
- Phase 2 (Python Linting) completed
- Docker installed locally
- hadolint Docker image available

## Initial Error Summary
```bash
docker run --rm -i hadolint/hadolint < docker/Dockerfile
```

**Result**: Exit code 1 - 2 warnings (failure-threshold: warning in CI)

```
-:27 DL3008 warning: Pin versions in apt get install.
     Instead of `apt-get install <package>`
     use `apt-get install <package>=<version>`

-:33 DL3013 warning: Pin versions in pip.
     Instead of `pip install <package>`
     use `pip install <package>==<version>`
```

## Root Cause Analysis

### Issue 1: DL3008 - Unpinned APT Package
**File**: `docker/Dockerfile`
**Line**: 27-28

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

**Problem**: Package `git` installed without version constraint
**Impact**:
- Builds are not reproducible
- Different build times may get different versions
- Security updates could introduce breaking changes

**Rationale for warning**: Dockerfile best practice for production images

### Issue 2: DL3013 - Unpinned PIP Package
**File**: `docker/Dockerfile`
**Line**: 33

```dockerfile
RUN pip install --no-cache-dir uv
```

**Problem**: Package `uv` installed without version constraint
**Impact**:
- UV updates could break the build
- Different environments may have different behavior
- Difficult to debug version-specific issues

## Resolution Steps

### Step 1: Determine Appropriate Versions

#### Git Version Selection
```bash
# Check available versions in python:3.12-slim base image
docker run --rm python:3.12-slim bash -c "apt-cache madison git | head -5"
```

Selected version: `1:2.39.*`
- Rationale:
  - Wildcard allows patch updates (security fixes)
  - Major.minor version locked for compatibility
  - Available in Debian bookworm (python:3.12-slim base)

#### UV Version Selection
```bash
# Check current UV version in project
uv --version
```

Result: `uv 0.5.15`

Selected version: `0.5.15`
- Rationale:
  - Matches version used in development
  - Known to work with current uv.lock file
  - Explicit version ensures reproducibility

### Step 2: Update Dockerfile

**File**: `docker/Dockerfile`

```dockerfile
# BEFORE
# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN pip install --no-cache-dir uv

# AFTER
# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git=1:2.39.* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN pip install --no-cache-dir uv==0.5.15
```

### Step 3: Verify Fix Locally

```bash
docker run --rm -i hadolint/hadolint < docker/Dockerfile
```

**Result**: ✅ No warnings or errors!

### Step 4: Test Docker Build

```bash
docker build -f docker/Dockerfile -t zettelkasten-mcp:test .
```

**Result**: ✅ Build successful with pinned versions

Verified:
- Git installation works with version constraint
- UV installation works with exact version
- Application builds and runs correctly

## Files Modified

### Docker Files (1 file)
- `docker/Dockerfile`
  - Line 28: Added git version constraint `=1:2.39.*`
  - Line 33: Added uv version constraint `==0.5.15`

## Commit

```
commit bd7aa04e1bc757297c60bbf471bcc3b09169f264
Author: aRustyDev

fix: Resolve remaining CI linting failures

Fixed Dockerfile hadolint warnings:
- Pinned git version to 1:2.39.*
- Pinned uv version to 0.5.15
- hadolint now passes with no warnings
```

## Verification

### Local Testing
```bash
# Lint check
docker run --rm -i hadolint/hadolint < docker/Dockerfile
✅ No errors

# Build check
docker build -f docker/Dockerfile -t test .
✅ Build successful

# Run check
docker run --rm test --help
✅ Application runs
```

### CI Testing
After push, lint-dockerfile job: ✅ Passed

## Configuration Details

### Workflow Configuration
**File**: `.github/workflows/lint.yml`
```yaml
- name: Run hadolint
  uses: hadolint/hadolint-action@v3.1.0
  with:
    dockerfile: docker/Dockerfile
    failure-threshold: warning  # Treats warnings as failures
```

This explains why warnings blocked the CI.

## Best Practices Applied

### Version Pinning Strategies

1. **Patch-level wildcards** (e.g., `1:2.39.*`):
   - ✅ Use for: System packages from stable repos
   - ✅ Allows: Security patches
   - ✅ Prevents: Breaking changes

2. **Exact versions** (e.g., `==0.5.15`):
   - ✅ Use for: Python packages
   - ✅ Ensures: Reproducible builds
   - ✅ Prevents: Unexpected updates

3. **When to update**:
   - Security vulnerabilities
   - New features needed
   - Explicit decision, not automatic

### Dockerfile Linting Rules

Common hadolint rules for production:
- **DL3008**: Pin apt package versions
- **DL3013**: Pin pip package versions
- **DL3015**: Avoid `apt-get upgrade` (use newer base image)
- **DL3018**: Pin apk package versions (Alpine)
- **DL3025**: Use JSON format for CMD/ENTRYPOINT

## Key Learnings

1. **Warnings matter**: Configure failure-threshold based on environment
2. **Version strategy**: Choose appropriate pinning granularity
3. **Base image matters**: Version availability depends on base image
4. **Test locally**: hadolint Docker image exactly matches CI
5. **Document choices**: Record why specific versions were selected

## Common Patterns

### Pattern: System Package Version Pinning
```dockerfile
# ❌ Bad - No version
RUN apt-get install -y package-name

# ⚠️  Okay - Full version (too specific)
RUN apt-get install -y package-name=1.2.3-4

# ✅ Best - Major.minor with patch wildcard
RUN apt-get install -y package-name=1.2.*
```

### Pattern: Python Package Version Pinning
```dockerfile
# ❌ Bad - No version
RUN pip install package-name

# ⚠️  Okay - Major version only (too loose)
RUN pip install package-name>=1.0.0

# ✅ Best - Exact version
RUN pip install package-name==1.2.3
```

## Duration
Approximately 30 minutes including verification

## Related Issues
- Resolved Dockerfile linting blocking CI merge
- Improved build reproducibility
- Established version pinning standards

---

**Phase Status**: ✅ Completed
**Previous Phase**: [Python Linting Resolution](ci-python-linting-resolution.md)
**Next Phase**: [Markdown Linting Resolution](ci-markdown-linting-resolution.md)
