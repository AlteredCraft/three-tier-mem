# Implementation Milestones

## 1. Core Agent Infrastructure
- Set up Claude Agent SDK with memory tool support
- Implement basic agent.py with command-line interface
- Configure UV dependencies and environment management
- Establish debug mode flag for token usage visibility

## 2. Static Memory (Tier 1)
- Create `todo-app/static_memory/CLAUDE.md` with always-loaded facts
- Define user preferences, date formats, and system configuration
- Integrate static memory into agent system prompt (~500 token budget)

## 3. Dynamic Memory (Tier 2)
- Implement `memories/tasks/` directory structure
- Define task markdown format with YAML frontmatter
- Enable agent memory tool for creating/updating task files
- Add progressive disclosure: load only needed entities

## 4. Task Memory (Tier 3) - Skills System
- Create `skills/schedule-task/` with SKILL.md directives
- Build `search_tasks.py` grep utility for filtering without full context load
- Add `reference/` docs for progressive context loading
- Demonstrate on-demand skill invocation

## 5. Token Efficiency Validation
- Instrument debug mode with per-tier token tracking
- Generate 100+ sample tasks for scale testing
- Validate 30x token reduction vs eager loading
- Document real performance metrics

## 6. SQLite Migration Path (Optional)
- Create `schedule-task-sqlite/` alternative implementation
- Maintain identical skill interface with SQL backend
- Demonstrate migration strategy for scale thresholds
- Document when/why to migrate from files
