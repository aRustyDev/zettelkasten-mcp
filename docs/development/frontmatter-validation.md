# Frontmatter Validation

## Overview

The `.ai/scripts/validate-frontmatter.py` script validates YAML frontmatter in markdown files with UUID-based cross-reference checking. It ensures consistency across the knowledge base and catches broken references between documents.

### Key Features

- **Configuration-based scanning** - Define what to validate via config file
- **UUID cache** - Fast repeated validation (30-40% performance improvement)
- **Two-phase discovery** - Accurate single-file validation with cross-reference checking
- **Pre-commit integration** - Automatic validation on commit
- **Smart defaults** - Works without configuration

---

## Quick Start

### Basic Usage

Validate a single file:
```bash
python3 .ai/scripts/validate-frontmatter.py path/to/file.md
```

Validate multiple files:
```bash
python3 .ai/scripts/validate-frontmatter.py file1.md file2.md file3.md
```

Use custom config:
```bash
python3 .ai/scripts/validate-frontmatter.py --config /path/to/config.json file.md
python3 .ai/scripts/validate-frontmatter.py -c /path/to/config.json file.md
```

Validate using glob pattern:
```bash
python3 .ai/scripts/validate-frontmatter.py --glob '.ai/plans/**/*.md'
python3 .ai/scripts/validate-frontmatter.py -g '.ai/**/*.md'
```

### Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config PATH` | `-c` | Path to config file (default: `.ai/.frontmatter-config.json`) |
| `--glob PATTERN` | `-g` | Glob pattern to match files |
| `--help` | `-h` | Show help message and exit |

**Examples:**
- `python3 .ai/scripts/validate-frontmatter.py --help` - View all options
- `python3 .ai/scripts/validate-frontmatter.py -c custom.json file.md` - Use custom config
- `python3 .ai/scripts/validate-frontmatter.py --glob '.ai/**/*.md'` - Validate all markdown in .ai/

### With Pre-commit

The validator runs automatically on commit for changed markdown files:
```bash
git add .ai/INDEX.md
git commit -m "Update index"
# Pre-commit automatically validates INDEX.md
```

---

## Configuration

### Config File Location

`.ai/.frontmatter-config.json` (optional)

If this file doesn't exist, the validator uses sensible defaults.

### Minimal Configuration

Enable caching only:
```json
{
  "version": "1.0",
  "cache": {
    "enabled": true
  }
}
```

### Full Configuration Example

```json
{
  "version": "1.0",
  "scan": {
    "directories": [".ai", "docs"],
    "exclude_patterns": [
      "**/templates/**",
      "**/artifacts/**",
      "**/prompts/**",
      "docs/project-knowledge/user/**"
    ]
  },
  "validation": {
    "required_fields": ["id", "title", "status", "date", "author"],
    "validate_cross_references": true,
    "title_must_match_h1": true
  },
  "cache": {
    "enabled": true,
    "path": ".ai/.uuid-cache.json",
    "ttl_seconds": 3600
  }
}
```

### Configuration Options

#### `version` (required)
- **Type:** String
- **Value:** `"1.0"`
- **Purpose:** Config schema version

#### `scan` (optional)
Defines which files to validate.

- **`directories`** - List of directories to scan for markdown files
  - Default: `[".ai", "docs"]`

- **`exclude_patterns`** - Glob patterns to exclude
  - Default: `["**/templates/**", "**/artifacts/**"]`
  - Supports standard glob syntax: `**/pattern/**`

#### `validation` (optional)
Defines validation rules.

- **`required_fields`** - Frontmatter fields that must be present
  - Default: `["id", "title", "status", "date", "author"]`

- **`validate_cross_references`** - Check UUID references exist
  - Default: `true`
  - Validates UUIDs in `related` and `children` fields

- **`title_must_match_h1`** - Warn if title differs from H1 heading
  - Default: `true`

#### `cache` (optional)
Optional performance optimization.

