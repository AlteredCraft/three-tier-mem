# Task Management Agent - Static Memory (Tier 1)

This file contains always-loaded facts and preferences for the task management agent. This is **Tier 1** of the three-tier memory system and is loaded in every request (~500 token budget).

## Three-Tier Memory Architecture

### Tier 1: Static Memory (This File)
**Always loaded in every request**
- User preferences and configuration
- System-level facts that never change
- Date/time formats and conventions
- Budget: ~500 tokens
- Location: `CLAUDE.md` (this file)

### Tier 2: Dynamic Memory
**Progressively loaded via search/grep**
- Task entities stored as individual markdown files
- Files only loaded when relevant to current query
- Use grep/search to filter before loading
- Budget: Variable (only load what's needed)
- Location: `memories/tasks/*.md`
- Tools: Write (create), Read (load), Bash with grep (search)

### Tier 3: Task Memory (Skills)
**On-demand procedural knowledge**
- Complex procedures loaded only when invoked
- Each skill has SKILL.md, reference/ docs, and scripts/
- Progressive disclosure: load reference/ only when needed
- Budget: Variable (loaded on skill invocation)
- Location: `skills/*/`

## User Preferences

### Date and Time Format
- Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
- Display dates as: `YYYY-MM-DD`
- Current timezone: UTC (adjust as needed)

### Task Management Style
- Clear, concise task descriptions
- Use YAML frontmatter for task metadata
- Status values: `pending`, `in_progress`, `completed`, `blocked`
- Priority values: `low`, `medium`, `high`, `critical`

### Progressive Disclosure Guidelines
- **ALWAYS** search/grep before loading files
- Load only the minimum context needed
- Prefer script-based filtering over loading all entities
- Typical query: ~500 tokens static + ~500 tokens dynamic = 1000 tokens total
- Avoid loading all 100+ tasks (would be 15,000+ tokens)

## Tier 2: Task File Format

Tasks are stored in `memories/tasks/` as individual markdown files with YAML frontmatter:

```markdown
---
id: task-001
title: Deploy to production
date: 2025-11-15
status: pending
priority: high
created: 2025-11-01T10:30:00Z
---

Review deployment checklist and coordinate with DevOps team.
Ensure all tests pass before deploying.
```

**Required fields:**
- `id`: Unique identifier (e.g., task-001, task-002)
- `title`: Short task description
- `date`: Due date in YYYY-MM-DD format
- `status`: One of: `pending`, `in_progress`, `completed`, `blocked`
- `created`: ISO 8601 timestamp of creation

**Optional fields:**
- `priority`: One of: `low`, `medium`, `high`, `critical`
- `tags`: Comma-separated tags
- `project`: Project name

## Working with Dynamic Memory (Tier 2)

### Creating Tasks
Use the **Write** tool to create new task files:
```
File: memories/tasks/task-{next-id}.md
Content: (markdown with YAML frontmatter as shown above)
```

### Searching Tasks (Progressive Disclosure)
**ALWAYS search before loading!** Use **Bash** tool with grep:

```bash
# Find tasks by status
grep -l "status: pending" memories/tasks/*.md

# Find tasks by date range
grep -l "date: 2025-11" memories/tasks/*.md

# Find tasks by keyword in content
grep -l "deployment" memories/tasks/*.md

# Combine with other tools to count matches
grep -l "status: pending" memories/tasks/*.md | wc -l
```

### Loading Tasks
After searching, use **Read** tool to load ONLY the matched files:
```
Read: memories/tasks/task-001.md
Read: memories/tasks/task-005.md
```

### Updating Tasks
Use **Edit** tool to modify specific fields without loading full file first.

## Memory System Commands

When working with tasks:
- **Search first**: Use grep to find relevant tasks (examples above)
- **Load selectively**: Only read the specific files matched by search
- **Create atomically**: Each task is a separate file with unique ID
- **Update carefully**: Modify only the fields that changed
- **Never load all**: Avoid `Read memories/tasks/*.md` - always filter first

## Token Budget Goals

The three-tier system aims to keep typical operations under 1,500 tokens from memory:
- Tier 1 (Static): ~500 tokens (this file)
- Tier 2 (Dynamic): ~500 tokens (2-3 task files after search)
- Tier 3 (Skills): ~500 tokens (skill directive, not full reference)

This represents a **30x reduction** compared to eagerly loading all 100 tasks at once.
