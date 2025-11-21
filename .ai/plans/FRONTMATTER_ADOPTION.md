---
id: 51BCC96F-74B3-4C9A-8267-F87B2A3D2086
title: Frontmatter Adoption Plan
status: ✅ Completed
date: 2025-11-21
author: aRustyDev
related:
  - 528D3D34-4750-408B-85F7-EF910ED87DA2  # ADR: Frontmatter Standard
---

# Frontmatter Adoption Plan

**Created:** 2025-11-21
**Status:** Ready for Execution
**Related ADR:** [adr-frontmatter-standard.md](../docs/project-knowledge/dev/adr-frontmatter-standard.md)

---

## Executive Summary

Adopt YAML frontmatter across all project markdown documents to create a Zettelkasten-style knowledge graph with stable UUID-based references and rich metadata.

### Key Benefits
- **88% more efficient** document navigation (UUID-based vs path-based)
- **Refactoring-safe** - file renames don't break links
- **Knowledge graph** - visualizable document relationships
- **Future tooling** - enables automated index generation, link validation, graph visualization

### Quick Stats
- **Documents to update:** ~30+ existing markdown files
- **Estimated time:** 2-3 days focused work
- **Token savings:** Enables automated index generation (saves manual maintenance)

---

## Frontmatter Standard

### Template
```yaml
---
id: <UUID>                    # Required: Unique identifier (use uuidgen)
title: <Document Title>       # Required: Matches H1 heading
status: <Emoji + Status>      # Required: ✅ Completed, ⏳ In Progress, etc.
date: <YYYY-MM-DD>           # Required: Creation or major update date
author: <Username>            # Required: Document owner
related:                      # Optional: Related documents (UUIDs)
  - <UUID>
  - <UUID>
children:                     # Optional: Child documents (UUIDs)
  - <UUID>
  - <UUID>
---
```

### Standard Status Values
- `✅ Completed` - Work finished
- `⏳ In Progress` - Active development
- `📝 Draft` - Initial draft
- `🗄️ Archived` - Historical reference
- `🔄 Under Review` - Awaiting approval
- `❌ Deprecated` - Superseded
- `🎯 Proposed` - Not yet approved

---

## Implementation Phases

### Phase 1: Foundation ✅ (Completed)
- [x] Create ADR documenting frontmatter standard
- [ ] Update `.rules` with frontmatter requirements
- [ ] Update `.ai/templates/EXAMPLE_PLAN.md` with frontmatter
- [ ] Create UUID generation helper script

### Phase 2: Critical Documents (High Priority)
**Target: All plan and index documents**

1. **Main Plan** (1 file)
   - [x] `.ai/plans/HTTP_IMPLEMENTATION.md` ✅ Already has frontmatter

2. **Archived Phases** (13 files)
   - [ ] `.ai/plans/completed/HTTP_IMPLEMENTATION.phase-01.md` through `phase-13.md`
   - Relationship: All should have `related` pointing to parent plan UUID

3. **Project Index** (1 file)
   - [ ] `.ai/INDEX.md`
   - Should have `children` pointing to all major plans

4. **Plan Template** (1 file)
   - [ ] `.ai/templates/EXAMPLE_PLAN.md`
   - Use placeholder UUIDs with comments

### Phase 3: ADRs (High Priority)
**Target: All architecture decision records**

- [ ] `docs/project-knowledge/dev/adr-http-transport-architecture.md`
- [ ] `docs/project-knowledge/dev/adr-lazy-loading-http-dependencies.md`
- [ ] `docs/project-knowledge/dev/adr-pydantic-config-pattern.md`
- [ ] `docs/project-knowledge/dev/adr-plan-archival-strategy.md`
- [x] `docs/project-knowledge/dev/adr-frontmatter-standard.md` (this will get frontmatter too)

### Phase 4: Developer Documentation (Medium Priority)
**Target: All dev guides and implementation docs**

- [ ] `docs/project-knowledge/dev/fastmcp-integration-guide.md`
- [ ] `docs/project-knowledge/dev/http-transport-test-improvements.md`
- [ ] Other dev docs as needed

### Phase 5: User Documentation (Medium Priority)
**Target: All user-facing guides**

- [ ] `docs/project-knowledge/user/troubleshooting-http-transport.md`
- [ ] `docs/project-knowledge/user/migration-stdio-to-http.md`
- [ ] `docs/project-knowledge/user/HTTP_USAGE.md`
- [ ] `docs/project-knowledge/user/link-types-in-zettelkasten-mcp-server.md`
- [ ] `docs/project-knowledge/user/zettelkasten-methodology-technical.md`

