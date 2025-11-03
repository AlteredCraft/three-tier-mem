# Three-Tier Agent Memory System

An experimental implementation demonstrating how memory systems scale through three tiers optimized for different context needs: static facts (always loaded), dynamic entities (progressively disclosed), and procedural knowledge (on-demand).

This is a working proof-of-concept showing how far file-based memory can scale using progressive disclosure patterns. An LLM-agnostic approach that mimics SDK memory/skills patterns using standard tools.

## Core Concept

**The Constraint**: Context windows are the bottleneck in agent memory systems.

**The Solution**: Three-tier architecture where each tier uses a different loading strategy:

1. **Static Memory (Tier 1)** - Always loaded facts and preferences
2. **Dynamic Memory (Tier 2)** - Domain entities loaded progressively as needed
3. **Task Memory (Tier 3)** - Procedural knowledge (Skills), these are represented as scripts the LLM can reuse.

**Key Insight**: Files + progressive disclosure patterns handle surprising scale before you need more complex solutions. This LLM-agnostic implementation uses standard tools (Read/Write/Bash) rather than SDK-specific memory features, making the patterns portable and educational.

## Tech Stack

- Python 3.13+ (UV-managed)
- Claude Agent SDK (good [baseline agent example](https://github.com/anthropics/claude-cookbooks/blob/main/claude_agent_sdk/00_The_one_liner_research_agent.ipynb))
- LLM-agnostic patterns: mimics SDK [memory tool](https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool) and [Skills](https://docs.claude.com/en/api/skills-guide) using standard Read/Write/Bash tools
- Modern tooling: UV for dependency management

## Repository Structure

The companion app fully resides in the `todo-app/` folder. The root level contains learning documentation and project overview.

**Note**: `CLAUDE.md` exists at both levels:
- Root `CLAUDE.md`: Learning context and high-level architecture overview
- `todo-app/CLAUDE.md`: Agent's static memory (Tier 1) - always loaded by the agent

```
todo-app/
├── README.md                          # Setup and usage
├── dist.env                           # API key template
├── agent.py                           # Main agent implementation
├── CLAUDE.md                          # Tier 1: Always-loaded static memory
├── scripts/
│   └── list_skills.py                 # Skill discovery utility
├── memories/                          # Tier 2: Dynamic memory (agent-managed)
│   └── tasks/
│       ├── task-001.md                # Sample task files
│       ├── task-002.md                # (9 tasks included)
│       └── ...
└── skills/                            # Tier 3: Procedural knowledge
    ├── CLAUDE.md                      # Global skill directives
    └── schedule-task/                 # File-based task management skill
        ├── SKILL.md                   # Skill overview and directives
        ├── reference/
        │   ├── date-handling.md       # Date handling best practices
        │   └── examples.md            # Task creation examples
        └── scripts/
            └── search_tasks.py        # Progressive disclosure search utility
```

**Note**: The SQLite migration example (`schedule-task-sqlite/`) is planned for Milestone 5 and not yet implemented.

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

From repository root:
```bash
uv run todo-app/agent.py
```

With debug mode (shows token usage and context window contents):
```bash
uv run todo-app/agent.py --debug
```

Or from within `todo-app/` directory:
```bash
cd todo-app
uv run agent.py --debug
```

## How It Works

### Tier 1: Static Memory (`todo-app/CLAUDE.md`)

Always loaded into the system prompt on every interaction via SDK's `setting_sources=["project"]`.

**Contains**:
- User preferences (date format, scheduling style)
- Memory system configuration and guidelines
- Task file format specification
- Progressive disclosure instructions

**Cost**: ~500 tokens per request

**When to use**: Information needed for every interaction

**Implementation**: Standard CLAUDE.md file that agent SDK auto-loads from working directory via `setting_sources=["project"]`

### Tier 2: Dynamic Memory (`memories/tasks/*.md`)

Domain entities stored as individual files, loaded progressively as needed.

**Structure** (defined in CLAUDE.md):
```markdown
---
id: task-001
title: Deploy to production
date: 2025-11-15
status: pending
priority: high
created: 2025-11-01T10:30:00Z
project: web-platform
---

Review deployment checklist and coordinate with DevOps team.
```

**How it works**:
- Agent creates/updates task files using **Write** tool
- Agent searches via **Bash** tool with grep or Python scripts
- Agent loads only matched files using **Read** tool
- Progressive disclosure: search → filter → load only what's needed

**Cost**: Only tokens for loaded entities (typically ~500 tokens vs thousands for eager loading)

**Token Savings**: Significant reduction through progressive disclosure (target: 30x vs loading all entities)

**When to use**: Data needed selectively based on context

**Implementation**: Standard file operations with Read/Write/Bash tools - mimics SDK memory tool patterns but remains LLM-agnostic

### Tier 3: Task Memory (`skills/schedule-task/`)

Procedural knowledge (Skills) loaded on-demand when invoked. Uses portable SKILL.md format with standard Read/Write/Bash tools (hybrid approach).

**Architecture: Lightweight Skill Discovery**

Agent discovers skills without loading full content:
```bash
uv run scripts/list_skills.py
```

Returns JSON metadata:
```json
[
  {
    "name": "schedule-task",
    "description": "Task management with progressive disclosure...",
    "path": "skills/schedule-task"
  }
]
```

**Components**:
- **SKILL.md**: Skill overview with YAML frontmatter + directives
  - Progressive disclosure workflow
  - When to use helper scripts
  - When to load reference files
- **scripts/**: Python utilities executed via Bash tool
  - `search_tasks.py`: Filter tasks by status/priority/date/text
  - Returns file paths (not content) for selective loading
- **reference/**: Additional context loaded only when needed
  - `date-handling.md`: Best practices for date parsing
  - `examples.md`: Good/bad task creation examples

**How it works**:
1. Agent discovers skills via `list_skills.py` (minimal tokens)
2. When task-relevant, agent loads SKILL.md via Read tool
3. Scripts execute via Bash tool (output only, no source in context)
4. Reference files load progressively when confusion occurs
5. Progressive disclosure: metadata → skill → scripts → references

**Cost**: Only loaded when skill is invoked
- Skill metadata: ~50 tokens
- SKILL.md: ~500 tokens
- Script outputs: ~50 tokens (just file paths)
- References: ~300 tokens each (only if needed)

**Token Savings**: 30x reduction by not loading full skill content or all reference materials upfront

**When to use**: Complex procedures not needed in every interaction

**Implementation**: Portable SKILL.md format + standard tools (LLM-agnostic, upgrade path to Skills API if needed)

## Example Workflows

### Scenario 1: "What do I have scheduled this week?"

1. Agent checks available skills via `uv run scripts/list_skills.py`
2. Finds schedule-task skill, loads `skills/schedule-task/SKILL.md`
3. Skill directives instruct to use search_tasks.py before loading tasks
4. Agent runs: `uv run skills/schedule-task/scripts/search_tasks.py --date-after 2025-11-10 --date-before 2025-11-16`
5. Script returns 3 matching file paths
6. Agent reads only those 3 task files via Read tool
7. **Token cost**: ~1,100 total (50 metadata + 500 skill + 50 script output + 500 for 3 tasks)
8. **vs loading all tasks eagerly** = significant reduction through progressive disclosure
9. Agent responds with formatted task list

### Scenario 2: "Schedule deployment review for next Tuesday"

1. Agent uses static memory (CLAUDE.md) to determine date format preferences
2. Agent calculates exact date (2025-11-12)
3. CLAUDE.md provides task file format and structure
4. Agent creates `memories/tasks/task-010.md` using **Write** tool
5. **File operation**: Single write, no locking needed, human-readable format

### Scenario 3: "Check if I have any conflicts that day"

1. Skill already loaded from previous interaction
2. `search_tasks.py` filters by date (grep is fast!)
3. Agent reads only potentially conflicting tasks
4. **Performance**: Fast file-based filtering even at scale
5. Responds without loading all tasks

## Progressive Disclosure in Action

**Without progressive disclosure**:
- Load all tasks eagerly = thousands of tokens
- Load full skill context every time
- Expensive and slow

**With progressive disclosure**:
- Load only SKILL.md initially = ~500 tokens
- Search via grep/scripts (minimal context cost)
- Load only relevant task files = ~500 tokens
- **Total**: ~1,000 tokens typical (significant reduction vs eager loading)

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
**At scale**:
- Files are compact on disk
- Loading all eagerly: thousands of tokens (expensive!)
- With progressive disclosure: ~1,000 tokens for typical operations
- **Target: 30x reduction in context usage** (validation pending in Milestone 4)

## SQLite Migration Path (Optional - Milestone 5)

**Status**: Planned for Milestone 5, not yet implemented

**Location (future)**: `schedule-task-sqlite/` at repo root

**When you might want SQLite**:
- Multiple agents writing tasks simultaneously (ACID transactions)
- Complex queries like "tasks between date X and Y, grouped by project"
- JOIN operations across different entity types
- **Reality**: Most apps never hit these limits

**What will change** (minimal!):
- Same three-tier architecture
- Same skill interface
- Swap file operations for SQL queries
- Progressive disclosure still works (WHERE clauses)
- Estimated ~1 hour migration effort

This demonstrates the migration path when file-based storage reaches its limits.

## Project Goals

This implementation demonstrates:
1. **Files scale**: Progressive disclosure enables efficient management at scale
2. **Token savings**: Target 30x reduction through progressive disclosure (M4 validation)
3. **LLM-agnostic patterns**: Mimics SDK features using standard tools
4. **Migration path**: SQLite alternative planned (M5) when limits are reached
5. **Modern setup**: UV-based project for easy reproduction
6. **Educational value**: Clear visibility into memory tier mechanics

## Key Takeaways

- Memory systems are really about context window management
- Three tiers = three loading strategies (always, progressive, on-demand)
- Files + progressive disclosure scale surprisingly far before needing databases
- LLM-agnostic: Uses standard tools (Read/Write/Bash) rather than SDK-specific features
- The pattern (three tiers, progressive disclosure) is storage-agnostic
- Start simple with files, migrate only when hitting real limits (M5 explores this path)
- Plain text files work with version control and are human-readable for debugging
