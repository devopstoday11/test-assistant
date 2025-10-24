"""File handling logic for test-assistant."""
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file renaming and management."""

    LATEST_SUFFIX = "-latest"

    def __init__(
        self,
        watch_dir: str,
        timestamp_format: str = "mmddyy-HH-MM-SS-AMPM",
        stability_timeout: float = 5.0,
        stability_check_interval: float = 0.1
    ):
        """Initialize file handler.

        Args:
            watch_dir: Directory being watched
            timestamp_format: Format for timestamp (e.g., mmddyy-HH-MM-SS-AMPM)
            stability_timeout: Max seconds to wait for file size to stabilize
            stability_check_interval: Interval between file size checks
        """
        self.watch_dir = Path(watch_dir)
        self.timestamp_format = timestamp_format
        self.stability_timeout = stability_timeout
        self.stability_check_interval = stability_check_interval

    def generate_timestamp(self) -> str:
        """Generate timestamp based on configured format.

        Returns:
            Formatted timestamp string
        """
        now = datetime.now()
        date_part = now.strftime("%m%d%y")

        # Parse format and generate time part
        if self.timestamp_format == "mmddyy-HH-MM-SS-AMPM":
            # Format: mmddyy-HH-MM-SS-AM/PM (with separators)
            hour = now.strftime("%I")  # 12-hour format
            minute = now.strftime("%M")
            second = now.strftime("%S")
            ampm = now.strftime("%p")
            time_part = f"{hour}-{minute}-{second}-{ampm}"
        elif self.timestamp_format == "mmddyy-HH:MM:SS-AMPM":
            # Format: mmddyy-HH:MM:SS-AM/PM (with colons)
            hour = now.strftime("%I")
            minute = now.strftime("%M")
            second = now.strftime("%S")
            ampm = now.strftime("%p")
            time_part = f"{hour}:{minute}:{second}-{ampm}"
        else:  # mmddyy-HHMMSS-AMPM (no separators)
            time_part = now.strftime("%I%M%S-%p")

        return f"{date_part}-{time_part}"

    def wait_for_file_stability(self, file_path: Path) -> bool:
        """Wait for file size to stabilize before processing.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file is stable, False if timeout or file disappeared
        """
        logger.debug(f"Waiting for file stability: {file_path.name}")
        start_time = time.time()
        prev_size = -1

        while time.time() - start_time < self.stability_timeout:
            try:
                if not file_path.exists():
                    logger.warning(f"File disappeared during stability check: {file_path.name}")
                    return False

                curr_size = file_path.stat().st_size

                if curr_size == prev_size and prev_size >= 0:
                    # File size hasn't changed, it's stable
                    logger.debug(f"File stable at {curr_size} bytes: {file_path.name}")
                    return True

                prev_size = curr_size
                time.sleep(self.stability_check_interval)

            except Exception as e:
                logger.error(f"Error checking file stability: {e}")
                return False

        logger.warning(f"File stability check timeout after {self.stability_timeout}s: {file_path.name}")
        return True  # Proceed anyway after timeout
    
    def find_latest_file(self) -> Optional[Path]:
        """Find the file with -latest suffix in the watch directory.
        
        Returns:
            Path to the file with -latest suffix, or None if not found
        """
        for file_path in self.watch_dir.iterdir():
            if file_path.is_file() and self.LATEST_SUFFIX in file_path.stem:
                return file_path
        return None
    
    def remove_latest_suffix(self, file_path: Path) -> Path:
        """Remove -latest suffix from a file.
        
        Args:
            file_path: Path to the file with -latest suffix
            
        Returns:
            New path after renaming
        """
        stem = file_path.stem
        suffix = file_path.suffix
        
        # Remove -latest from the stem
        new_stem = stem.replace(self.LATEST_SUFFIX, "")
        new_path = file_path.parent / f"{new_stem}{suffix}"
        
        logger.info(f"Removing -latest suffix: {file_path.name} -> {new_path.name}")
        file_path.rename(new_path)
        return new_path
    
    def rename_to_latest(self, file_path: Path) -> Path:
        """Rename a file with timestamp-latest format.
        
        Args:
            file_path: Path to the new file
            
        Returns:
            New path after renaming
        """
        timestamp = self.generate_timestamp()
        suffix = file_path.suffix
        new_name = f"{timestamp}{self.LATEST_SUFFIX}{suffix}"
        new_path = file_path.parent / new_name
        
        logger.info(f"Renaming new file: {file_path.name} -> {new_name}")
        file_path.rename(new_path)
        return new_path
    
    def process_new_file(self, file_path: Path) -> Path:
        """Process a newly detected file.
        
        This removes -latest from any existing file and adds it to the new one.
        
        Args:
            file_path: Path to the newly detected file
            
        Returns:
            Path to the renamed file with -latest suffix
        """
        logger.info(f"Processing new file: {file_path.name}")
        
        # Step 1: Find and remove -latest from any existing file
        existing_latest = self.find_latest_file()
        if existing_latest and existing_latest != file_path:
            self.remove_latest_suffix(existing_latest)
        
        # Step 2: Rename the new file with timestamp-latest
        new_path = self.rename_to_latest(file_path)
        
        return new_path
