#!/usr/bin/env python3
"""
Skill Discovery Script

Scans the skills/ directory and extracts metadata from SKILL.md frontmatter.
Returns a JSON list of available skills with their names and descriptions.

This enables lightweight skill discovery without loading full skill content,
supporting the progressive disclosure pattern in the three-tier memory system.

Usage:
    python scripts/list_skills.py

Output:
    JSON array of skill objects with name, description, and path
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional


def parse_frontmatter(content: str) -> Optional[Dict[str, str]]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Markdown file content

    Returns:
        Dictionary of frontmatter fields, or None if no frontmatter found
    """
    # Match YAML frontmatter between --- delimiters
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None

    frontmatter_text = match.group(1)
    frontmatter = {}

    # Parse simple YAML (key: value pairs)
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter


def discover_skills(skills_dir: Path) -> List[Dict[str, str]]:
    """
    Discover all skills in the skills directory.

    Args:
        skills_dir: Path to the skills directory

    Returns:
        List of skill metadata dictionaries
    """
    skills = []

    # Check if skills directory exists
    if not skills_dir.exists():
        return skills

    # Scan each subdirectory in skills/
    for skill_path in sorted(skills_dir.iterdir()):
        if not skill_path.is_dir():
            continue

        # Look for SKILL.md file
        skill_md_path = skill_path / "SKILL.md"
        if not skill_md_path.exists():
            continue

        # Read and parse SKILL.md
        try:
            content = skill_md_path.read_text()
            frontmatter = parse_frontmatter(content)

            if not frontmatter:
                # No frontmatter found, skip this skill
                continue

            # Extract required fields
            skill_info = {
                "name": frontmatter.get("name", skill_path.name),
                "description": frontmatter.get("description", "No description available"),
                "path": f"skills/{skill_path.name}",
            }

            # Optional fields
            if "version" in frontmatter:
                skill_info["version"] = frontmatter["version"]

            skills.append(skill_info)

        except Exception as e:
            # Skip skills that can't be read
            print(f"Warning: Could not read {skill_md_path}: {e}", file=sys.stderr)
            continue

    return skills


def main():
    """Main entry point for skill discovery."""
    # Determine script location and find skills directory
    script_dir = Path(__file__).parent
    app_dir = script_dir.parent  # todo-app/
    skills_dir = app_dir / "skills"

    # Discover skills
    skills = discover_skills(skills_dir)

    # Output as JSON
    print(json.dumps(skills, indent=2))

    return 0 if skills else 1


if __name__ == "__main__":
    sys.exit(main())
