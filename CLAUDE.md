# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository demonstrates a three-tier agent memory system architecture that optimizes context window usage through progressive disclosure patterns. The project is in early development stages, with the implementation planned to reside in the `todo-app/` directory.

**Core Architecture**: Three-tier memory system where each tier uses different loading strategies:
1. **Static Memory (Tier 1)**: Always-loaded facts and preferences (~500 tokens)
2. **Dynamic Memory (Tier 2)**: Domain entities loaded progressively as needed (agent-managed files)
3. **Task Memory (Tier 3)**: Procedural knowledge (Skills) loaded on-demand

**Key Design Principle**: Files + progressive disclosure patterns can scale to hundreds of entities before requiring databases. Use grep/search scripts to filter without loading full context.

## Development Setup

### Prerequisites
- Python 3.13+ (specified in pyproject.toml)
- UV package manager for dependency management
- Anthropic API key

### Installation
```bash
# Install dependencies
uv sync

# Configure environment (in todo-app/)
cd todo-app
cp dist.env .env
# Add ANTHROPIC_API_KEY to .env
```

### Running the Agent
```bash
# From repository root
uv run todo-app/agent.py

# With debug mode (shows token usage and context window contents)
uv run todo-app/agent.py --debug
```

## Repository Structure

**Root level**: Documentation of the three-tier memory concept and architecture
**todo-app/**: Complete implementation of the working demo application

Key directories (planned):
- `todo-app/static_memory/`: Tier 1 - Always-loaded memory system facts (CLAUDE.md)
- `todo-app/memories/tasks/`: Tier 2 - Dynamic memory entities (task-*.md files)
- `todo-app/skills/`: Tier 3 - On-demand procedural knowledge
  - Each skill contains: SKILL.md, reference/ docs, and scripts/ utilities
- `todo-app/schedule-task-sqlite/`: Optional SQLite migration example

## Architecture Patterns

### Memory Tier Guidelines

**Static Memory (static_memory/CLAUDE.md)**:
- User preferences, date formats, scheduling style
- Memory system configuration
- Project context
- Cost: ~500 tokens per request
- Use for: Information needed in every interaction

**Dynamic Memory (memories/tasks/*.md)**:
- Individual markdown files per entity with YAML frontmatter
- Agent creates/updates via memory tool
- Search/filter using scripts without loading all files
- Use for: Data needed selectively based on context
- Example structure:
  ```markdown
  ---
  id: task-001
  title: Deploy to production
  date: 2025-10-28
  status: pending
  created: 2025-10-24T10:30:00Z
  ---

  Task description here.
  ```

**Task Memory (skills/)**:
- SKILL.md: Skill overview and directives
- reference/: Additional context loaded progressively
- scripts/: Utilities for searching/filtering (Python)
- Use for: Complex procedures not needed in every interaction

### Progressive Disclosure Pattern

**Always prefer scripts over loading full context**:
- Use grep utilities (like `search_tasks.py`) to filter entities
- Load only the specific files needed after filtering
- Token efficiency: ~500 tokens typical vs 15,000 tokens loading all 100 tasks (30x reduction)

**File-based scale thresholds**:
- <5 entities: Load all directly
- 5-500 entities: Progressive disclosure with grep (this demo's target)
- 500-5,000 entities: Add indexing scripts
- >5K entities: Consider SQLite (migration path included in repo)

## Development Principles

### When Building Skills
- Keep SKILL.md focused on directives and when to use helper scripts
- Store detailed guidance in reference/ files (loaded progressively when needed)
- Provide Python scripts for filtering/searching without loading full context
- Maintain same skill interface whether using files or SQLite

### Working with the Memory System
- Static memory changes require careful consideration (always loaded)
- Dynamic memory files are agent-managed (create via memory tool)
- Files are the primary storage mechanism - no schema migrations needed
- Human-readable debugging: all entities are markdown with YAML frontmatter

### Token Budget Awareness
- Debug mode (`--debug` flag) shows token usage per tier
- Optimize for progressive disclosure over eager loading
- Target: Keep typical operations under 1,000 tokens from memory
- Grep is fast (milliseconds) - use it liberally

## Technology Stack

- **Python 3.13+**: Primary language
- **UV**: Dependency and environment management (replaces pip/venv)
- **Claude Agent SDK**: Agent implementation with memory tool support
- **Skills API**: On-demand procedural knowledge loading
- File system as primary storage (SQLite optional)

## SQLite Migration Path (Optional)

Located in `schedule-task-sqlite/` (when implemented):
- Same three-tier architecture
- Same skill interface
- Swap file operations for SQL queries
- Progressive disclosure via WHERE clauses
- ~1 hour migration effort

Only needed for:
- Concurrent writes from multiple agents (ACID transactions)
- Complex queries with JOINs across entity types
- Most applications never hit these limits
