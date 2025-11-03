# Task Creation Examples

**Progressive Disclosure**: This reference is loaded only when examples or clarification are needed. Don't load this unless the user's request is vague or you need formatting guidance.

## Good Task Examples

### Example 1: Specific Task with All Details
```markdown
---
id: task-042
title: Review Q4 security audit report
date: 2025-11-18
status: pending
priority: high
created: 2025-11-01T14:20:00Z
project: security
tags: audit, compliance, review
---

Review the Q4 security audit report from external auditors.
Focus on critical findings and create remediation plan.

Action items:
- [ ] Read full report (50 pages)
- [ ] Identify critical issues
- [ ] Draft remediation timeline
- [ ] Schedule team meeting to discuss findings
```

**Why it's good:**
- Specific, actionable title
- Exact date (not relative)
- Appropriate priority
- Clear description with concrete action items
- Relevant tags and project

### Example 2: Simple Task
```markdown
---
id: task-043
title: Update team wiki with new onboarding process
date: 2025-11-12
status: pending
priority: low
created: 2025-11-01T15:00:00Z
---

Add the new onboarding checklist and timeline to the team wiki.
Use the document Sarah shared last week as reference.
```

**Why it's good:**
- Clear, single purpose
- Reasonable date
- Appropriate low priority (not urgent)
- Sufficient context

### Example 3: Blocked Task
```markdown
---
id: task-044
title: Deploy database migration for user profiles
date: 2025-11-20
status: blocked
priority: critical
created: 2025-11-01T16:30:00Z
project: web-platform
tags: database, migration, deployment
---

Deploy the user profile schema migration to production.

**Blocked by:**
- Waiting for DBA review and approval
- Need maintenance window scheduled

**Checklist when unblocked:**
- [ ] Backup production database
- [ ] Run migration on staging
- [ ] Verify data integrity
- [ ] Deploy to production
- [ ] Monitor for 24 hours
```

**Why it's good:**
- Status accurately reflects blocker
- Explains what's blocking progress
- Has checklist ready for when unblocked
- Critical priority justified

## Bad Task Examples (Don't Do These)

### Bad Example 1: Too Vague
```markdown
---
id: task-045
title: Fix stuff
date: 2025-11-15
status: pending
priority: medium
created: 2025-11-01T17:00:00Z
---

Need to fix some things.
```

**Why it's bad:**
- "Fix stuff" is not actionable
- No context on what needs fixing
- No way to determine when it's complete
- Future you won't know what this meant

**Fix it:**
```markdown
title: Fix memory leak in background worker process
...
```

### Bad Example 2: Multiple Unrelated Tasks
```markdown
---
id: task-046
title: Deploy code, update docs, review PRs, fix bugs
date: 2025-11-15
status: pending
priority: high
created: 2025-11-01T17:15:00Z
---

Need to do all these things by next week.
```

**Why it's bad:**
- One task = one thing
- Can't track partial completion
- All different priorities mixed together
- Overwhelming and unfocused

**Fix it:** Split into 4 separate tasks with specific details and appropriate priorities

### Bad Example 3: Relative Date
```markdown
---
id: task-047
title: Send monthly report
date: next Friday
status: pending
priority: medium
created: 2025-11-01T17:30:00Z
---

Send the monthly report next Friday.
```

**Why it's bad:**
- "next Friday" is not ISO 8601 format
- Ambiguous (which Friday?)
- Won't parse correctly

**Fix it:**
```yaml
date: 2025-11-08
```

### Bad Example 4: Missing Required Fields
```markdown
---
id: task-048
title: Call client
---

Need to call the client about the project.
```

**Why it's bad:**
- Missing `date` (required)
- Missing `status` (required)
- Missing `created` timestamp (required)
- Won't follow standard format

**Fix it:** Add all required fields

## Edge Cases

### Edge Case 1: Task with Subtasks
For complex tasks, use checklist format in description:

```markdown
---
id: task-049
title: Complete onboarding for 3 new engineers
date: 2025-11-22
status: in_progress
priority: high
created: 2025-11-01T18:00:00Z
project: team
---

Onboard Alice, Bob, and Carol who start on November 15.

Progress:
- [x] Alice - laptop setup complete
- [x] Alice - accounts created
- [ ] Alice - team introduction meeting
- [x] Bob - laptop setup complete
- [ ] Bob - accounts created
- [ ] Carol - laptop setup complete
```

### Edge Case 2: Recurring Task Pattern
For tasks that repeat, create new task each time:

```markdown
---
id: task-050
title: Submit weekly status report - Week of Nov 10
date: 2025-11-15
status: pending
priority: medium
created: 2025-11-10T09:00:00Z
tags: recurring, status-report
---

Submit status report for the week of November 10-15.
Next report will be created as task-0XX for week of Nov 17.
```

**Note**: Each recurrence is a separate task. Don't reuse IDs.

## When to Use What Priority

| Priority | Use When | Example |
|----------|----------|---------|
| **critical** | Outage, security breach, blocking launch | "Fix production database connection failure" |
| **high** | Important deadline, affects others | "Deploy feature for client demo tomorrow" |
| **medium** | Normal priority work | "Implement user profile page" |
| **low** | Nice to have, no deadline pressure | "Refactor old utility functions" |

## Common Questions

**Q: Should I include every detail?**
A: Include enough for future you to understand. If you'll forget context in a week, add it.

**Q: How specific should titles be?**
A: Specific enough to understand at a glance. "Fix bug" ❌ vs "Fix login redirect bug on Safari" ✅

**Q: When should I use tags?**
A: When you want to group tasks across projects (like `security`, `tech-debt`, `documentation`)

**Q: Can I change task IDs?**
A: No. Task IDs are immutable once created. Create new tasks instead.
