#!/usr/bin/env python3
"""
Task Search Script

Efficiently search and filter task files without loading all content into memory.
Uses grep-based filtering to demonstrate progressive disclosure patterns.

This script is part of the schedule-task skill (Tier 3) and enables finding
relevant tasks from the dynamic memory pool (Tier 2) without token overhead.

Usage:
    python search_tasks.py [OPTIONS]

Examples:
    # Find all pending tasks
    python search_tasks.py --status pending

    # Find high-priority tasks due this week
    python search_tasks.py --priority high --date-after 2025-11-10 --date-before 2025-11-16

    # Search for deployment-related tasks
    python search_tasks.py --text deployment
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set


def search_by_field(tasks_dir: Path, field: str, value: str) -> Set[Path]:
    """
    Search tasks by a specific frontmatter field.

    Args:
        tasks_dir: Path to memories/tasks directory
        field: Field name (e.g., "status", "priority")
        value: Field value to match

    Returns:
        Set of matching task file paths
    """
    matches = set()
    pattern = f"{field}: {value}"

    for task_file in tasks_dir.glob("task-*.md"):
        try:
            content = task_file.read_text()
            if pattern in content:
                matches.add(task_file)
        except Exception:
            # Skip files that can't be read
            continue

    return matches


def search_by_date_range(tasks_dir: Path, after: str = None, before: str = None) -> Set[Path]:
    """
    Search tasks by date range.

    Args:
        tasks_dir: Path to memories/tasks directory
        after: Only include tasks on or after this date (YYYY-MM-DD)
        before: Only include tasks on or before this date (YYYY-MM-DD)

    Returns:
        Set of matching task file paths
    """
    matches = set()
    date_pattern = re.compile(r'^date: (\d{4}-\d{2}-\d{2})', re.MULTILINE)

    for task_file in tasks_dir.glob("task-*.md"):
        try:
            content = task_file.read_text()
            match = date_pattern.search(content)

            if not match:
                continue

            task_date = match.group(1)

            # Check date constraints
            if after and task_date < after:
                continue
            if before and task_date > before:
                continue

            matches.add(task_file)

        except Exception:
            # Skip files that can't be read
            continue

    return matches


def search_by_text(tasks_dir: Path, text: str) -> Set[Path]:
    """
    Full-text search across task content.

    Args:
        tasks_dir: Path to memories/tasks directory
        text: Text to search for (case-insensitive)

    Returns:
        Set of matching task file paths
    """
    matches = set()
    search_lower = text.lower()

    for task_file in tasks_dir.glob("task-*.md"):
        try:
            content = task_file.read_text()
            if search_lower in content.lower():
                matches.add(task_file)
        except Exception:
            # Skip files that can't be read
            continue

    return matches


def main():
    """Main entry point for task search."""
    parser = argparse.ArgumentParser(
        description="Search and filter task files using progressive disclosure patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --status pending                    # All pending tasks
  %(prog)s --priority high --status pending    # High-priority pending tasks
  %(prog)s --date-after 2025-11-10            # Tasks due after date
  %(prog)s --project web-platform             # Tasks for specific project
  %(prog)s --text deployment                  # Full-text search
        """
    )

    # Search filters
    parser.add_argument("--status", help="Filter by status (pending, in_progress, completed, blocked)")
    parser.add_argument("--priority", help="Filter by priority (low, medium, high, critical)")
    parser.add_argument("--project", help="Filter by project name")
    parser.add_argument("--date-after", help="Tasks on or after this date (YYYY-MM-DD)")
    parser.add_argument("--date-before", help="Tasks on or before this date (YYYY-MM-DD)")
    parser.add_argument("--text", help="Full-text search (case-insensitive)")

    args = parser.parse_args()

    # Find tasks directory
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent  # skills/schedule-task/
    app_dir = skill_dir.parent.parent  # todo-app/
    tasks_dir = app_dir / "memories" / "tasks"

    if not tasks_dir.exists():
        print("Error: memories/tasks directory not found", file=sys.stderr)
        return 1

    # Start with all tasks, then apply filters
    all_tasks = set(tasks_dir.glob("task-*.md"))
    matches = all_tasks

    # Apply field filters
    if args.status:
        status_matches = search_by_field(tasks_dir, "status", args.status)
        matches &= status_matches

    if args.priority:
        priority_matches = search_by_field(tasks_dir, "priority", args.priority)
        matches &= priority_matches

    if args.project:
        project_matches = search_by_field(tasks_dir, "project", args.project)
        matches &= project_matches

    # Apply date range filter
    if args.date_after or args.date_before:
        date_matches = search_by_date_range(tasks_dir, args.date_after, args.date_before)
        matches &= date_matches

    # Apply text search
    if args.text:
        text_matches = search_by_text(tasks_dir, args.text)
        matches &= text_matches

    # Output results (relative paths from todo-app/)
    sorted_matches = sorted(matches)

    if not sorted_matches:
        print("No tasks found matching criteria", file=sys.stderr)
        return 0

    for task_file in sorted_matches:
        # Output relative path from app directory
        relative_path = task_file.relative_to(app_dir)
        print(relative_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