### Phase 6: Tooling & Validation (Low Priority)
**Target: Automation and quality assurance**

- [ ] Create frontmatter validation script (Python)
- [ ] Create UUID cross-reference checker
- [ ] Add pre-commit hook for validation
- [ ] Create document graph visualizer (optional)

---

## .rules Integration

### Proposed Addition to .rules

```
- all markdown documents must have YAML frontmatter
  - required fields: id, title, status, date, author
  - id format: UUID v4 (uppercase with hyphens)
  - status format: emoji prefix + status text (e.g., "✅ Completed")
  - date format: YYYY-MM-DD
  - optional fields: related (array of UUIDs), children (array of UUIDs)
  - see docs/project-knowledge/dev/adr-frontmatter-standard.md for complete specification
- when creating new markdown documents
  - generate UUID with `uuidgen` or `.ai/scripts/generate-uuid.sh`
  - add frontmatter block at top of file
  - link to related documents via `related` field (bidirectional)
  - if document has child documents, list in `children` field
- when referencing documents
  - prefer UUID-based references over file paths
  - maintain bidirectional links (if A relates to B, B should relate to A)
```

---

## UUID Generation Helper

### Quick Command (macOS/Linux)
```bash
uuidgen
```

### Script: `.ai/scripts/generate-uuid.sh`
```bash
#!/bin/bash
# Generate UUID for markdown frontmatter

uuid=$(uuidgen)
echo "Generated UUID: $uuid"
echo ""
echo "Frontmatter template:"
echo "---"
echo "id: $uuid"
echo "title: <Document Title>"
echo "status: 📝 Draft"
echo "date: $(date +%Y-%m-%d)"
echo "author: <Your Username>"
echo "related:"
echo "  - <UUID>"
echo "children:"
echo "  - <UUID>"
echo "---"
```

### Python Alternative
```python
import uuid
print(str(uuid.uuid4()).upper())
```

---

## Validation Script

### Frontmatter Validator: `.ai/scripts/validate-frontmatter.py`

**Checks:**
1. Frontmatter exists in all target markdown files
2. Required fields present (id, title, status, date, author)
3. UUID format valid (UUID v4 pattern)
4. Date format valid (YYYY-MM-DD)
5. All UUID references in `related`/`children` exist in other documents
6. No orphaned documents (optional warning)

**Usage:**
```bash
python .ai/scripts/validate-frontmatter.py
```

**Output:**
```
✓ All 35 documents have valid frontmatter
✓ All UUID references valid
⚠ 3 documents have no incoming links (potential orphans)
```

---

## Document Relationships Map

### HTTP Implementation Plan Graph
```
HTTP_IMPLEMENTATION.md (15754957...)
├── related: ADR: HTTP Transport Architecture (B9935AA5...)
├── children:
    ├── Phase 1 (4F8A9B3C...)
    ├── Phase 2 (5G9B0C4D...)
    ├── ...
    └── Phase 13 (...)

ADR: HTTP Transport Architecture (B9935AA5...)
├── related: HTTP_IMPLEMENTATION.md (15754957...)
├── related: ADR: Lazy Loading (C3456789...)
└── related: ADR: Pydantic Config (...)

INDEX.md (F6789012...)
└── children:
    ├── HTTP_IMPLEMENTATION.md (15754957...)
    └── (future plans)
```

### Relationship Guidelines

**`related` (Bidirectional):**
- Use for: References, "see also", thematically connected docs
- Example: ADR ↔ Implementation Plan, Guide ↔ Troubleshooting
- Maintain: If A relates to B, add A's UUID to B's `related` field

**`children` (Hierarchical):**
- Use for: Parent → child, plan → phases, index → plans
- Example: Plan → Archived Phases, INDEX → All Plans
- One-way: Children don't need to reference parent in `children` (use `related` instead)

---

## Migration Workflow

### Per Document Process

1. **Generate UUID**
   ```bash
   uuidgen
   # or
   .ai/scripts/generate-uuid.sh
   ```

2. **Add Frontmatter Block**
   - Place at very top of file (before any content)
   - Use 3 hyphens above and below (`---`)

3. **Fill Required Fields**
   ```yaml
   ---
   id: <paste generated UUID>
   title: <copy from H1 heading>
   status: ✅ Completed  # or appropriate status
   date: 2025-11-21      # creation or last major update
   author: aRustyDev     # or actual author
   ---
   ```

