#!/usr/bin/env python3
"""
Task Management Agent with Three-Tier Memory System
Using direct Anthropic SDK for LLM-agnostic patterns

A demonstration of progressive disclosure for context window optimization:
- Tier 1 (Static): Always-loaded facts from CLAUDE.md (~500 tokens)
- Tier 2 (Dynamic): Progressively loaded entities via search/grep
- Tier 3 (Skills): On-demand procedural knowledge

Usage:
    uv run todo-app/agent.py              # Run agent
    uv run todo-app/agent.py --debug      # Show token usage breakdown
"""

import argparse
import asyncio
import glob as glob_module
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from anthropic import AsyncAnthropic
from dotenv import load_dotenv


# Tool definitions for file system operations and command execution
TOOLS = [
    {
        "name": "read_file",
        "description": "Read contents of a file from the filesystem. Returns the file content as text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates the file if it doesn't exist, overwrites if it does. Creates parent directories as needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "bash",
        "description": "Execute a bash command and return its output. Use for running scripts, searching files with grep, listing directories, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Bash command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "grep",
        "description": "Search for patterns in files using grep. Returns list of matching file paths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Pattern to search for (supports regex)"
                },
                "path": {
                    "type": "string",
                    "description": "File or directory path to search in (supports wildcards like *.md)"
                }
            },
            "required": ["pattern", "path"]
        }
    },
    {
        "name": "glob",
        "description": "Find files matching a glob pattern. Returns list of matching file paths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern (e.g., '*.py', 'src/**/*.md', 'memories/tasks/*.md')"
                }
            },
            "required": ["pattern"]
        }
    }
]


def validate_environment() -> None:
    """Validate that required environment variables are set."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment.", file=sys.stderr)
        print("\nSetup required:", file=sys.stderr)
        print("1. cd todo-app", file=sys.stderr)
        print("2. cp dist.env .env", file=sys.stderr)
        print("3. Edit .env and add your ANTHROPIC_API_KEY=sk-ant-...", file=sys.stderr)
        sys.exit(1)


def load_system_prompt(agent_dir: Path) -> str:
    """
    Load static memory (Tier 1) from CLAUDE.md.

    This replaces the Agent SDK's automatic setting_sources=["project"] loading.
    By loading manually, we make the static memory injection explicit and visible.

    Args:
        agent_dir: Path to the todo-app directory

    Returns:
        Complete system prompt including CLAUDE.md content
    """
    claude_md_path = agent_dir / "CLAUDE.md"

    if not claude_md_path.exists():
        raise FileNotFoundError(
            f"CLAUDE.md not found at {claude_md_path}. "
            "This file contains Tier 1 static memory and is required."
        )

    with open(claude_md_path, 'r') as f:
        claude_md_content = f.read()

    # Combine base instructions with static memory
    system_prompt = f"""You are a helpful task management assistant.
You help users organize, track, and complete their tasks effectively.
The system uses a three-tier memory architecture for efficient context management.

{claude_md_content}
"""

    return system_prompt


async def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Execute a tool and return its result as a string.

    This function implements the actual behavior of each tool. The tool definitions
    above tell Claude what tools exist and what parameters they accept. This function
    executes them when Claude decides to use them.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Dictionary of input parameters for the tool

    Returns:
        String result to send back to Claude in the agentic loop
    """
    try:
        if tool_name == "read_file":
            file_path = Path(tool_input["file_path"])

            if not file_path.exists():
                return f"Error: File not found: {file_path}"

            if not file_path.is_file():
                return f"Error: Path is not a file: {file_path}"

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            except UnicodeDecodeError:
                return f"Error: File appears to be binary and cannot be read as text: {file_path}"

        elif tool_name == "write_file":
            file_path = Path(tool_input["file_path"])
            content = tool_input["content"]

            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote {len(content)} characters to {file_path}"

        elif tool_name == "bash":
            command = tool_input["command"]

            # Execute command with timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )

            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"

            if result.returncode != 0:
                output += f"\nCommand exited with code {result.returncode}"

            return output if output.strip() else "Command completed successfully (no output)"

        elif tool_name == "grep":
            pattern = tool_input["pattern"]
            path = tool_input["path"]

            # Use grep to search for pattern
            result = subprocess.run(
                f"grep -l '{pattern}' {path}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.stdout:
                return result.stdout.strip()
            else:
                return "No matches found"

        elif tool_name == "glob":
            pattern = tool_input["pattern"]

            # Find files matching glob pattern
            matches = glob_module.glob(pattern, recursive=True)

            if not matches:
                return "No files matched the pattern"

            # Sort for consistent output
            return "\n".join(sorted(matches))

        else:
            return f"Error: Unknown tool: {tool_name}"

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing {tool_name}: {type(e).__name__}: {str(e)}"


async def agentic_loop(
    user_message: str,
    client: AsyncAnthropic,
    messages: List[Dict[str, Any]],
    system_prompt: str,
    debug: bool = False
) -> Tuple[str, Dict[str, int]]:
    """
    Main agentic loop handling tool use.

    This is the core pattern that the Agent SDK abstracts away. We implement it
    explicitly here for educational transparency and LLM-agnostic portability.

    Flow:
    1. Add user message to history
    2. Call Claude with current message history
    3. Check stop_reason in response:
       - "tool_use": Extract tool calls, execute them, add results, loop back to step 2
       - "end_turn"/"stop_sequence": Extract text response and return
       - "max_tokens": Handle truncation and return

    Args:
        user_message: The user's input message
        client: AsyncAnthropic client
        messages: Conversation history (mutated in place)
        system_prompt: System prompt including CLAUDE.md content
        debug: Whether to print debug information

    Returns:
        Tuple of (response_text, usage_stats)
    """
    # Add user message to conversation history
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Track cumulative token usage across turns in the loop
    total_usage = {
        "input_tokens": 0,
        "output_tokens": 0
    }

    # Agentic loop: continue until Claude provides a final answer
    while True:
        # Call Claude API
        response = await client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        # Accumulate token usage
        total_usage["input_tokens"] += response.usage.input_tokens
        total_usage["output_tokens"] += response.usage.output_tokens

        # Add Claude's response to conversation history
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Handle different stop reasons
        if response.stop_reason == "tool_use":
            # Claude wants to use tools - execute them and continue loop
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    if debug:
                        print(f"[Executing tool: {block.name}]", flush=True)

                    # Execute the tool
                    result = await execute_tool(block.name, block.input)

                    # Format result for Claude
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,  # Must match the tool_use block's id
                        "content": result
                    })

            # Add tool results as a user message
            messages.append({
                "role": "user",
                "content": tool_results
            })

            # Continue loop to get Claude's next response
            continue

        elif response.stop_reason in ["end_turn", "stop_sequence"]:
            # Claude provided a final answer - extract text and return
            text_parts = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)

            final_text = " ".join(text_parts)
            return final_text, total_usage

        elif response.stop_reason == "max_tokens":
            # Response was truncated - extract what we have and warn user
            text_parts = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)

            final_text = " ".join(text_parts) + "\n\n[Response truncated due to length]"
            return final_text, total_usage

        else:
            # Unexpected stop reason - return what we have
            text_parts = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)

            final_text = " ".join(text_parts)
            if not final_text:
                final_text = f"[Unexpected stop_reason: {response.stop_reason}]"

            return final_text, total_usage


