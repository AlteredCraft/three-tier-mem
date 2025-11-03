# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository demonstrates a three-tier agent memory system architecture that optimizes context window usage through progressive disclosure patterns. The implementation resides in the `todo-app/` directory.

**Core Architecture**: Three-tier memory system where each tier uses different loading strategies:
1. **Static Memory (Tier 1)**: Always-loaded facts and preferences (~500 tokens)
2. **Dynamic Memory (Tier 2)**: Domain entities loaded progressively as needed (agent-managed files)
3. **Task Memory (Tier 3)**: Procedural knowledge (Skills) loaded on-demand

**Key Design Principle**: Files + progressive disclosure patterns can scale to hundreds of entities before requiring databases. Use grep/search scripts to filter without loading full context.

**Implementation Approach**: Uses direct Anthropic SDK with explicit tool definitions and agentic loop for LLM-agnostic, educational transparency. All patterns are portable to other LLMs (OpenAI, Gemini, etc.).

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

Key directories:
- `todo-app/CLAUDE.md`: Tier 1 - Always-loaded static memory (loaded explicitly via `load_system_prompt()`)
- `todo-app/memories/tasks/`: Tier 2 - Dynamic memory entities (task-*.md files)
- `todo-app/skills/`: Tier 3 - On-demand procedural knowledge
  - Each skill contains: SKILL.md, reference/ docs, and scripts/ utilities
- `todo-app/scripts/`: Utility scripts (skill discovery, etc.)
- `todo-app/agent.py`: Main agent with explicit agentic loop implementation

## Architecture Patterns

### Memory Tier Guidelines

**Static Memory (todo-app/CLAUDE.md)**:
- User preferences, date formats, scheduling style
- Memory system configuration
- Project context
- Cost: ~500 tokens per request
- Use for: Information needed in every interaction
- Implementation: Loaded explicitly via `load_system_prompt()` function (agent.py:124-156)

**Dynamic Memory (memories/tasks/*.md)**:
- Individual markdown files per entity with YAML frontmatter
- Agent creates/updates via `write_file` tool
- Search/filter using `bash`, `grep`, and `glob` tools without loading all files
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
- **Anthropic SDK**: Direct API with explicit tool definitions and agentic loop
- **LLM-Agnostic Design**: Portable patterns that work with any tool-supporting LLM
- File system as primary storage (SQLite optional migration path in M5)

## Implementation Notes

**Agentic Loop** (agent.py:265-389):
- Explicit implementation of tool_use → execute → tool_result pattern
- Educational transparency: all steps visible in code
- Portable to other LLMs (OpenAI function calling, Gemini tool use, etc.)

**Tool Definitions** (agent.py:30-109):
- Custom JSON schemas for: `read_file`, `write_file`, `bash`, `grep`, `glob`
- Direct implementation in `execute_tool()` function
- No SDK magic - all behavior is explicit

**Static Memory Loading** (agent.py:124-156):
- Manual file reading of CLAUDE.md at startup
- Injected into `system` parameter on API calls
- Replaces SDK's automatic `setting_sources` loading

**Migration History**:
- Originally implemented with Claude Agent SDK for rapid prototyping (M1-M3)
- Migrated to direct Anthropic SDK for educational transparency and LLM portability
- Three-tier memory architecture remained unchanged, proving pattern portability

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
