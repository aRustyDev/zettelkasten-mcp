# [Plan Name] Implementation Plan

**Created:** YYYY-MM-DD
**Status:** In Progress / Completed
**Owner:** Team/Individual
**Related:** [Links to related plans or docs]

---

## Overview

Brief description of what this plan aims to accomplish.

### Objectives
- Primary objective 1
- Primary objective 2
- Primary objective 3

### Success Criteria
- Measurable outcome 1
- Measurable outcome 2
- Measurable outcome 3

### Scope
**In Scope:**
- Feature/change 1
- Feature/change 2

**Out of Scope:**
- What's explicitly not included
- Future considerations

---

## Status Overview

| Phase | Status | Date | Commit | Archive Link |
|-------|--------|------|--------|--------------|
| 1 | ✅ | YYYY-MM-DD | abc1234 | [Details](./completed/PLAN_NAME.phase-01.md) |
| 2 | ✅ | YYYY-MM-DD | def5678 | [Details](./completed/PLAN_NAME.phase-02.md) |
| 3 | ⏳ ACTIVE | - | - | See below |
| 4 | ⏹️ PENDING | - | - | Planned |
| 5 | ⏹️ PENDING | - | - | Planned |

**Legend:**
- ✅ COMPLETED - Phase finished and archived
- ⏳ ACTIVE - Currently being implemented
- ⏹️ PENDING - Planned but not started
- ❌ BLOCKED - Blocked by dependency
- 🔄 IN REVIEW - Awaiting review/testing

**Progress:** X/Y phases complete (Z%)

---

## Phase Summary

### Completed Phases (Brief)

**Phase 1: [Phase Name]** ✅
- Objective: Brief description
- Outcome: What was delivered
- Commit: abc1234
- [Full details](./completed/PLAN_NAME.phase-01.md)

**Phase 2: [Phase Name]** ✅
- Objective: Brief description
- Outcome: What was delivered
- Commit: def5678
- [Full details](./completed/PLAN_NAME.phase-02.md)

### Blocked/Deferred Phases

**Phase X: [Phase Name]** ❌
- Blocker: Description of what's blocking progress
- Resolution: How to unblock
- Target: When expected to resume

---

## Active Phases (Full Details)

### ⏳ Phase 3: [Current Phase Name]

**Date:** Started YYYY-MM-DD
**Status:** In Progress
**Objective:** What this phase aims to accomplish

#### Prerequisites
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

#### Steps

##### Step 3.1: [Step Name]
**File/Location:** `path/to/file.ext`

**Action:** Detailed description of what to do

**Implementation:**
```language
// Code example or configuration
```

**Rationale:** Why this approach was chosen

**Time Estimate:** X minutes/hours

##### Step 3.2: [Step Name]
[Same structure as 3.1]

##### Step 3.3: [Step Name]
[Same structure as 3.1]

#### Testing
```bash
# Commands to verify implementation
command1
command2
```

**Expected Results:**
- Output/behavior 1
- Output/behavior 2

#### Documentation Updates
- [ ] Update README.md
- [ ] Update CHANGELOG.md
- [ ] Add/update ADR if needed
- [ ] Update user documentation
- [ ] Update developer documentation

#### Success Criteria
- ✅ Criteria 1 met
- ✅ Criteria 2 met
- ✅ Criteria 3 met

#### Time Estimate
- **Estimated:** X hours
- **Actual:** Y hours (update when complete)

