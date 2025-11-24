# Frontmatter Validation - Quick Reference

## Quick Commands

```bash
# Validate single file
python3 .ai/scripts/validate-frontmatter.py path/to/file.md

# Validate multiple files
python3 .ai/scripts/validate-frontmatter.py file1.md file2.md

# Use custom config
python3 .ai/scripts/validate-frontmatter.py --config /path/to/config.json file.md
python3 .ai/scripts/validate-frontmatter.py -c /path/to/config.json file.md

# Validate using glob pattern
python3 .ai/scripts/validate-frontmatter.py --glob '.ai/plans/**/*.md'

# Test pre-commit hook
pre-commit run validate-frontmatter --files .ai/INDEX.md
pre-commit run validate-frontmatter --all-files
```

## Minimal Config (Enable Cache)

`.ai/.frontmatter-config.json`:
```json
{
  "version": "1.0",
  "cache": {
    "enabled": true
  }
}
```

## Required Frontmatter

```yaml
---
id: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX  # uuidgen | tr '[:lower:]' '[:upper:]'
title: Document Title
status: Draft
date: 2025-11-23  # YYYY-MM-DD
author: Your Name
---

# Document Title
```

## Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Invalid UUID reference | Check referenced file has frontmatter |
| Duplicate UUID | Run `uuidgen \| tr '[:lower:]' '[:upper:]'` |
| No frontmatter found | Add frontmatter to top of file |
| Title mismatch | Make frontmatter title match H1 heading |
| Cache not working | Check config has `"version": "1.0"` |

## Performance

- **Without cache:** ~200ms (41 files)
- **With cache:** ~136ms (41 files)
- **Improvement:** ~35% faster

## Full Documentation

See `docs/development/frontmatter-validation.md`
