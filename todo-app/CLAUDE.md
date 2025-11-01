# Task Management Agent - Static Memory (Tier 1)

This file contains always-loaded facts and preferences for the task management agent. This is **Tier 1** of the three-tier memory system and is loaded in every request (~500 token budget).

## Three-Tier Memory Architecture

### Tier 1: Static Memory (This File)
**Always loaded in every request**
- User preferences and configuration
- System-level facts that never change
- Date/time formats and conventions
- Budget: ~500 tokens
- Location: `static_memory/CLAUDE.md`

### Tier 2: Dynamic Memory
**Progressively loaded via search/grep**
- Task entities stored as individual markdown files
- Files only loaded when relevant to current query
- Use grep/search scripts to filter before loading
- Budget: Variable (only load what's needed)
- Location: `memories/tasks/*.md`

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

## Memory System Commands

When working with tasks:
- **Search first**: Use grep/search tools to find relevant tasks
- **Load selectively**: Only read the specific files matched by search
- **Create atomically**: Each task is a separate file with unique ID
- **Update carefully**: Modify only the fields that changed

## Token Budget Goals

The three-tier system aims to keep typical operations under 1,500 tokens from memory:
- Tier 1 (Static): ~500 tokens (this file)
- Tier 2 (Dynamic): ~500 tokens (2-3 task files after search)
- Tier 3 (Skills): ~500 tokens (skill directive, not full reference)

This represents a **30x reduction** compared to eagerly loading all 100 tasks at once.
