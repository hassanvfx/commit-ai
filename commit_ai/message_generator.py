"""Message generator that orchestrates AI providers and analysis."""

from typing import Dict
from .git_analyzer import GitAnalyzer
from .context_analyzer import ContextAnalyzer
from .ai_providers import OllamaProvider, OpenAIProvider, AnthropicProvider, GeminiProvider


class MessageGenerator:
    """Orchestrates commit message generation using AI providers."""
    
    def __init__(self, config: Dict):
        """Initialize message generator.
        
        Args:
            config: Full application configuration
        """
        self.config = config
        self.provider = self._get_provider()
    
    def _get_provider(self):
        """Get the configured AI provider.
        
        Returns:
            AI provider instance
        """
        provider_name = self.config.get('ai_provider', 'ollama')
        providers_config = self.config.get('providers', {})
        
        provider_config = providers_config.get(provider_name, {})
        
        provider_map = {
            'ollama': OllamaProvider,
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'gemini': GeminiProvider
        }
        
        provider_class = provider_map.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        return provider_class(provider_config)
    
    def generate(self) -> Dict[str, str]:
        """Generate commit message from staged changes.
        
        Returns:
            Dictionary with commit message components
        """
        # Check if we're in a git repository
        if not GitAnalyzer.is_git_repository():
            raise Exception("Not a git repository")
        
        # Check if there are staged changes
        if not GitAnalyzer.has_staged_changes():
            raise Exception("No staged changes to commit")
        
        # Get staged changes
        diff = GitAnalyzer.get_staged_diff()
        files = GitAnalyzer.get_staged_files()
        
        if not diff:
            raise Exception("No diff available")
        
        # Analyze context
        change_type = ContextAnalyzer.detect_change_type(diff, files)
        scope = ContextAnalyzer.analyze_scope(files)
        
        # Check if provider is available
        if not self.provider.is_available():
            # Fall back to simple message
            fallback = self.config.get('fallback_message', 'chore: update files')
            return {
                'reasoning': 'AI provider not available',
                'title': fallback,
                'body': '',
                'full_message': fallback
            }
        
        # Generate commit message using AI
        result = self.provider.generate_commit_message(diff, files, self.config)
        
        # Add detected scope if not already present and scope detection is enabled
        if scope and '(' not in result['title']:
            # Insert scope after the type
            parts = result['title'].split(':', 1)
            if len(parts) == 2:
                result['title'] = f"{parts[0]}({scope}):{parts[1]}"
                result['full_message'] = f"{result['title']}\n\n{result['body']}" if result['body'] else result['title']
        
        return result
    
    def test_provider(self) -> bool:
        """Test if the configured provider works.
        
        Returns:
            True if provider is working
        """
        return self.provider.test_connection()
    
    def validate_provider(self) -> tuple[bool, str]:
        """Validate provider configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.provider.validate_config()