def print_debug_info(usage: Dict[str, int], turn_count: int, duration_ms: int = 0) -> None:
    """
    Display detailed debug information about token usage.

    This replaces the Agent SDK's automatic ResultMessage debug output.

    Args:
        usage: Dictionary with input_tokens and output_tokens
        turn_count: Number of user turns in the conversation
        duration_ms: Optional duration in milliseconds
    """
    print("\n" + "=" * 60)
    print("DEBUG INFO")
    print("=" * 60)
    print(f"Turns: {turn_count}")
    if duration_ms > 0:
        print(f"Duration: {duration_ms}ms")
    print("\nToken Usage:")
    print(f"  Input Tokens: {usage['input_tokens']}")
    print(f"  Output Tokens: {usage['output_tokens']}")
    print(f"  Total Tokens: {usage['input_tokens'] + usage['output_tokens']}")
    print("=" * 60 + "\n")


async def run_agent(debug: bool = False) -> None:
    """
    Main agent loop with interactive conversation.

    This function manages the overall conversation flow, maintaining message history
    and calling the agentic loop for each user input.

    Args:
        debug: If True, display token usage and timing information after each interaction
    """
    # Get the todo-app directory (where this script is located)
    agent_dir = Path(__file__).parent.resolve()

    # Change working directory to todo-app/ for consistent file operations
    os.chdir(agent_dir)

    # Load system prompt (Tier 1: Static Memory)
    system_prompt = load_system_prompt(agent_dir)

    print("=" * 60)
    print("Task Management Agent (Three-Tier Memory Demo)")
    print("Using direct Anthropic SDK")
    print("=" * 60)
    print(f"Working Directory: {agent_dir}")
    if debug:
        print("Debug Mode: ENABLED (showing token usage)")
    print("Type 'exit' or 'quit' to stop, or Ctrl+C to interrupt")
    print("=" * 60 + "\n")

    try:
        # Initialize Anthropic client
        async with AsyncAnthropic() as client:
            # Initialize empty message history
            # This list will grow as the conversation progresses
            messages = []

            while True:
                try:
                    # Get user input
                    user_input = input("You: ").strip()

                    # Check for exit commands
                    if user_input.lower() in ["exit", "quit", "q"]:
                        print("\nGoodbye!")
                        break

                    # Skip empty input
                    if not user_input:
                        continue

                    # Run agentic loop with user input
                    import time
                    start_time = time.time()

                    response_text, usage = await agentic_loop(
                        user_input,
                        client,
                        messages,
                        system_prompt,
                        debug
                    )

                    duration_ms = int((time.time() - start_time) * 1000)

                    # Display Claude's response
                    print(f"\nAssistant: {response_text}\n")

                    # Show debug info if enabled
                    if debug:
                        turn_count = len([m for m in messages if m["role"] == "user"])
                        print_debug_info(usage, turn_count, duration_ms)

                except KeyboardInterrupt:
                    print("\n\nInterrupted. Type 'exit' to quit, or continue chatting.")
                    continue

                except Exception as e:
                    print(f"\nError: {e}", file=sys.stderr)
                    if debug:
                        import traceback
                        traceback.print_exc()
                    continue

    except Exception as e:
        print(f"\nFailed to initialize agent: {e}", file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """Parse arguments and run the agent."""
    # Load environment variables from .env file
    load_dotenv()

    # Validate environment before proceeding
    validate_environment()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Task Management Agent with Three-Tier Memory System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              Run the agent normally
  %(prog)s --debug      Show token usage and timing breakdown after each interaction

The agent uses a three-tier memory system:
- Tier 1 (Static): Always-loaded facts from CLAUDE.md (~500 tokens)
- Tier 2 (Dynamic): Progressively loaded task entities via search
- Tier 3 (Skills): On-demand procedural knowledge

This implementation uses the direct Anthropic SDK to demonstrate LLM-agnostic
patterns. Tool definitions, the agentic loop, and static memory loading are all
visible in the code for educational purposes.
        """
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (shows token usage, timing, and tool execution)"
    )

    args = parser.parse_args()

    # Run the async agent
    try:
        asyncio.run(run_agent(debug=args.debug))
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
