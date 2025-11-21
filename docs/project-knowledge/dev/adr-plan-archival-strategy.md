---
id: 9B7BB6E1-A27A-4BB6-BBD6-C26FD24529A1
title: ADR: Plan Archival Strategy for Token Efficiency
status: ✅ Accepted
date: 2025-11-21
author: aRustyDev
---
# ADR: Plan Archival Strategy for Token Efficiency

**Status:** Accepted
**Date:** 2025-11-21
**Context:** Long-running projects with multi-phase implementation plans

## Problem Statement

As implementation plans grow (10+ phases, 3000+ lines), reading the entire plan document becomes increasingly inefficient:

- **Token Waste:** Reading 60K tokens when only 10K are relevant (90% waste)
- **Context Pollution:** Irrelevant completed phases consume context window
- **Scalability Issues:** Plans with 30+ phases would exceed 100K tokens
- **Performance:** Large file reads are slower and more expensive
- **Cognitive Load:** AI must process irrelevant historical context

### Real-World Example

HTTP Implementation Plan (Phase 13):
- Total size: 3,200 lines (~60,000 tokens)
- Active phases: 1 (Phase 14 hypothetically)
- Relevant content: 300 lines (~5,000 tokens)
- **Waste per read: 55,000 tokens (92%)**

## Decision

Implement a **phased archival strategy** where:
1. Completed phases are moved to individual archive files
2. Main plan contains only status summary + active phases
3. Archives are read on-demand when historical context needed
4. INDEX.md provides navigation across all plan documents

## Architecture

### Directory Structure

```
.ai/
├── INDEX.md                          # Central navigation
├── plans/
│   ├── PLAN_NAME.md                  # Main plan (lean)
│   ├── completed/
│   │   ├── PLAN_NAME.phase-01.md    # Archived phases
│   │   ├── PLAN_NAME.phase-02.md
│   │   └── ...
│   └── templates/
│       └── EXAMPLE_PLAN.md           # Plan template
```

### Main Plan Structure

Lean document containing:
- Overview and objectives
- Status table (all phases with links)
- Active phase(s) details only
- Next steps

**Example:**
```markdown
# Plan Name

## Status Overview
| Phase | Status | Date | Commit | Archive |
|-------|--------|------|--------|---------|
| 1 | ✅ | 2025-11-20 | abc123 | [Details](./completed/PLAN.phase-01.md) |
| 14 | ⏳ ACTIVE | - | - | See below |

## Active Phases

### Phase 14: Current Work
[Full implementation details]
```

**Size:** ~500-1000 lines (~10K tokens)

### Archived Phase Structure

Individual files for each completed phase:
- Metadata (status, date, commit)
- Complete implementation details
- Results and outcomes
- Links back to main plan

**Example:**
```markdown
# Plan Name - Phase 5: Documentation

**Status:** ✅ COMPLETED
**Date:** 2025-11-20
**Commit:** abc123
**Plan:** [Back to main plan](../PLAN_NAME.md)

[Complete phase details from original plan]
```

**Size:** ~200-500 lines per phase (~4-8K tokens)

### INDEX.md Structure

Central navigation document:
```markdown
# Project Index

## Active Plans
- [Plan Name](./plans/PLAN_NAME.md)
  - Status: Phase 14/20 (70% complete)
  - [View archived phases](./plans/completed/)

## Quick Links
- [Recent Phase](./plans/completed/PLAN.phase-13.md)
```

**Size:** ~100-200 lines (~2K tokens)

## Token Efficiency Analysis

### Comparison Table

| Scenario | Single Doc | Archived | Savings |
|----------|-----------|----------|---------|
| Read active phase | 60K | 10K | 83% |
| Reference old phase | 60K | 14K | 77% |
| Plan next phase | 60K | 22K | 63% |
| **Average** | **60K** | **15K** | **75%** |

### Projected Savings

**10 plan reads during development:**
- Single document: 600K tokens
- Archived: 150K tokens
- **Savings: 450K tokens (75%)**

