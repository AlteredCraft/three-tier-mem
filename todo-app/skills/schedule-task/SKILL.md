---
name: schedule-task
description: Task management with progressive disclosure patterns for efficient context usage. Search, create, update, and organize tasks without loading all entities.
version: 1.0.0
---

# Schedule Task Skill

This skill enables efficient task management through progressive disclosure patterns. It demonstrates how procedural knowledge (Tier 3) coordinates with dynamic memory (Tier 2) to handle 100+ tasks while maintaining low token usage.

## When to Use This Skill

Use this skill when the user wants to:
- Create new tasks
- Search for existing tasks
- Update task status or details
- List tasks by criteria (status, date, priority, project)
- Check for scheduling conflicts
- Organize and manage their task list

## Core Principle: Progressive Disclosure

**NEVER load all tasks at once.** Always search/filter first, then load only what's needed.

**Pattern:**
1. Search → 2. Filter → 3. Load specific files

## Task File Format

Tasks are stored in `memories/tasks/` with this structure (see CLAUDE.md for full spec):

```markdown
---
id: task-001
title: Task description
date: 2025-11-15
status: pending
priority: high
created: 2025-11-01T10:30:00Z
project: project-name
---

Detailed task description and notes.
```

**Required fields:** id, title, date, status, created
**Status values:** pending, in_progress, completed, blocked
**Priority values:** low, medium, high, critical

## Using the Search Script

**Before loading any task files**, use the search script to filter:

```bash
uv run skills/schedule-task/scripts/search_tasks.py [OPTIONS]
```

**Options:**
- `--status pending` - Find tasks by status
- `--priority high` - Find tasks by priority
- `--date-after 2025-11-01` - Tasks due after date
- `--date-before 2025-11-20` - Tasks due before date
- `--project web-platform` - Tasks for specific project
- `--text deployment` - Full-text search in task content

**Examples:**
```bash
# Find all pending high-priority tasks
uv run skills/schedule-task/scripts/search_tasks.py --status pending --priority high

# Find tasks this week
uv run skills/schedule-task/scripts/search_tasks.py --date-after 2025-11-10 --date-before 2025-11-16

# Search for deployment-related tasks
uv run skills/schedule-task/scripts/search_tasks.py --text deployment
```

The script returns a list of matching file paths. **Read only these files**, not all tasks.

## Workflow Examples

### Creating a New Task

1. Determine the next available task ID (count existing: `ls memories/tasks/ | wc -l`)
2. Get task details from user (title, date, priority, etc.)
3. If date is relative ("next Tuesday"), calculate exact date - see `reference/date-handling.md` if needed
4. Use Write tool to create `memories/tasks/task-{id}.md` with proper format
5. Confirm task created to user

### Searching Tasks

1. Understand user's criteria (status? date range? priority?)
2. Run `search_tasks.py` with appropriate filters
3. Read only the matched task files
4. Present results to user (don't show raw file paths)

### Updating Task Status

1. Find the specific task (use search if needed)
2. Read the task file
3. Use Edit tool to update the status field in frontmatter
4. Confirm update to user

### Checking for Conflicts

1. Get the target date from user
2. Search for tasks on that date: `search_tasks.py --date-after DATE --date-before DATE`
3. Read matched tasks
4. Report conflicts if any exist

## Progressive Disclosure of References

Load reference files **only when needed**:

- **`reference/date-handling.md`**: Load when:
  - User provides relative dates ("next Tuesday", "in 3 days")
  - Date ambiguity or confusion occurs
  - Timezone considerations needed

- **`reference/examples.md`**: Load when:
  - User's task description is too vague
  - Formatting guidance needed
  - Examples would clarify expectations

## Token Efficiency

**Goal:** Keep typical operations under 1,500 tokens total

- Tier 1 (Static/CLAUDE.md): ~500 tokens (always loaded)
- Tier 2 (Dynamic/Tasks): ~500 tokens (2-3 matched tasks)
- Tier 3 (This skill): ~500 tokens (SKILL.md only, not references)

**Without progressive disclosure:** Loading all 100 tasks = ~15,000 tokens (10x over budget!)

**With progressive disclosure:** Search script + 2-3 tasks = ~1,000 tokens (under budget ✓)

## Error Handling

- If no tasks match search: Inform user, don't try to load non-existent files
- If task ID conflicts: Use next available ID
- If required fields missing: Re-prompt user for details
- If date parsing fails: Load `reference/date-handling.md` for guidance

## Important Reminders

1. **Always search before loading** - Use `search_tasks.py` to filter
2. **Load only matches** - Don't read all task files
3. **Keep references on-demand** - Load date-handling.md and examples.md only when confusion occurs
4. **Exact dates preferred** - Convert relative dates to YYYY-MM-DD format
5. **Confirm actions** - Tell user what you did ("Created task-010.md for deployment review on 2025-11-15")
