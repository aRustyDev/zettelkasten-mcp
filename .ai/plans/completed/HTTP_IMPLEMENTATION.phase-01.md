# HTTP Transport Implementation - Phase 1: Add Dependencies

**Status:** ✅ COMPLETED
**Date:** 2025-11-20
**Commit:** d7f22f6
**Plan:** [Back to main plan](../HTTP_IMPLEMENTATION.md)

---


### Step 1.1: Update pyproject.toml
**File:** `pyproject.toml`

**Action:** Add HTTP server dependencies to the `dependencies` array:

```toml
dependencies = [
    "mcp[cli]>=1.2.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "markdown>=3.4.0",
    "python-frontmatter>=1.0.0",
    "python-dotenv>=1.0.0",
    # New HTTP dependencies
    "starlette>=0.27.0",
    "uvicorn>=0.23.0",
]
```

**Rationale:** Starlette provides the ASGI framework and uvicorn is the ASGI server needed for HTTP transport.

### Step 1.2: Install Dependencies
```bash
pip install -e .
# or if using uv
uv pip install -e .
```

---

