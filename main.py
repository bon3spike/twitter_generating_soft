#!/usr/bin/env python3
"""Main entry point with interactive menu for selecting functions."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))


def show_menu() -> None:
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("  Content Studio for Twitter/X")
    print("=" * 60)
    print("\nAvailable functions:\n")
    print("  1. Analyze existing posts (tone/style report)")
    print("  2. Generate new posts (save to CSV)")
    print("\n  0. Exit")
    print("\n" + "=" * 60)


def prompt_optional_int(prompt: str) -> int | None:
    try:
        value = input(prompt).strip()
    except KeyboardInterrupt:
        return None
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        print("❌ Invalid number. Using default value.")
        return None


async def run_analyze_posts() -> int:
    """Run analyze_posts.py with optional overrides."""
    try:
        input_path = input(
            "\nEnter path to analysis input file (press Enter for analysis_input.txt): "
        ).strip()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 1
    cmd = [sys.executable, str(BASE_DIR / "analyze_posts.py")]
    if input_path:
        cmd += ["--input", input_path]
    return subprocess.run(cmd).returncode


async def run_generate_posts() -> int:
    """Run generate_posts.py with optional count override."""
    count = prompt_optional_int("\nHow many posts to generate? (Enter to use default): ")
    cmd = [sys.executable, str(BASE_DIR / "generate_posts.py")]
    if count:
        cmd += ["--count", str(count)]
    return subprocess.run(cmd).returncode


def get_user_choice() -> int:
    """Get user's menu choice."""
    while True:
        try:
            choice = input("\nSelect function (0-2): ").strip()
            choice_num = int(choice)
            if 0 <= choice_num <= 2:
                return choice_num
            print("❌ Invalid choice. Enter a number between 0 and 2.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return 0


async def main() -> None:
    """Main function with interactive menu."""
    while True:
        show_menu()
        choice = get_user_choice()

        if choice == 0:
            print("\n👋 Goodbye!")
            break

        print("\n" + "=" * 60)
        print(f"Running function {choice}...")
        print("=" * 60 + "\n")

        try:
            if choice == 1:
                exit_code = await run_analyze_posts()
            elif choice == 2:
                exit_code = await run_generate_posts()
            else:
                print("❌ Unknown function")
                exit_code = 1

            if exit_code == 0:
                print("\n✅ Function completed successfully!")
            else:
                print(f"\n❌ Function completed with errors (exit code: {exit_code})")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as error:  # noqa: BLE001
            print(f"\n❌ Error: {error}")
            import traceback

            traceback.print_exc()

        try:
            continue_choice = input(
                "\nPress Enter to return to menu, or 'q' to quit: "
            ).strip().lower()
            if continue_choice == "q":
                print("\n👋 Goodbye!")
                break
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