- **`enabled`** - Enable UUID cache
  - Default: `false` (conservative default)
  - Recommended: `true` for projects with 50+ markdown files

- **`path`** - Cache file location
  - Default: `".ai/.uuid-cache.json"`
  - **Important:** Add this to `.gitignore`

- **`ttl_seconds`** - Time-to-live in seconds
  - Default: `null` (no expiration)
  - Example: `3600` = 1 hour, `86400` = 24 hours
  - Cache also invalidates on file changes

---

## How It Works

### Two-Phase Discovery

The validator uses a two-phase approach for accurate validation:

**Phase 1: UUID Discovery**
- Scans all markdown files in configured directories
- Builds complete UUID → file path mapping
- Uses cache if available (fast) or scans filesystem (slower)

**Phase 2: Validation**
- Validates only the requested files in detail
- Checks cross-references against complete UUID map
- Reports errors and warnings

This architecture enables **single-file validation** while maintaining **accurate cross-reference checking**.

### Cache Mechanism

When caching is enabled:

1. **First run** - Scans all files, builds UUID map, saves cache (~200ms for 40 files)
2. **Subsequent runs** - Loads UUID map from cache (~130ms for 40 files)
3. **Cache invalidation** - Automatically rebuilds when:
   - Configuration changes
   - Any markdown file is modified (mtime check)
   - File count changes (files added/removed)
   - TTL expires (if configured)

**Performance:** ~35% faster with cache for typical projects.

---

## Usage Examples

### Example 1: Validate Single File with Cross-References

```bash
python3 .ai/scripts/validate-frontmatter.py .ai/plans/phases/streamable-http-implementation.phase-1.md
```

**What happens:**
1. Loads configuration (or uses defaults)
2. Discovers all UUIDs in `.ai/` and `docs/`
3. Validates only `phase-1.md` in detail
4. Checks that referenced UUIDs exist

**Output:**
```
============================================================
Frontmatter Validation Results
============================================================
Files validated: 1
Passed: 1
Failed: 0

✅ All frontmatter is valid!
```

### Example 2: Enable Caching for Faster Validation

Create `.ai/.frontmatter-config.json`:
```json
{
  "version": "1.0",
  "cache": {
    "enabled": true,
    "ttl_seconds": 3600
  }
}
```

Then run:
```bash
# First run - creates cache
python3 .ai/scripts/validate-frontmatter.py .ai/INDEX.md  # ~200ms

# Second run - uses cache
python3 .ai/scripts/validate-frontmatter.py .ai/INDEX.md  # ~130ms
```

### Example 3: Custom Scan Directories

Validate only `.ai/` directory:
```json
{
  "version": "1.0",
  "scan": {
    "directories": [".ai"]
  }
}
```

### Example 4: Exclude Additional Patterns

```json
{
  "version": "1.0",
  "scan": {
    "exclude_patterns": [
      "**/templates/**",
      "**/artifacts/**",
      "**/drafts/**",
      "**/*.draft.md"
    ]
  }
}
```

---

## Pre-commit Integration

### Configuration

The validator is configured as a pre-commit hook in `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: validate-frontmatter
      name: Validate Markdown Frontmatter
      entry: python3 .ai/scripts/validate-frontmatter.py
      language: system
      files: \.md$
      exclude: ^(README\.md|CHANGELOG\.md|\.github/.*\.md|\.ai/templates/.*|\.ai/artifacts/.*)$
      pass_filenames: true
```

### Behavior

- Runs automatically when committing markdown files
- Validates only changed files
- Uses complete UUID map for accurate cross-reference checking
- Blocks commit if validation fails

### Manual Testing

Test the hook without committing:
```bash
# Single file
pre-commit run validate-frontmatter --files .ai/INDEX.md

# All files
pre-commit run validate-frontmatter --all-files
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Invalid UUID reference" Error

**Error:**
```
❌ Errors (1):
  - .ai/INDEX.md: Invalid UUID reference in 'children': 2F7850D8-3E51-456C-AE60-C70BAF323BFB