#### Commit Message Template
```
type: Brief description

Detailed description of changes made in this phase.

Implementation:
- Change 1
- Change 2

Testing:
- Test results
- Coverage: X%

Documentation:
- Updated files list

[Related issue/ticket]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Pending Phases (Planning Only)

### ⏹️ Phase 4: [Next Phase Name]

**Objective:** Brief description
**Dependencies:** Phase 3 complete
**Estimated Effort:** X hours

**High-level approach:**
1. Step 1
2. Step 2
3. Step 3

### ⏹️ Phase 5: [Future Phase Name]

**Objective:** Brief description
**Dependencies:** Phase 4 complete
**Estimated Effort:** X hours

**High-level approach:**
1. Step 1
2. Step 2
3. Step 3

---

## Architecture Decisions

### Key Technical Decisions
1. **Decision:** What was decided
   - **Rationale:** Why
   - **Alternatives Considered:** What else was considered
   - **Tradeoffs:** Pros/cons

2. **Decision:** Another decision
   - **Rationale:** Why
   - **Alternatives Considered:** What else
   - **Tradeoffs:** Pros/cons

### ADRs Created
- [ADR Title](../docs/project-knowledge/dev/adr-name.md) - Brief description

---

## Dependencies

### External Dependencies
- Dependency 1 - Version/status
- Dependency 2 - Version/status

### Internal Dependencies
- Feature/module 1 must be complete
- Configuration X must be set

### Blockers
- [ ] Blocker 1 - Description and owner
- [ ] Blocker 2 - Description and owner

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Risk 1 | High/Med/Low | High/Med/Low | How to mitigate |
| Risk 2 | High/Med/Low | High/Med/Low | How to mitigate |

---

## Testing Strategy

### Unit Tests
- Test coverage target: X%
- Key test scenarios:
  1. Scenario 1
  2. Scenario 2

### Integration Tests
- Integration points to test:
  1. Point 1
  2. Point 2

### Manual Testing
- [ ] Test case 1
- [ ] Test case 2
- [ ] Test case 3

---

## Rollback Plan

### If Phase X Fails
1. Step to rollback
2. Step to rollback
3. Recovery procedure

### Compatibility
- **Backward Compatible:** Yes/No
- **Migration Required:** Yes/No
- **Breaking Changes:** List any

---

## Timeline

| Phase | Est. Start | Est. End | Actual Start | Actual End | Status |
|-------|-----------|----------|--------------|------------|--------|
| 1 | YYYY-MM-DD | YYYY-MM-DD | YYYY-MM-DD | YYYY-MM-DD | ✅ |
| 2 | YYYY-MM-DD | YYYY-MM-DD | YYYY-MM-DD | YYYY-MM-DD | ✅ |
| 3 | YYYY-MM-DD | YYYY-MM-DD | YYYY-MM-DD | - | ⏳ |
| 4 | YYYY-MM-DD | YYYY-MM-DD | - | - | ⏹️ |
| 5 | YYYY-MM-DD | YYYY-MM-DD | - | - | ⏹️ |

**Total Estimated Time:** X hours/days
**Time Spent:** Y hours/days
**Remaining:** Z hours/days

---

## Resources

### Documentation
- [Related Doc 1](path/to/doc)
- [Related Doc 2](path/to/doc)

### External References
- [External Resource 1](url)
- [External Resource 2](url)

### Tools Required
- Tool 1 - Version X.Y
- Tool 2 - Version X.Y

---

## Future Enhancements

Ideas for future iterations:
1. Enhancement 1 - Description
2. Enhancement 2 - Description
3. Enhancement 3 - Description

---

## Notes

### Lessons Learned
- Lesson 1
- Lesson 2

### Open Questions
- [ ] Question 1
- [ ] Question 2

### Deviations from Plan
- **Original Plan:** What was originally planned
- **Actual Implementation:** What was actually done
- **Reason:** Why the change was made

---

## Archival Instructions

When a phase is completed:

1. **Extract phase content** to `.ai/plans/completed/PLAN_NAME.phase-XX.md`
2. **Update status table** above with ✅ and archive link
3. **Replace phase details** in this file with brief summary
4. **Update INDEX.md** to reflect completion
5. **Commit changes** with message: `docs: Archive Phase XX`

### Archive File Template

```markdown
# [Plan Name] - Phase X: [Phase Name]

**Status:** ✅ COMPLETED
**Date:** YYYY-MM-DD
**Commit:** abc1234
**Plan:** [Back to main plan](../PLAN_NAME.md)

## Overview
[Brief summary]

## Implementation
[All the detailed content from this plan]

## Results
- Outcome 1
- Outcome 2

## Lessons Learned
- Lesson 1
- Lesson 2
```

---

**Last Updated:** YYYY-MM-DD
**Next Review:** YYYY-MM-DD
