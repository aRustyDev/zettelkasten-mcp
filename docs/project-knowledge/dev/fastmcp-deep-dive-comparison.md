---
id: 6E8A9F2C-1D4B-4E5A-9C3E-7F4B2D1A8E6C
title: FastMCP Deep Dive - Option A vs Option B Comparison
status: ✅ Analysis Complete
date: 2025-11-22
author: aRustyDev
related:
  - 82D15E44-AA64-4624-AE3E-3C2E5BAC97B3  # Doc: Streamable HTTP Implementation Options
  - FF1F3BCB-1328-41E3-9B7C-60946539384A  # Doc: MCP HTTP Transport Protocols
  - 2F7850D8-3E51-456C-AE60-C70BAF323BFB  # Plan: Streamable HTTP Implementation
---

# FastMCP Deep Dive: Option A vs Option B Comparison

**Research Date:** 2025-11-22
**Author:** aRustyDev
**Status:** ✅ Complete

---

## Executive Summary

This document provides an in-depth comparison between **Option A** (Upgrading MCP SDK 1.6.0 → 1.22.0) and **Option B** (Migrating to FastMCP 2.0 standalone package) for implementing Streamable HTTP support in the Zettelkasten MCP server.

**Key Finding:** Both options support Streamable HTTP, but they represent fundamentally different approaches:
- **Option A**: Stay with official Anthropic SDK, minimal migration
- **Option B**: Adopt community-driven framework with advanced features

**Critical Context:**
- **Current State**: `mcp[cli]==1.6.0` (FastMCP 1.0 embedded)
- **Option A Target**: `mcp[cli]==1.22.0` (FastMCP 1.0 updated)
- **Option B Target**: `fastmcp==2.13.0` (standalone package)
- **Project Goal**: Fork intended as upstream contribution (PR to main repo)

---

## Table of Contents

