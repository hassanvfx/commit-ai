"""Git repository analyzer for extracting changes."""

import subprocess
from typing import List, Tuple, Optional


class GitAnalyzer:
    """Analyzes git repository to extract staged changes."""
    
    @staticmethod
    def get_staged_diff() -> str:
        """Get diff of staged changes.
        
        Returns:
            Git diff output as string
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--staged'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get git diff: {e.stderr}")
    
    @staticmethod
    def get_staged_files() -> List[str]:
        """Get list of staged files.
        
        Returns:
            List of file paths that are staged
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--staged', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            return files
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get staged files: {e.stderr}")
    
    @staticmethod
    def is_git_repository() -> bool:
        """Check if current directory is a git repository.
        
        Returns:
            True if in a git repository
        """
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def has_staged_changes() -> bool:
        """Check if there are staged changes.
        
        Returns:
            True if there are staged changes
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--staged', '--quiet'],
                capture_output=True
            )
            # Returns 0 if no changes, 1 if changes exist
            return result.returncode == 1
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def get_repo_root() -> Optional[str]:
        """Get the root directory of the git repository.
        
        Returns:
            Path to repository root or None
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def get_branch_name() -> Optional[str]:
        """Get current branch name.
        
        Returns:
            Branch name or None
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def get_last_commit_message() -> Optional[str]:
        """Get the last commit message.
        
        Returns:
            Last commit message or None
        """
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