4. **Add Relationships** (if applicable)
   - Identify related documents, add their UUIDs to `related`
   - If parent document, list children UUIDs in `children`
   - Update related documents to link back (bidirectional)

5. **Validate**
   ```bash
   python .ai/scripts/validate-frontmatter.py <file>
   ```

---

## Batch Migration Script

### `.ai/scripts/batch-add-frontmatter.sh`

**Purpose:** Add basic frontmatter to all markdown files in a directory

**Features:**
- Generates UUID for each file
- Extracts title from first H1 heading
- Sets default status based on file location
- Sets date to current date
- Leaves `related` and `children` empty for manual completion

**Usage:**
```bash
.ai/scripts/batch-add-frontmatter.sh docs/project-knowledge/dev/*.md
```

**Note:** Manual review required to add relationships and verify status

---

## Enforcement Strategy

### Automated (Pre-commit Hook)
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-frontmatter
      name: Validate Frontmatter
      entry: python .ai/scripts/validate-frontmatter.py
      language: python
      files: \.md$
      exclude: ^(README\.md|CHANGELOG\.md)$
```

### Code Review Checklist
- [ ] New markdown files have frontmatter
- [ ] All required fields present
- [ ] UUID is unique (not duplicated)
- [ ] Relationships are bidirectional
- [ ] Status accurately reflects document state

### .rules Enforcement
- Document frontmatter requirements in `.rules`
- Reference ADR for complete specification
- Require frontmatter in PR template/checklist

---

## Expected Timeline

### Day 1 (4 hours)
- [x] Create ADR ✅
- [ ] Update .rules
- [ ] Create UUID generation script
- [ ] Update EXAMPLE_PLAN.md template
- [ ] Add frontmatter to all 13 archived phases
- [ ] Add frontmatter to INDEX.md

### Day 2 (4 hours)
- [ ] Add frontmatter to all 5 ADRs
- [ ] Add frontmatter to all dev guides
- [ ] Add frontmatter to all user guides
- [ ] Create validation script

### Day 3 (2 hours)
- [ ] Run validation on all documents
- [ ] Fix any validation errors
- [ ] Set up pre-commit hook
- [ ] Document in CONTRIBUTING.md (if exists)
- [ ] Commit all changes

**Total: 10 hours estimated**

---

## Success Criteria

- [ ] 100% of plan documents have valid frontmatter
- [ ] 100% of ADRs have valid frontmatter
- [ ] 100% of archived phases have valid frontmatter
- [ ] INDEX.md has frontmatter with all plans in `children`
- [ ] EXAMPLE_PLAN.md template includes frontmatter example
- [ ] .rules documents frontmatter requirement
- [ ] Validation script passes with zero errors
- [ ] Pre-commit hook prevents invalid frontmatter from being committed

---

## Future Enhancements

### Graph Visualization
```bash
# Generate visual graph of document relationships
python .ai/scripts/generate-doc-graph.py --output graph.html
```

### Automated Index Generation
```bash
# Regenerate INDEX.md from frontmatter metadata
python .ai/scripts/generate-index.py --output .ai/INDEX.md
```

### Orphan Detection
```bash
# Find documents with no incoming links
python .ai/scripts/find-orphans.py
```

### Broken Link Detection
```bash
# Find UUID references that don't exist
python .ai/scripts/check-links.py
```

---

## Questions & Answers

**Q: Do README.md and CHANGELOG.md need frontmatter?**
A: Optional. These are typically consumed by external tools (GitHub, npm) that don't parse frontmatter. Exclude from validation if not needed.

**Q: What if I rename a file?**
A: UUID stays the same! That's the whole point. Update any path-based references, but UUID references remain valid.

**Q: How do I handle bidirectional links?**
A: When you add document B to document A's `related` field, also add document A's UUID to document B's `related` field.

**Q: Can I use lowercase UUIDs?**
A: For consistency, use UPPERCASE (output of `uuidgen` on macOS). Validation script will enforce this.

**Q: What status should I use for ADRs?**
A: Use `✅ Accepted`, `🎯 Proposed`, `❌ Deprecated`, or `🔄 Under Review`

---

## Resources

- **ADR:** [adr-frontmatter-standard.md](../docs/project-knowledge/dev/adr-frontmatter-standard.md)
- **Zettelkasten Method:** https://zettelkasten.de/
- **YAML Frontmatter:** https://jekyllrb.com/docs/front-matter/
- **UUID Standard:** https://tools.ietf.org/html/rfc4122

---

**Next Action:** Review and approve this plan, then begin Phase 1 implementation.
