"""Claude CLI integration for test-assistant."""
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ClaudeCodeRunner:
    """Handles interaction with claude CLI."""

    def __init__(self, prompt_template: str, dry_run: bool = False):
        """Initialize Claude runner.

        Args:
            prompt_template: Template prompt to use with claude
            dry_run: If True, skip Claude CLI execution
        """
        self.prompt_template = prompt_template
        self.dry_run = dry_run

    def check_claude_code_available(self) -> bool:
        """Check if claude CLI is available.

        Returns:
            True if claude is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def run_claude_code(self, file_path: Path) -> Optional[str]:
        """Run claude CLI with the specified file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Output from claude CLI, or None if error
        """
        # Construct the full prompt
        full_prompt = f"{self.prompt_template} {file_path}"

        logger.info(f"Running claude with file: {file_path}")
        logger.info(f"Prompt: {full_prompt}")

        print("\n" + "="*80)
        print(f"🤖 TRIGGERING CLAUDE CLI")
        print("="*80)
        print(f"File: {file_path}")
        print(f"Prompt: {full_prompt}")

        if self.dry_run:
            print("🔸 DRY RUN MODE: Claude CLI execution skipped")
            print("="*80 + "\n")
            logger.info("Dry run mode: skipping claude execution")
            return "DRY RUN MODE - No actual execution"

        print("="*80 + "\n")

        try:
            # Run claude with the -p flag for non-interactive output
            result = subprocess.run(
                ["claude", "-p", full_prompt],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Display output
            if result.stdout:
                print("CLAUDE OUTPUT:")
                print("-" * 80)
                print(result.stdout)
                print("-" * 80)

            if result.stderr:
                print("CLAUDE ERRORS:")
                print("-" * 80)
                print(result.stderr)
                print("-" * 80)

            if result.returncode != 0:
                logger.error(f"claude exited with code {result.returncode}")
                return None

            print("\n" + "="*80)
            print("✅ CLAUDE EXECUTION COMPLETED")
            print("="*80 + "\n")

            return result.stdout

        except subprocess.TimeoutExpired:
            logger.error("claude execution timed out")
            print("\n❌ ERROR: claude execution timed out\n")
            return None
        except Exception as e:
            logger.error(f"Error running claude: {e}")
            print(f"\n❌ ERROR: {e}\n")
            return None
