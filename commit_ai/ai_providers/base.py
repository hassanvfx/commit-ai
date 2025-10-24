"""Base abstract class for AI providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class AIProvider(ABC):
    """Abstract base class for AI providers that generate commit messages."""
    
    def __init__(self, config: Dict):
        """Initialize provider with configuration.
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is properly configured and available.
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_commit_message(self, diff: str, files: List[str], config: Dict) -> Dict[str, str]:
        """Generate commit message from git changes.
        
        Args:
            diff: Git diff output showing changes
            files: List of modified file paths
            config: Full application configuration including templates
        
        Returns:
            Dictionary with keys:
                - 'title': Commit message title/subject line
                - 'body': Detailed commit message body
                - 'reasoning': AI's reasoning process (optional)
                - 'full_message': Complete formatted commit message
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test provider connectivity and authentication.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """Validate provider configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, None
