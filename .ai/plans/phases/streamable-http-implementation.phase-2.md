---
id: 4F557F9D-D5A9-4ACD-88D2-C741353CAC20
title: "Phase 2: Upgrade Dependencies"
status: ✅ Completed
date: 2025-11-22
author: aRustyDev
related:
  - 2F7850D8-3E51-456C-AE60-C70BAF323BFB  # Plan: Streamable HTTP Implementation
  - 3EC53936-B5CC-425D-804B-ED865033880B  # Phase 1: Preparation & Analysis
---

# Phase 2: Upgrade Dependencies

**Duration:** 1 hour
**Status:** ⏸️ Pending

---

## Objective

Upgrade MCP Python SDK from version 1.6.0 to 1.22.0 and resolve any dependency conflicts.

---

## Tasks

### 2.1 Update pyproject.toml

File: `/Users/arustydev/repos/mcp/zettelkasten-mcp/pyproject.toml`

**Change:**
```diff
 [project]
 dependencies = [
-    "mcp[cli]>=1.2.0",
+    "mcp[cli]>=1.22.0",
     "sqlalchemy>=2.0.0",
     "pydantic>=2.0.0",
     "python-frontmatter>=1.0.0",
     "markdown>=3.4.0",
     "python-dotenv>=1.0.0",
     "starlette>=0.27.0",
     "uvicorn>=0.23.0",
 ]
```

**Why `>=1.22.0`?**
- Ensures we get at least version 1.22.0 which includes Streamable HTTP
- Allows patch version updates (1.22.1, 1.22.2, etc.)
- Future-proofs for minor bugfixes in the 1.22.x series

---

### 2.2 Upgrade Dependencies

```bash
cd /Users/arustydev/repos/mcp/zettelkasten-mcp

# Remove old lock file to force fresh dependency resolution
rm uv.lock

# Sync dependencies (downloads and installs packages)
uv sync

# Verify the upgrade was successful
uv pip show mcp
# Expected output: Version: 1.22.0 (or newer patch version)
```

**What Happens:**
1. `rm uv.lock` - Forces `uv` to recalculate all dependency versions
2. `uv sync` - Resolves dependencies, creates new lock file, installs packages
3. `uv pip show mcp` - Confirms MCP SDK version upgraded successfully

**Expected Duration:** 2-5 minutes (depending on network speed)

---

### 2.3 Check for Dependency Conflicts

```bash
# Capture new package versions
uv pip list > .ai/artifacts/post-upgrade-packages.txt

# Check for any dependency conflicts or warnings
uv pip check

# Compare before/after package versions
diff .ai/artifacts/pre-upgrade-packages.txt .ai/artifacts/post-upgrade-packages.txt > .ai/artifacts/package-diff.txt

# Review the diff
cat .ai/artifacts/package-diff.txt
```

**What to Look For:**
- `uv pip check` should output: "No broken requirements found"
- `package-diff.txt` should show:
  - `mcp` upgraded from 1.6.0 → 1.22.0
  - Possible updates to `starlette`, `uvicorn` (MCP SDK dependencies)
  - No unexpected major version changes in other packages

**Red Flags:**
- ❌ `uv pip check` reports broken requirements
- ❌ Major version changes in SQLAlchemy, Pydantic, or other core deps
- ❌ Package removal (any `-` lines in diff for critical packages)

**If Issues Occur:**
- Review the diff carefully
- Check if new MCP SDK has conflicting dependency requirements
- Consider pinning problematic packages to compatible versions
- Document issues in `.ai/artifacts/upgrade-issues.md`

---

### 2.4 Verify Import Still Works

```bash
# Quick smoke test - verify FastMCP can be imported
uv run python -c "from mcp.server.fastmcp import FastMCP, Context; print('Import successful')"

# Expected output: "Import successful"
```

**Purpose:**
- Ensures the upgrade didn't break basic import paths
- Confirms FastMCP 1.0 is still available in upgraded SDK
- Quick sanity check before diving into code changes

**If Import Fails:**
- Check error message carefully
- Verify `mcp` package installed correctly: `uv pip show mcp`
- Check if FastMCP moved to different module path (unlikely but possible)
- Review SDK changelog for breaking changes

---

## Deliverables

After completing this phase, you should have:

- ✅ `pyproject.toml` updated with `mcp[cli]>=1.22.0`
- ✅ New `uv.lock` file generated
- ✅ MCP SDK upgraded to version 1.22.0 (or newer)
- ✅ No dependency conflicts (`uv pip check` passes)
- ✅ FastMCP imports successfully
- ✅ Package diff documented in `.ai/artifacts/package-diff.txt`

---

## Verification Checklist

Before proceeding to Phase 3:

- [ ] `pyproject.toml` contains `mcp[cli]>=1.22.0`
- [ ] `uv pip show mcp` shows version 1.22.0 or newer
- [ ] `uv pip check` reports no broken requirements
- [ ] FastMCP import test passes
- [ ] `package-diff.txt` reviewed and looks reasonable
- [ ] No unexpected major version changes in critical dependencies

---

## Rollback Plan

If this phase fails:

```bash
# Revert changes
git checkout pyproject.toml uv.lock

# Reinstall old dependencies
uv sync

# Verify rollback
uv pip show mcp  # Should show 1.6.0
```

**When to Rollback:**
- Irreconcilable dependency conflicts
- Critical breaking changes discovered in changelog
- FastMCP import fails
- Major version conflicts with SQLAlchemy/Pydantic

---

## Time Estimate

**Total: 1 hour**

- Update pyproject.toml: 2 minutes
- Run upgrade: 5 minutes
- Check conflicts: 10 minutes
- Verify imports: 5 minutes
- Review and document: 30 minutes
- Buffer for issues: 8 minutes

---

## Known Risks

**🟡 Medium Risk: Breaking Changes**
- 16 minor version jump (1.6.0 → 1.22.0)
- **Mitigation:** Changelog review in Phase 1 should catch major issues

**🟢 Low Risk: Dependency Conflicts**
- MCP SDK has stable dependencies (starlette, uvicorn)
- **Mitigation:** `uv pip check` will catch issues immediately

**🟢 Low Risk: FastMCP API Changes**
- FastMCP 1.0 API is stable across SDK versions
- **Mitigation:** Import test confirms availability

---

## Notes

- Keep `pre-upgrade-packages.txt` for comparison and rollback reference
- Document any warnings or unexpected changes in `.ai/artifacts/upgrade-notes.md`
- If major issues found, pause and reassess approach

---

**Previous Phase:** [Phase 1: Preparation & Analysis](./streamable-http-implementation.phase-1.md)
**Next Phase:** [Phase 3: Code Updates for Streamable HTTP](./streamable-http-implementation.phase-3.md)
