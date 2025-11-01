#!/usr/bin/env python3
"""
Task Management Agent with Three-Tier Memory System

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
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock


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


def print_debug_info(message: ResultMessage) -> None:
    """Display detailed debug information from a ResultMessage.

    Shows token usage breakdown, timing, and cost information to help
    understand context window usage across the three memory tiers.
    """
    print("\n" + "=" * 60)
    print("DEBUG INFO")
    print("=" * 60)

    # Session information
    if message.session_id:
        print(f"Session ID: {message.session_id}")

    # Turn and timing information
    print(f"Turns: {message.num_turns}")
    print(f"Duration: {message.duration_ms}ms")
    if message.duration_api_ms:
        print(f"API Duration: {message.duration_api_ms}ms")

    # Cost tracking
    if message.total_cost_usd is not None:
        print(f"Total Cost: ${message.total_cost_usd:.4f}")

    # Token usage breakdown
    if message.usage:
        print("\nToken Usage Breakdown:")
        usage = message.usage

        # Handle usage as either dict or object
        def get_token_value(key):
            if isinstance(usage, dict):
                return usage.get(key, 0)
            return getattr(usage, key, 0)

        input_tokens = get_token_value('input_tokens')
        output_tokens = get_token_value('output_tokens')
        cache_creation = get_token_value('cache_creation_input_tokens')
        cache_read = get_token_value('cache_read_input_tokens')

        print(f"  Input Tokens: {input_tokens}")
        print(f"  Output Tokens: {output_tokens}")

        if cache_creation > 0:
            print(f"  Cache Creation: {cache_creation}")
        if cache_read > 0:
            print(f"  Cache Read: {cache_read}")

        # Calculate total tokens
        total_tokens = input_tokens + output_tokens
        print(f"  Total Tokens: {total_tokens}")

    print("=" * 60 + "\n")


async def run_agent(debug: bool = False) -> None:
    """Main agent loop with interactive conversation.

    Args:
        debug: If True, display token usage and timing information after each interaction.
    """
    # Get the todo-app directory (where this script is located)
    agent_dir = Path(__file__).parent.resolve()

    # Configure agent options
    options = ClaudeAgentOptions(
        # System prompt provides context for task management
        system_prompt=(
            "You are a helpful task management assistant. "
            "You help users organize, track, and complete their tasks effectively. "
            "The system uses a three-tier memory architecture for efficient context management."
        ),

        # Enable core tools for file operations and system interaction
        allowed_tools=["Read", "Write", "Bash", "Grep", "Glob"],

        # Set working directory to todo-app/
        cwd=str(agent_dir),

        # Load CLAUDE.md from project settings (Tier 1: Static Memory)
        setting_sources=["project"],

        # Safety limit to prevent runaway costs
        max_budget_usd=1.00,
    )

    print("=" * 60)
    print("Task Management Agent (Three-Tier Memory Demo)")
    print("=" * 60)
    print(f"Working Directory: {agent_dir}")
    if debug:
        print("Debug Mode: ENABLED (showing token usage)")
    print("Type 'exit' or 'quit' to stop, or Ctrl+C to interrupt")
    print("=" * 60 + "\n")

    try:
        async with ClaudeSDKClient(options=options) as client:
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

                    # Send query to Claude
                    await client.query(user_input)

                    # Process responses
                    assistant_response = []
                    async for message in client.receive_response():
                        # Handle assistant messages (Claude's response)
                        if isinstance(message, AssistantMessage):
                            for block in message.content:
                                if isinstance(block, TextBlock):
                                    assistant_response.append(block.text)

                        # Handle result messages (usage/cost stats)
                        elif isinstance(message, ResultMessage):
                            # Display assistant's response
                            if assistant_response:
                                print(f"\nAssistant: {' '.join(assistant_response)}\n")
                                assistant_response = []

                            # Show debug info if enabled
                            if debug:
                                print_debug_info(message)

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
  %(prog)s --debug      Show token usage and cost breakdown after each interaction

The agent uses a three-tier memory system:
- Tier 1 (Static): Always-loaded facts (~500 tokens)
- Tier 2 (Dynamic): Progressively loaded entities via search
- Tier 3 (Skills): On-demand procedural knowledge
        """
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (shows token usage, timing, and cost breakdown)"
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