```

**Causes:**
1. Referenced document doesn't have frontmatter
2. Referenced document has wrong UUID
3. Referenced document excluded from scanning

**Solutions:**
1. Check that referenced file exists and has frontmatter
2. Verify UUID matches exactly (uppercase, no quotes)
3. Check `exclude_patterns` in config

#### Issue 2: "Duplicate UUID" Error

**Error:**
```
❌ Errors (1):
  - .ai/plans/new-doc.md: Duplicate UUID ABC123... (also in .ai/plans/old-doc.md)
```

**Cause:** Two files have the same UUID in their frontmatter.

**Solution:** Generate a new UUID for one file:
```bash
uuidgen | tr '[:lower:]' '[:upper:]'
```

#### Issue 3: Cache Not Working

**Symptom:** No performance improvement on second run.

**Checks:**
```bash
# 1. Is cache enabled in config?
cat .ai/.frontmatter-config.json
# Should have: "enabled": true

# 2. Is cache file being created?
ls -la .ai/.uuid-cache.json

# 3. Check cache is valid
python3 -c "
import json
cache = json.load(open('.ai/.uuid-cache.json'))
print(f'Version: {cache[\"version\"]}')
print(f'UUIDs: {len(cache[\"uuids\"])}')
"
```

**Solutions:**
- Ensure config has `"version": "1.0"`
- Check `.ai/` directory is writable
- Verify cache file not gitignored in wrong location

#### Issue 4: "No frontmatter found"

**Error:**
```
❌ Errors (1):
  - docs/new-file.md: No frontmatter found
```

**Cause:** File doesn't start with `---`

**Solution:** Add frontmatter to file:
```markdown
---
id: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
title: Document Title
status: Draft
date: 2025-11-23
author: Your Name
---

# Document Title

Content here...
```

Generate UUID:
```bash
uuidgen | tr '[:lower:]' '[:upper:]'
```

#### Issue 5: Title Mismatch Warning

**Warning:**
```
⚠️  Warnings (1):
  - .ai/plans/doc.md: Title mismatch - frontmatter: 'Plan A', H1: 'Plan B'
```

**Cause:** Title in frontmatter differs from H1 heading.

**Solution:** Make them match:
```markdown
---
title: Implementation Plan
---

# Implementation Plan
```

---

## Performance

### Benchmarks

**Environment:** 41 markdown files in knowledge base

| Scenario | Without Cache | With Cache | Improvement |
|----------|---------------|------------|-------------|
| First run | 208ms | 208ms | - |
| Second run | 208ms | 136ms | **35% faster** |
| Third run | 208ms | 136ms | **35% faster** |

**Scaling:**
- 50-100 files: ~40% improvement
- 100-500 files: ~50% improvement
- 500+ files: ~60% improvement

### When to Enable Cache

**Enable cache if:**
- ✅ Project has 50+ markdown files
- ✅ Running validation frequently (pre-commit, CI)
- ✅ Development workflow involves many commits

**Keep cache disabled if:**
- ❌ Small project (<20 files)
- ❌ Files change very frequently
- ❌ Prefer predictable behavior over performance

---

## Best Practices

### 1. Use Minimal Configs

Let defaults handle most settings:
```json
{
  "version": "1.0",
  "cache": {
    "enabled": true
  }
}
```

### 2. Set Appropriate TTL

Balance freshness vs performance:
- **No TTL** (`null`) - Cache valid until file changes
- **1 hour** (`3600`) - Good for active development
- **24 hours** (`86400`) - Good for stable projects

### 3. Exclude Appropriately

Exclude files that shouldn't be validated:
```json
{
  "scan": {
    "exclude_patterns": [
      "**/templates/**",    // Template files
      "**/artifacts/**",    // Generated files
      "**/drafts/**",       // Work in progress
      "**/*.draft.md"       // Draft documents
    ]
  }
}
```

### 4. Version Control

**Commit:** `.ai/.frontmatter-config.json`
**Ignore:** `.ai/.uuid-cache.json`

### 5. CI/CD Integration

For GitHub Actions:
```yaml
- name: Validate frontmatter
  run: |
    python3 .ai/scripts/validate-frontmatter.py .ai/**/*.md docs/**/*.md