1. [What is FastMCP 2.0?](#what-is-fastmcp-20)
2. [Feature Comparison Matrix](#feature-comparison-matrix)
3. [Support & Maintenance](#support--maintenance)
4. [Similarity to Current Architecture](#similarity-to-current-architecture)
5. [Exclusive Features Analysis](#exclusive-features-analysis)
6. [Database Integration](#database-integration)
7. [Migration Complexity](#migration-complexity)
8. [Recommendation](#recommendation)

---

## What is FastMCP 2.0?

### The Fork Story

**FastMCP 1.0** (2024):
- Created by Jeremiah Lowin (jlowin) as "the fast, Pythonic way to build MCP servers"
- Became so popular it was adopted into the official MCP Python SDK
- Lives at `mcp.server.fastmcp` in the official SDK
- Focused on simplicity: decorator-based server creation

**FastMCP 2.0** (2025):
- **Major Release Date**: April 16, 2025
- **Philosophical Shift**: "Reimagines FastMCP as a full ecosystem platform"
- Forked from FastMCP 1.0 to move faster than SDK governance allows
- Standalone package: `pip install fastmcp` (separate from `mcp` package)
- **Growth**: 10k+ GitHub stars in 6 weeks post-relaunch
- **Current Version**: 2.13.0 (October 25, 2025)

### Why the New Major Release?

FastMCP 2.0 was created to:
1. **Move Faster**: SDK governance requires consensus; FastMCP 2.0 can iterate rapidly
2. **Add Enterprise Features**: Auth, deployment, composition patterns
3. **Build an Ecosystem**: FastMCP Cloud, OpenAPI integration, proxy servers
4. **Pragmatic Breaking Changes**: Willing to break compatibility to improve DX

### New Features in FastMCP 2.0

**Major Additions (Not in SDK 1.22.0):**

#### 🔐 Authentication & Security (v2.6+)
- **OAuth 2.1 Support**: WorkOS, GitHub, Google, Azure, AWS Cognito, Auth0
- **OAuth Proxy Pattern**: Bridge providers without Dynamic Client Registration
- **JWT Validation**: Enterprise-grade token verification
- **Bearer Token Auth**: Simple API key authentication
- **Consent Screens**: Prevent authorization bypass attacks

#### 💾 State Management (v2.11+, v2.13)
- **Pluggable Storage Backends**:
  - Filesystem (encrypted by default)
  - Redis, DynamoDB, Elasticsearch
  - MongoDB, Memcached, RocksDB
- **OAuth Token Persistence**: Survive restarts
- **Response Caching Middleware**: TTL-based caching

#### 🔧 Advanced Features
- **MCP Middleware System** (v2.9): Intercept operations (auth, logging, rate limiting)
- **Tool Transformation** (v2.8): Wrap tools to rename, rewrite descriptions
- **Component Control**: Tag-based filtering, enable/disable tools dynamically
- **Server Proxying**: Transport bridging (stdio ↔ SSE ↔ HTTP)
- **FastAPI Integration**: Generate MCP from OpenAPI specs
- **In-Memory Testing**: Deterministic testing without network
- **Elicitation Support** (v2.10): Human-in-the-loop workflows
- **Output Schemas**: Structured tool outputs

#### 🚀 Developer Experience
- **FastMCP CLI**: Enhanced tooling (`fastmcp install`, `fastmcp run`)
- **FastMCP Cloud**: Managed deployment platform (free beta)
- **Declarative JSON Config** (v2.12): `fastmcp.json` for portable config
- **Server Lifespans**: Proper init/cleanup hooks
- **Pydantic Validation**: Better type safety

---

## Feature Comparison Matrix

| Feature | Option A: MCP SDK 1.22.0 | Option B: FastMCP 2.0 | Notes |
|---------|-------------------------|----------------------|-------|
| **Core Protocol** |
| STDIO Transport | ✅ Yes | ✅ Yes | Both support |
| Streamable HTTP | ✅ Yes (v1.8.0+) | ✅ Yes (v2.3.0+) | Both support |
| Legacy SSE | ✅ Yes | ✅ Yes (deprecated) | Both support |
| MCP Protocol Compliance | ✅ Official Reference | ✅ Full Compliance | SDK is canonical |
| **Decorator API** |
| `@mcp.tool` | ✅ Yes | ✅ Yes | Identical |
| `@mcp.resource` | ✅ Yes | ✅ Yes | Identical |
| `@mcp.prompt` | ✅ Yes | ✅ Yes | Identical |
| Context API | ✅ Basic | ✅ Enhanced | v2.0 has more methods |
| **Authentication** |
| OAuth 2.1 | ❌ No | ✅ Yes (10+ providers) | **Exclusive to 2.0** |
| Bearer Token | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| JWT Validation | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| OAuth Proxy | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| **State & Storage** |
| In-Memory State | ✅ Manual | ✅ Built-in | 2.0 provides dict API |
| Persistent Storage | ❌ No | ✅ Yes (Redis, DynamoDB, etc.) | **Exclusive to 2.0** |
| Response Caching | ❌ No | ✅ Yes (middleware) | **Exclusive to 2.0** |
| **Advanced Features** |
| Middleware System | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| Tool Transformation | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| Tag-Based Filtering | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| Server Proxying | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| OpenAPI Generation | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| Elicitation | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| **Integrations** |
| FastAPI Integration | ⚠️ Manual | ✅ First-class | 2.0 has helpers |
| OpenAPI Parser | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| Cloud Deployment | ❌ No | ✅ FastMCP Cloud | **Exclusive to 2.0** |
| **Testing** |
| In-Memory Testing | ❌ No | ✅ Yes | **Exclusive to 2.0** |
| **Developer Tools** |
| CLI Tooling | ⚠️ Basic (`mcp`) | ✅ Enhanced (`fastmcp`) | 2.0 has more commands |
| Config Format | ⚠️ JSON only | ✅ JSON + `fastmcp.json` | 2.0 more portable |
| **Documentation** |
| Quality | ✅ Good (official) | ✅ Excellent | 2.0 more examples |
| Examples | ✅ Adequate | ✅ Extensive | 2.0 has more |

---

## Support & Maintenance

### Option A: MCP SDK 1.22.0

**Official Support:**
- **Maintainer**: Anthropic (official)
- **Repository**: https://github.com/modelcontextprotocol/python-sdk
- **Stars**: 20.2k ⭐
- **Release Cadence**: Stable, conservative
- **Breaking Changes**: Rare, well-documented
- **Bug Fixes**: Prioritized for protocol compliance
- **Community**: Large, diverse
- **Longevity**: ✅ Long-term (backed by Anthropic)

**Pros:**
- ✅ Official Anthropic support
- ✅ Canonical MCP implementation
- ✅ Conservative, stable releases
- ✅ Best for upstream contributions (PRs to main repo)

**Cons:**
- ❌ Slower feature development (governance overhead)
- ❌ Less opinionated (minimal batteries-included)
- ❌ Fewer enterprise features

### Option B: FastMCP 2.0

**Community-Driven Support:**
- **Maintainer**: Jeremiah Lowin (@jlowin) + community
- **Repository**: https://github.com/jlowin/fastmcp
- **Stars**: 10k+ ⭐ (in 6 weeks!)
- **Release Cadence**: Fast, frequent (minor versions may break)
- **Breaking Changes**: Common in minor versions (pragmatic)
- **Bug Fixes**: Fast iteration
- **Community**: Growing, enthusiastic
- **Longevity**: ⚠️ Dependent on maintainer(s)

**Pros:**
- ✅ Rapid feature development
- ✅ Enterprise features (auth, storage, middleware)
- ✅ FastMCP Cloud deployment platform
- ✅ Extensive documentation and examples

**Cons:**
- ❌ Not official Anthropic (third-party)
- ❌ Breaking changes in minor versions
- ❌ Fork divergence risk from official SDK
- ❌ May not be accepted in upstream PRs

---

## Similarity to Current Architecture

### Current Project Structure

```python
# Current: src/zettelkasten_mcp/server/mcp_server.py
from mcp.server.fastmcp import Context, FastMCP

class ZettelkastenMcpServer:
    def __init__(self):
        self.mcp = FastMCP(
            config.server_name,
            version=config.server_version,
            json_response=config.json_response,
        )
        self.zettel_service = ZettelService()  # SQLAlchemy
        self.search_service = SearchService(self.zettel_service)

    @mcp.tool
    def zk_create_note(self, title: str, content: str) -> str:
        # ... implementation
```

### Option A: Upgrade to MCP SDK 1.22.0

**Code Changes Required:**

```python
# Minimal changes - mostly the same!
from mcp.server.fastmcp import Context, FastMCP

class ZettelkastenMcpServer:
    def __init__(self):
        self.mcp = FastMCP(
            config.server_name,
            version=config.server_version,
            json_response=config.json_response,
            stateless_http=True,  # NEW: Optimize for Streamable HTTP
        )
        # Everything else stays the same!

# Run with Streamable HTTP
await mcp.run_streamable_http_async(
    host=config.http_host,
    port=config.http_port,
)
```

**Similarity Score: 95%**
- ✅ Same import path
- ✅ Same decorator API
- ✅ Same initialization pattern
- ✅ Existing service layer (SQLAlchemy) unchanged
- ✅ Minimal config changes

### Option B: Migrate to FastMCP 2.0

**Code Changes Required:**

```python
# Import path changes
from fastmcp import Context, FastMCP  # Different package!

class ZettelkastenMcpServer:
    def __init__(self):
        self.mcp = FastMCP(
            config.server_name,
            version=config.server_version,
            json_response=config.json_response,
            # Could add new 2.0 features:
            # auth=WorkOSProvider(...),  # If desired
            # storage=RedisStorage(...),  # If desired
        )
        # Service layer unchanged!

# Run with Streamable HTTP (same as 1.0)
await mcp.run_async(
    transport="http",  # or "streamable-http"
    host=config.http_host,
    port=config.http_port,
)
```

**Similarity Score: 90%**
- ⚠️ Import path changes (global find/replace)
- ✅ Same decorator API
- ✅ Same initialization pattern (with optional new features)
- ✅ Existing service layer (SQLAlchemy) unchanged
- ⚠️ Dependency change (`mcp` → `fastmcp`)

---

## Exclusive Features Analysis

### Features ONLY in Option A (MCP SDK 1.22.0)

**1. Official Anthropic Backing**
- Canonical MCP implementation
- Guaranteed long-term support
- Best for upstream contributions

**2. Conservative Stability**
- Breaking changes extremely rare
- Safer for production (fewer surprises)

**That's it!** MCP SDK 1.22.0 is a minimal, stable implementation.

### Features ONLY in Option B (FastMCP 2.0)

**1. Enterprise Authentication** 🔐
- **10+ OAuth Providers**: WorkOS, GitHub, Google, Azure, AWS Cognito, Auth0, Descope, Scalekit
- **OAuth Proxy**: Bridge providers without DCR
- **JWT Validation**: Enterprise-grade token verification
- **Bearer Tokens**: Simple API key auth

**Use Case for This Project:**
- ⚠️ Not needed now (no auth requirements)
- ✅ Future-proofing if multi-user access needed

**2. Persistent State & Caching** 💾
- **Storage Backends**: Redis, DynamoDB, Elasticsearch, Filesystem (encrypted)
- **OAuth Token Persistence**: Survive restarts
- **Response Caching**: TTL-based middleware

**Use Case for This Project:**
- ✅ **Potentially Useful**: Could cache expensive search results
- ✅ **SQLAlchemy Integration**: FastMCP 2.0 doesn't interfere with existing DB layer
- ⚠️ Not critical (current implementation works fine)

**3. Middleware System** 🔧
- Intercept tool calls
- Add logging, rate limiting, custom business logic
- **Use Case**: Could add audit logging for note modifications

**4. Tool Transformation** ✨
- Wrap tools to rename arguments
- Rewrite descriptions for LLM-friendliness
- **Use Case**: ⚠️ Not needed (tools are already well-designed)

**5. Server Proxying** 🔌
- Transport bridging (stdio ↔ SSE ↔ HTTP)
- **Use Case**: ⚠️ Not needed (single server deployment)

**6. OpenAPI Generation** 📋
- Generate MCP server from FastAPI apps
- **Use Case**: ❌ Not relevant (not converting REST API)

**7. FastMCP Cloud** ☁️
- Managed deployment platform (free beta)
- **Use Case**: ✅ **Potentially Useful** for easy deployment

**8. In-Memory Testing** 🧪
- Deterministic testing without network
- **Use Case**: ✅ **Very Useful** for test suite improvements

**9. Enhanced CLI & DX** 🛠️
- `fastmcp install claude-code`, `fastmcp run`, etc.
- **Use Case**: ✅ **Nice-to-Have** for development

---

## Database Integration

### Current Project: SQLAlchemy

```python
# Existing architecture
class ZettelService:
    def __init__(self):
        self.engine = create_engine(config.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
```

### Option A: MCP SDK 1.22.0

**Integration Approach:**
- ✅ **No Change Required**: SQLAlchemy works as-is
- ✅ **Clean Separation**: Service layer independent of MCP layer
- ✅ **Proven Pattern**: Current implementation works

**Example:**
```python
from mcp.server.fastmcp import FastMCP

class ZettelkastenMcpServer:
    def __init__(self):
        self.mcp = FastMCP(...)
        self.zettel_service = ZettelService()  # SQLAlchemy service

    @self.mcp.tool
    def zk_create_note(self, title: str, content: str) -> str:
        return self.zettel_service.create_note(title, content)
```

**Complexity: ⭐ Very Low**

### Option B: FastMCP 2.0

**Integration Approach:**
- ✅ **No Change Required**: SQLAlchemy works as-is
- ✅ **Optional Enhancement**: Could use FastMCP storage for caching
- ✅ **Same Pattern**: Service layer remains independent

**Example (Same as Option A):**
```python
from fastmcp import FastMCP

class ZettelkastenMcpServer:
    def __init__(self):
        self.mcp = FastMCP(...)
        self.zettel_service = ZettelService()  # SQLAlchemy service - unchanged!

    @self.mcp.tool
    def zk_create_note(self, title: str, content: str) -> str:
        return self.zettel_service.create_note(title, content)
```

**Optional Enhancement (FastMCP 2.0 only):**
```python
from fastmcp import FastMCP
from fastmcp.server.storage import RedisStorage

class ZettelkastenMcpServer:
    def __init__(self):
        # Optional: Use FastMCP storage for caching search results
        self.mcp = FastMCP(
            config.server_name,
            storage=RedisStorage(url="redis://localhost"),  # NEW
        )
        self.zettel_service = ZettelService()  # SQLAlchemy unchanged

    @self.mcp.tool
    async def zk_search(self, query: str) -> str:
        # Optional: Cache expensive searches
        cache_key = f"search:{query}"
        if cached := await self.mcp.storage.get(cache_key):
            return cached

        results = self.search_service.search(query)
        await self.mcp.storage.set(cache_key, results, ttl=300)
        return results
```

**Complexity: ⭐ Very Low (optional features add complexity)**

### Database Integration Winner: TIE ✅

Both options work identically with SQLAlchemy. FastMCP 2.0 offers **optional** caching enhancements, but they're not required.

---

## Migration Complexity

### Option A: Upgrade MCP SDK (1.6.0 → 1.22.0)

**Changes Required:**

1. **Update Dependencies** (5 minutes)
```toml
# pyproject.toml
dependencies = [
    "mcp[cli]>=1.22.0",  # Was: >=1.2.0
]
```

2. **Code Changes** (30 minutes)
```python
# Add stateless_http parameter
self.mcp = FastMCP(
    config.server_name,
    version=config.server_version,
    json_response=config.json_response,
    stateless_http=True,  # NEW
)

# Update run method (if using HTTP)
# Before:
mcp.run(transport="sse", host="0.0.0.0", port=8000)

# After:
mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

3. **Testing** (3-4 hours)
- Run existing test suite
- Test STDIO transport (backward compat)
- Test Streamable HTTP with Zed
- Test with `npx mcp-remote` (backward compat)

4. **Docker Updates** (30 minutes)
- Update `pyproject.toml` version
- Rebuild image
- Test deployment

**Total Estimate: 4-6 hours**

**Breaking Change Risk: 🟡 Medium**
- 16 minor versions (1.6.0 → 1.22.0)
- Need to review changelog for breaking changes
- FastMCP 1.0 API generally stable

### Option B: Migrate to FastMCP 2.0

**Changes Required:**

1. **Update Dependencies** (5 minutes)
```toml
# pyproject.toml
dependencies = [
    # "mcp[cli]>=1.2.0",  # REMOVE
    "fastmcp>=2.13.0",  # ADD
    # ... rest unchanged
]
```

2. **Import Changes** (30 minutes)
```python
# Global find/replace across all files
# Before:
from mcp.server.fastmcp import FastMCP, Context

# After:
from fastmcp import FastMCP, Context
```

3. **Code Changes** (1-2 hours)
- Verify API compatibility
- Update run methods (slightly different signature)
- Optional: Add new 2.0 features (auth, storage, etc.)

4. **Testing** (8-11 hours)
- **Migration Testing**: Ensure all tools work (4-6 hours)
- **API Compatibility**: Test for subtle differences (2-3 hours)
- **Transport Testing**: STDIO, Streamable HTTP (2 hours)

5. **Docker Updates** (30 minutes)
- Update dependencies
- Rebuild image
- Test deployment

**Total Estimate: 10-14 hours**

**Breaking Change Risk: 🟠 Medium-High**
- Switching packages entirely
- Potential subtle API differences
- Less upstream contribution friendly

---

## Feature Regressions

### Does MCP SDK 1.22.0 Lack Anything Compared to FastMCP 2.0?

**Yes - FastMCP 2.0 Exclusive Features:**

| Feature | Impact for Zettelkasten MCP |
|---------|---------------------------|
| OAuth Authentication | ⚠️ Low (not needed now) |
| Persistent Storage | ⚠️ Low-Medium (nice-to-have for caching) |
| Middleware System | ⚠️ Low (nice-to-have for logging) |
| Tool Transformation | ❌ Not Needed |
| Server Proxying | ❌ Not Needed |
| OpenAPI Generation | ❌ Not Needed |
| FastMCP Cloud | ⚠️ Low-Medium (convenience) |
| In-Memory Testing | ✅ Medium (improves test suite) |

**Verdict:** MCP SDK 1.22.0 lacks **advanced enterprise features**, but none are critical for this project.

### Does FastMCP 2.0 Lack Anything Compared to MCP SDK 1.22.0?

**No - FastMCP 2.0 is a Superset**

FastMCP 2.0 implements everything from FastMCP 1.0 (in SDK) plus additional features. **No regressions.**

**Important Note on SDK Dependency:**
- FastMCP 2.12.5 **pins MCP SDK < 1.17** for compatibility
- This means FastMCP 2.0 may **lag behind** latest SDK protocol changes
- For cutting-edge MCP spec compliance, SDK 1.22.0 is better

---

## Which Has Better Support?

### Anthropic Official SDK (Option A)

**Support Model:**
- ✅ **Official**: Backed by Anthropic
- ✅ **Long-term**: Will exist as long as MCP exists
- ✅ **Stable**: Conservative, well-tested releases
- ✅ **Community**: 20k+ stars, large ecosystem
- ✅ **Best for PRs**: Upstream contributions accepted

**Risk Assessment: 🟢 Very Low**

### FastMCP 2.0 (Option B)

**Support Model:**
- ⚠️ **Community**: Maintained by jlowin + contributors
- ⚠️ **Dependent**: On maintainer(s) continued involvement
- ✅ **Active**: 10k stars in 6 weeks, rapid development
- ✅ **Responsive**: Fast issue resolution
- ❌ **PR Risk**: May not be accepted upstream

**Risk Assessment: 🟡 Low-Medium**
- Bus factor: If maintainer steps away, project could stall
- Fork divergence: May drift from official SDK over time

---

## Which is More Similar to Existing Project?

### Code Similarity: Option A Wins ✅

**Option A (MCP SDK 1.22.0):**
- ✅ **Same import path**: `from mcp.server.fastmcp import FastMCP`
- ✅ **Same package**: Already using `mcp[cli]`
- ✅ **Minimal changes**: Add one parameter, change transport string
- ✅ **95% identical**: to current codebase

**Option B (FastMCP 2.0):**
- ⚠️ **Different import**: `from fastmcp import FastMCP`
- ⚠️ **Package change**: `mcp` → `fastmcp`
- ✅ **API compatible**: Decorator syntax identical
- ✅ **90% identical**: to current codebase (after import changes)

**Winner: Option A** (less disruptive)

---

## Exclusive Features Summary

### Option A Exclusive: Official Backing ✅
- Anthropic official support
- Long-term stability guarantee
- Best for upstream PRs

### Option B Exclusive: Everything Else 🚀
- Authentication (OAuth, JWT, Bearer)
- Persistent storage (Redis, DynamoDB, etc.)
- Middleware system
- Tool transformation
- Server proxying
- OpenAPI generation
- FastMCP Cloud deployment
- In-memory testing
- Enhanced CLI & DX

---

## Final Recommendation

### For Zettelkasten MCP Project: **Option A** ✅

**Reasoning:**

1. **Project Goal**: Fork intended as upstream contribution (PR)
   - ✅ Option A: Official SDK, PR-friendly
   - ❌ Option B: Third-party package, PR may not be accepted

2. **Required Features**: Streamable HTTP support
   - ✅ Option A: Has it (v1.8.0+)
   - ✅ Option B: Has it (v2.3.0+)
   - **Both satisfy requirements**

3. **Migration Effort**:
   - ✅ Option A: 4-6 hours (minimal)
   - ⚠️ Option B: 10-14 hours (moderate)

4. **Long-term Maintenance**:
   - ✅ Option A: Anthropic official support
   - ⚠️ Option B: Community-dependent

5. **Similarity to Current Code**:
   - ✅ Option A: 95% identical (same imports)
   - ⚠️ Option B: 90% identical (import changes)

6. **FastMCP 2.0 Exclusive Features**:
   - Authentication: ⚠️ Not needed
   - Storage: ⚠️ Nice-to-have (not critical)
   - Middleware: ⚠️ Nice-to-have
   - OpenAPI/Proxying: ❌ Not needed
   - In-Memory Testing: ✅ Useful (but not critical)

**Verdict:**
Option A (MCP SDK 1.22.0) provides **everything needed** with **minimal effort** and **best upstream compatibility**. FastMCP 2.0's advanced features are impressive but not critical for this project's goals.

### When to Choose Option B

Consider FastMCP 2.0 if:
- ❌ **Not planning to contribute upstream** (standalone project)
- ✅ **Need enterprise auth** (OAuth, JWT)
- ✅ **Want managed deployment** (FastMCP Cloud)
- ✅ **Need advanced features** (middleware, proxying, tool transformation)
- ✅ **Willing to accept fork divergence risk**

For this project: **None of these apply strongly enough to justify the switch.**

---

## Migration Path (If Choosing Option A)

### Phase 1: Preparation (1 hour)
1. Create feature branch: `feat/upgrade-mcp-sdk-1.22`
2. Review MCP SDK changelog (1.6.0 → 1.22.0)
3. Document current behavior

### Phase 2: Upgrade Dependencies (30 min)
```bash
# Update pyproject.toml
dependencies = [
    "mcp[cli]>=1.22.0",
]

# Install
uv sync

# Verify
uv pip show mcp  # Should show 1.22.0
```

### Phase 3: Code Updates (30 min)
```python
# src/zettelkasten_mcp/server/mcp_server.py
self.mcp = FastMCP(
    config.server_name,
    version=config.server_version,
    json_response=config.json_response,
    stateless_http=True,  # ADD THIS
)

# src/zettelkasten_mcp/__main__.py
# Update transport string
if transport == "http":
    await mcp_server.mcp.run_async(
        transport="streamable-http",  # Changed from "sse"
        host=config.http_host,
        port=config.http_port,
    )
```

### Phase 4: Testing (3-4 hours)
```bash
# Run existing tests
uv run pytest

# Test STDIO transport
uvx zettelkasten-mcp

# Test Streamable HTTP
uvx zettelkasten-mcp --transport http --port 8000

# Test with Zed
# Update Zed config to use http://localhost:8000/mcp

# Test with mcp-remote (backward compat)
npx mcp-remote http://localhost:8000/sse  # Should still work
```

### Phase 5: Docker & Deployment (30 min)
```bash
# Update Docker image
docker-compose build

# Test container
docker-compose up

# Verify health endpoint
curl http://localhost:8000/health

# Test Streamable HTTP endpoint
curl http://localhost:8000/mcp
```

**Total: 4-6 hours** ✅

---

## Migration Path (If Choosing Option B)

### Phase 1: Preparation (1 hour)
Same as Option A

### Phase 2: Dependency Changes (30 min)
```toml
# pyproject.toml
dependencies = [
    # Remove:
    # "mcp[cli]>=1.2.0",

    # Add:
    "fastmcp>=2.13.0",

    # Keep:
    "sqlalchemy>=2.0.0",
    # ... rest unchanged
]
```

### Phase 3: Import Changes (1-2 hours)
```bash
# Global find/replace
find src -name "*.py" -exec sed -i '' 's/from mcp.server.fastmcp import/from fastmcp import/g' {} +
find src -name "*.py" -exec sed -i '' 's/from mcp.server.fastmcp.context import/from fastmcp import/g' {} +
```

### Phase 4: API Compatibility (2-3 hours)
- Review all tool/resource/prompt decorators
- Test for subtle API differences
- Update run methods if needed

### Phase 5: Testing (8-11 hours)
Same as Option A but more thorough due to package change

**Total: 10-14 hours** ⚠️

---

## References

- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **FastMCP 2.0**: https://github.com/jlowin/fastmcp
- **FastMCP Docs**: https://gofastmcp.com
- **MCP Specification**: https://modelcontextprotocol.io/specification
- **Cloudflare Blog**: https://blog.cloudflare.com/streamable-http-mcp-servers-python/

---

**Last Updated:** 2025-11-22
**Next Review:** After Option A implementation
**Decision:** Recommend Option A (MCP SDK 1.22.0)