**30-phase project:**
- Single document: 110K tokens per read
- Archived: 15K tokens per read
- **Savings: 95K tokens (86%)**

## Implementation Guidelines

### When to Archive a Phase

Archive immediately when:
1. Phase status changed to ✅ COMPLETED
2. Commit created for phase
3. CHANGELOG updated
4. Moving to next phase

### Archival Process

```bash
# 1. Extract phase content
# Copy phase details to new file

# 2. Create archive file
# File: .ai/plans/completed/PLAN_NAME.phase-XX.md

# 3. Update main plan
# Replace phase details with summary + link

# 4. Update INDEX.md
# Add phase to completed list

# 5. Commit changes
# "docs: Archive Phase XX to improve plan efficiency"
```

### Archive File Naming

Format: `PLAN_NAME.phase-XX.md`
- `PLAN_NAME`: Same as main plan filename (without .md)
- `phase-XX`: Two-digit phase number (01, 02, ..., 99)

Examples:
- `HTTP_IMPLEMENTATION.phase-01.md`
- `HTTP_IMPLEMENTATION.phase-13.md`
- `API_REDESIGN.phase-05.md`

### Content Migration

**Main Plan - Keep:**
- Phase status, date, commit
- Link to archived details
- Brief outcome summary (1-2 lines)

**Archive File - Include:**
- All original implementation details
- Step-by-step instructions
- Code examples
- Success criteria
- Commit messages
- Results and outcomes

## Benefits

### Token Efficiency
- **75-85% reduction** in token usage for typical operations
- More context available for actual work
- Faster processing times

### Scalability
- Can handle projects with 50+ phases
- No degradation as project grows
- Sustainable for multi-year projects

### Organization
- Clear separation of active vs. completed work
- Easy navigation with INDEX.md
- Historical context preserved but not in the way

### Performance
- Smaller file reads (faster)
- Less AI processing overhead
- Better context window utilization

### Maintainability
- Focused context for current work
- Easy to reference past decisions
- Clean separation of concerns

## Tradeoffs

### Added Complexity
- More files to manage
- Need to maintain INDEX.md
- Archival process adds steps

**Mitigation:** Automate with scripts or follow strict .rules

### Historical Context Loss
- Can't see full plan at once
- Need to read multiple files for full picture

**Mitigation:** Main plan status table provides overview, archives linked

### File Proliferation
- Many small files in completed/

**Mitigation:** Clear naming convention, organized by plan

## Alternatives Considered

### 1. Keep Single Document
**Rejected:** Doesn't scale, wastes tokens, poor performance

### 2. Delete Completed Phases
**Rejected:** Loses historical context, can't reference past decisions

### 3. Compress Completed Phases
**Rejected:** Still consumes tokens, harder to read when needed

### 4. External Documentation System
**Rejected:** Adds dependency, complicates workflow

## Success Metrics

### Token Usage
- Target: <15K tokens for typical plan read
- Current: 60K tokens (single document)
- **Expected improvement: 75%**

### File Count
- Target: <50 files per plan (manageable)
- Average: ~2-3 files per phase (main + archives)

### Accessibility
- Target: <30 seconds to find any phase details
- Method: INDEX.md + clear naming

### Adoption
- Target: All new plans use archival structure
- Existing plans: Migrate when exceeding 10 phases

## Implementation Status

- [x] ADR documented
- [ ] Template created
- [ ] HTTP plan archived
- [ ] INDEX.md populated
- [ ] .rules updated

## References

- `.rules` - Rule 7: Plan archival requirements
- `.ai/templates/EXAMPLE_PLAN.md` - Plan template with archival
- `.ai/INDEX.md` - Central project index

## Related Decisions

- **Token Budget Management:** How we manage context window usage
- **Documentation Structure:** Where different types of docs live
- **Plan Organization:** How we structure implementation plans

---

**Next Review:** After 5 plans use archival structure
**Owner:** Development team
**Tags:** #architecture #efficiency #documentation #planning
