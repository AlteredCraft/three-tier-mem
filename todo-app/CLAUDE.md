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

## Tier 3: Working with Skills

Skills are procedural knowledge packages loaded on-demand. They contain directives, scripts, and reference materials organized for progressive disclosure.

### Discovering Available Skills

**Before using any skill**, discover what's available:

```bash
uv run scripts/list_skills.py
```

This returns JSON with skill metadata (name, description, path):
```json
[
  {
    "name": "schedule-task",
    "description": "Task management with progressive disclosure...",
    "path": "skills/schedule-task"
  }
]
```

### Using a Skill

**When a task requires a skill:**

1. **Check relevance**: Is this task related to a discovered skill?
2. **Load SKILL.md**: `Read skills/{skill-name}/SKILL.md`
3. **Follow directives**: SKILL.md contains instructions and workflows
4. **Use scripts**: Run skill scripts via `python skills/{skill-name}/scripts/{script}.py`
5. **Progressive references**: Load `reference/*.md` files only when confusion occurs

### Example: Using schedule-task Skill

**When to load:**
- User wants to create/search/update tasks
- User asks about scheduling or task management
- Task-related queries need procedural guidance

**Workflow:**
```bash
# 1. Load the skill
Read skills/schedule-task/SKILL.md

# 2. Use scripts for filtering (before loading tasks!)
uv run skills/schedule-task/scripts/search_tasks.py --status pending --priority high

# 3. Load only matched task files
Read memories/tasks/task-001.md
Read memories/tasks/task-005.md

# 4. If date confusion occurs, load reference
Read skills/schedule-task/reference/date-handling.md

# 5. If examples needed
Read skills/schedule-task/reference/examples.md
```

### Progressive Disclosure with Skills

**Load order (from least to most tokens):**
1. Skill metadata (via list_skills.py) - minimal tokens
2. SKILL.md directives - ~500 tokens
3. Reference files - only when needed - ~300 tokens each
4. Scripts execute without context (output only)

**Don't:**
- Load all skills upfront
- Load SKILL.md if task doesn't need it
- Load all reference files (only on confusion)
- Read script source code (just execute and use output)

### Skill Guidelines

- **One skill at a time**: Load only the skill relevant to current task
- **Script outputs only**: Don't load script source, just run and use results
- **Reference on-demand**: Load reference/*.md only when directives aren't clear
- **Trust SKILL.md**: It contains the workflow, follow its instructions

## Token Budget Goals

The three-tier system aims to keep typical operations under 1,500 tokens from memory:
- Tier 1 (Static): ~500 tokens (this file)
- Tier 2 (Dynamic): ~500 tokens (2-3 task files after search)
- Tier 3 (Skills): ~500 tokens (SKILL.md only, not references)

**Typical workflow tokens:**
- list_skills.py output: ~50 tokens
- SKILL.md: ~500 tokens
- search_tasks.py output: ~50 tokens (just file paths)
- 2-3 task files: ~500 tokens
- Total: ~1,100 tokens

This represents a **30x reduction** compared to eagerly loading all 100 tasks at once.
