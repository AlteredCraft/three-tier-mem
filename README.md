# Three-Tier Agent Memory System

An experimental implementation demonstrating how memory systems scale through three tiers optimized for different context needs: static facts (always loaded), dynamic entities (progressively disclosed), and procedural knowledge (on-demand).

This is a working proof-of-concept showing how far file-based memory can scale using progressive disclosure patterns, with an optional SQLite migration path included.

## Core Concept

**The Constraint**: Context windows are the bottleneck in agent memory systems.

**The Solution**: Three-tier architecture where each tier uses a different loading strategy:

1. **Static Memory (Tier 1)** - Always loaded facts and preferences
2. **Dynamic Memory (Tier 2)** - Domain entities loaded progressively as needed
3. **Task Memory (Tier 3)** - Procedural knowledge (Skills) loaded on-demand

**Key Insight**: Files + progressive disclosure patterns handle surprising scale before you need databases.

## Tech Stack

- Python 3.13+ (UV-managed)
- Claude Agent SDK (with [memory tool](https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool)) (good [baseline agent example](https://github.com/anthropics/claude-cookbooks/blob/main/claude_agent_sdk/00_The_one_liner_research_agent.ipynb)
- Agent [Skills](https://docs.claude.com/en/api/skills-guide) support 
- Modern tooling: UV for dependency management

## Repository Structure

```
three-tier-mem/
├── README.md                          # Setup and usage
├── pyproject.toml                     # UV project configuration
├── dist.env                           # API key template
├── agent.py                           # Main agent implementation
├── CLAUDE.md                          # Global agent concerns and principles
├── static_memory/
│   └── CLAUDE.md                      # Tier 1: Always-loaded memory system facts
├── memories/                          # Tier 2: Dynamic memory (agent-managed)
│   └── tasks/
│       ├── task-001.md                # Example task
│       └── task-002.md                # Example task (100+ in demo)
├── skills/
│   ├── CLAUDE.md                      # Global skill concerns
│   └── schedule-task/                 # Tier 3: PRIMARY file-based implementation
│       ├── SKILL.md                   # Skill overview and directives
│       ├── reference/
│       │   ├── date-handling.md       # Best practices for dates
│       │   └── examples.md            # Few-shot examples
│       └── scripts/
│           └── search_tasks.py        # Grep utility for task files
└── schedule-task-sqlite/              # BONUS: Migration example (if needed)
    ├── README.md                      # Instructions for switching implementations
    ├── SKILL.md                       # Same interface, different storage
    ├── schema.sql                     # Simple task table
    └── task_db.py                     # SQL query utilities
```

## Setup

### Prerequisites
- Python 3.13 or higher
- [UV](https://github.com/astral-sh/uv) package manager
- Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd three-tier-mem
```

2. Copy and configure environment variables:
```bash
cp dist.env .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. Install dependencies (UV handles this automatically):
```bash
uv sync
```

### Running the Agent

```bash
uv run agent.py
```

With debug mode (shows token usage and context window contents):
```bash
uv run agent.py --debug
```

## How It Works

### Tier 1: Static Memory (`static_memory/CLAUDE.md`)

Always loaded into the system prompt on every interaction.

**Contains**:
- User preferences (date format, scheduling style)
- Memory system configuration
- Project context

**Cost**: ~500 tokens per request

**When to use**: Information needed for every interaction

### Tier 2: Dynamic Memory (`memories/tasks/*.md`)

Domain entities stored as individual files, loaded progressively as needed.

**Structure** (prescribed by skill):
```markdown
---
id: task-001
title: Deploy to production
date: 2025-10-28
status: pending
created: 2025-10-24T10:30:00Z
---

Review deployment checklist and coordinate with DevOps team.
```

**How it works**:
- Agent creates/updates via memory tool
- Skill scripts search and filter without loading all files
- Only relevant entities loaded into context

**Cost**: Only tokens for loaded entities (~500 tokens for typical operations vs 15,000 if loading all 100 tasks)

**When to use**: Data needed selectively based on context

### Tier 3: Task Memory (`skills/schedule-task/`)

Procedural knowledge (Skills) loaded on-demand when invoked.

**Components**:
- **SKILL.md**: Skill overview and directives
  - Date handling guidance
  - Task file structure specification
  - When to use helper scripts
- **reference/**: Additional context loaded progressively
  - `date-handling.md`: Best practices
  - `examples.md`: Few-shot examples
- **scripts/**: Utilities for searching/filtering
  - `search_tasks.py`: Grep utility for task files

**How it works**:
- Skill only loads when needed
- Scripts execute without loading full context
- Reference files provide additional guidance when confusion occurs

**Cost**: Only loaded when skill is invoked (~500 tokens)

**When to use**: Complex procedures not needed in every interaction

## Example Workflows

### Scenario 1: "What do I have scheduled this week?"

1. Agent invokes schedule-task skill (SKILL.md loads)
2. Skill uses `search_tasks.py` (script executes, returns task IDs)
3. Agent reads specific task files from `memories/tasks/`
4. **Token cost**: ~500 (vs 15,000 if loading all 100 tasks)
5. Agent responds with filtered list

### Scenario 2: "Schedule deployment review for next Tuesday"

1. Agent uses static memory to determine today's date context
2. Agent calculates exact date (2025-10-29)
3. Skill directives guide proper date format and structure
4. Agent creates `memories/tasks/task-003.md` via memory tool
5. **File operation**: Single write, no locking needed

### Scenario 3: "Check if I have any conflicts that day"

1. Skill already loaded from previous interaction
2. `search_tasks.py` filters by date (grep is fast!)
3. Agent reads only potentially conflicting tasks
4. **Performance**: Milliseconds for 100+ files
5. Responds without loading all tasks

## Progressive Disclosure in Action

**Without progressive disclosure**:
- Load all 100 tasks = 15,000 tokens
- Load full skill context every time
- Expensive and slow

**With progressive disclosure**:
- Load only SKILL.md initially = ~300 tokens
- Search via grep (no context cost)
- Load only relevant task files = ~200 tokens
- **Total**: ~500 tokens (30x reduction!)

## Debug Mode

The `--debug` flag provides visibility into:
- Static memory loaded at startup
- When skills load (and what files)
- What gets read from dynamic memory
- Token counts for each tier
- Total context window usage per interaction

This helps understand the efficiency gains from progressive disclosure.

## Performance Characteristics

### File-Based Scale
- **<5 entities** Load all (simple)
- **5-500 entities** Progressive disclosure with grep (this demo)
- **500-5,000 entities** Still works! Add indexing scripts
- **>5K entities** Consider alternatives (but you're building Jira at this point)

### Why Files Work at Scale
- Grep is fast (milliseconds for hundreds of files)
- No connection overhead
- No schema migrations
- Simple backup/version control
- Human-readable debugging

### Token Efficiency
**100 task files**:
- ~50KB on disk
- Loading all: 15,000 tokens (expensive!)
- With progressive disclosure: ~500 tokens for typical operations
- **30x reduction in context usage**

## SQLite Migration Path (Optional)

**Location**: `schedule-task-sqlite/` at repo root

**When you might want SQLite**:
- Multiple agents writing tasks simultaneously (ACID transactions)
- Complex queries like "tasks between date X and Y, grouped by project"
- JOIN operations across different entity types
- **Reality**: Most apps never hit these limits

**What changes** (minimal!):
- Same three-tier architecture
- Same skill interface
- Swap file operations for SQL queries
- Progressive disclosure still works (WHERE clauses)
- ~1 hour migration effort

**See**: `schedule-task-sqlite/README.md` for switching instructions

## Project Goals

This implementation demonstrates:
1. **Files scale**: 100+ tasks managed efficiently with real metrics
2. **Token savings**: 30x reduction through progressive disclosure
3. **Migration path**: SQLite option exists but rarely needed
4. **Modern setup**: UV-based project for easy reproduction
5. **Authentic metrics**: Real measurements from actual implementation

## Key Takeaways

- Memory systems are really about context window management
- Three tiers = three loading strategies
- Files + progressive disclosure scale surprisingly far
- The pattern (three tiers, progressive disclosure) is storage-agnostic
- Start simple with files, migrate only when you hit real limits (most never will)
- Since plain text file based, github could be your persistence solution
