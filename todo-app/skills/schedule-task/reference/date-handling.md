# Date Handling Best Practices

**Progressive Disclosure**: This reference is loaded only when date confusion or ambiguity occurs. Don't load this unless you need date handling guidance.

## Format Standard

**Always use ISO 8601 format for dates: `YYYY-MM-DD`**

Examples:
- ✅ `2025-11-15`
- ✅ `2025-12-01`
- ❌ `11/15/2025` (ambiguous)
- ❌ `Nov 15` (missing year)
- ❌ `next Tuesday` (relative, unclear)

## Converting Relative Dates

When users provide relative dates, convert to absolute dates:

| User Says | You Calculate | Example Result |
|-----------|---------------|----------------|
| "tomorrow" | today + 1 day | 2025-11-02 |
| "next Tuesday" | Find next Tuesday from today | 2025-11-05 |
| "in 3 days" | today + 3 days | 2025-11-04 |
| "next week" | Clarify specific day needed | Ask user |
| "end of month" | Last day of current month | 2025-11-30 |

**Important**: If today's date is not in context, ask the user or check system time. Don't assume.

## Common Pitfalls

### 1. Ambiguous Dates
**Problem**: "Schedule for 12/01"
- US format? December 1st
- European format? January 12th

**Solution**: Always confirm or use YYYY-MM-DD format

### 2. Missing Year
**Problem**: "Deploy on March 15"
- This year or next year?

**Solution**: Ask user or infer from context (if in November, "March 15" likely means next year)

### 3. Relative Date Without Context
**Problem**: "Remind me next week"
- Which day next week?

**Solution**: Ask user for specific date

### 4. Timezone Assumptions
**Problem**: Task due "end of day"
- Which timezone?
- User's timezone vs system timezone

**Solution**: Use UTC by default (as specified in CLAUDE.md). Add time as `23:59:59Z` for "end of day"

## Date Calculations

### Day of Week
If you need to calculate "next Tuesday":
1. Get current day of week
2. Calculate days until Tuesday
3. Add to current date

Example (if today is Friday, Nov 1):
- Days until Tuesday: (Tuesday index - Friday index + 7) % 7 = 4 days
- Result: 2025-11-05

### Month Boundaries
Be careful with month-end dates:
- "30 days from now" on Jan 31 = March 2 (not March 1)
- "End of February" = Feb 28 or Feb 29 (leap year!)

### Recurring Tasks
If implementing recurring tasks:
- Store next due date explicitly
- Recalculate after completion
- Don't rely on "every Tuesday" - always use specific dates

## When in Doubt

1. **Ask the user** for clarification
2. **Confirm the date** back to them ("Scheduling for November 15, 2025?")
3. **Use explicit formats** (YYYY-MM-DD)
4. **Default to UTC** timezone

## Examples

### Good Interactions

**User**: "Schedule deployment for next Tuesday"
**Agent**: "I'll schedule that for Tuesday, November 5, 2025. Is that correct?"

**User**: "Remind me in 3 days"
**Agent**: "I'll create a reminder for November 4, 2025."

### Bad Interactions (Don't Do This)

**User**: "Schedule for next week"
**Agent**: "Task created for November 10" ❌ (Which day? Not confirmed!)

**User**: "Deploy on 3/15"
**Agent**: "Scheduled for March 15" ❌ (Which year? Ambiguous format!)

## Integration with Task Format

In task files, always use:
```yaml
date: 2025-11-15
created: 2025-11-01T10:30:00Z
```

- `date`: Just the date (YYYY-MM-DD)
- `created`: Full timestamp with timezone (ISO 8601)