```

Cache can be disabled in CI for consistency:
```json
{
  "version": "1.0",
  "cache": {
    "enabled": false
  }
}
```

Or use separate config for CI.

---

## Migration Guide

### From Previous Version (No Config Support)

The validator is **fully backward compatible**. No changes required.

**Optional:** Enable caching for better performance:

1. Create config file:
```bash
cat > .ai/.frontmatter-config.json <<EOF
{
  "version": "1.0",
  "cache": {
    "enabled": true,
    "ttl_seconds": 3600
  }
}
EOF
```

2. Add cache to gitignore:
```bash
echo ".ai/.uuid-cache.json" >> .gitignore
```

3. Test:
```bash
python3 .ai/scripts/validate-frontmatter.py .ai/INDEX.md
```

That's it! Validation behavior unchanged, just faster.

---

## FAQ

### Q: Do I need a config file?

**A:** No. The validator works perfectly without configuration using smart defaults.

### Q: Will caching break validation accuracy?

**A:** No. Cache automatically invalidates when files change. Cross-reference validation remains 100% accurate.

### Q: Can I use different configs for different environments?

**A:** Yes. Use the `--config` flag to specify different config files:
```bash
# Development (with cache)
python3 .ai/scripts/validate-frontmatter.py --config .ai/.frontmatter-dev.json file.md

# CI (strict, no cache)
python3 .ai/scripts/validate-frontmatter.py --config .ai/.frontmatter-ci.json file.md

# Use default config
python3 .ai/scripts/validate-frontmatter.py file.md
```

You can also use the short form `-c`:
```bash
python3 .ai/scripts/validate-frontmatter.py -c custom.json file.md
```

### Q: How do I debug validation failures?

**A:** Run validator directly to see detailed output:
```bash
python3 .ai/scripts/validate-frontmatter.py path/to/failing-file.md
```

### Q: What happens if cache gets corrupted?

**A:** Validator detects invalid cache and rebuilds automatically. No intervention needed.

---

## Schema Reference

### Frontmatter Schema

Required fields:
```yaml
---
id: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX  # UUID (uppercase)
title: Document Title                      # String
status: Draft                               # String
date: 2025-11-23                           # YYYY-MM-DD
author: Author Name                         # String
---
```

Optional fields:
```yaml
related:                                    # List of related document UUIDs
  - AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA
  - BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB

children:                                   # List of child document UUIDs
  - CCCCCCCC-CCCC-CCCC-CCCC-CCCCCCCCCCCC
```

### Configuration Schema

See [Configuration Options](#configuration-options) above.

### Cache Schema

Auto-generated, do not edit manually:
```json
{
  "version": "1.0",
  "created": "2025-11-23T10:30:00Z",
  "timestamp": 1700000000,
  "config_hash": "a1b2c3d4e5f6",
  "file_count": 40,
  "file_mtimes": {
    "file_path": 1699999999
  },
  "uuids": {
    "UUID": "file_path"
  }
}
```

---

## Related Documentation

- [Zettelkasten Methodology](../project-knowledge/user/zettelkasten-methodology-technical.md)
- [Link Types](../project-knowledge/user/link-types-in-zettelkasten-mcp-server.md)
- [Frontmatter Adoption Plan](../../.ai/plans/FRONTMATTER_ADOPTION.md)

---

**Last Updated:** 2025-11-23
**Validator Version:** 1.0 (with config + cache support)
