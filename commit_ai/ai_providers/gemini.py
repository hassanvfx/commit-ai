"""Google Gemini AI provider implementation."""

from typing import Dict, List, Optional
from .base import AIProvider
from ..prompt_builder import PromptBuilder
from ..response_parser import ResponseParser


class GeminiProvider(AIProvider):
    """Google Gemini API provider for commit message generation."""
    
    def __init__(self, config: Dict):
        """Initialize Gemini provider.
        
        Args:
            config: Provider-specific configuration
        """
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'gemini-pro')
        self.base_url = config.get('base_url', 'https://generativelanguage.googleapis.com/v1')
    
    def is_available(self) -> bool:
        """Check if Gemini API key is configured.
        
        Returns:
            True if API key is present
        """
        return bool(self.api_key)
    
    def test_connection(self) -> bool:
        """Test Gemini API connection.
        
        Returns:
            True if connection successful
        """
        if not self.is_available():
            return False
        
        try:
            import requests
            
            # Test with a simple request
            response = requests.post(
                f'{self.base_url}/models/{self.model}:generateContent?key={self.api_key}',
                json={
                    'contents': [{'parts': [{'text': 'test'}]}]
                },
                timeout=10
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_commit_message(self, diff: str, files: List[str], config: Dict) -> Dict[str, str]:
        """Generate commit message using Google Gemini.
        
        Args:
            diff: Git diff output
            files: List of modified files
            config: Full application configuration
        
        Returns:
            Dictionary with commit message components
        """
        # Build reasoning-driven prompt
        builder = PromptBuilder(config)
        prompt_data = builder.build_reasoning_prompt(diff, files)
        
        # Call Gemini API
        try:
            response = self._call_gemini(
                prompt_data['system'],
                prompt_data['user']
            )
            
            # Parse structured response
            parser = ResponseParser()
            result = parser.parse_structured_response(response)
            
            # Validate conventional commit format
            valid_types = config.get('commit_format', {}).get('types', [])
            if valid_types and not parser.validate_conventional_commit(result['title'], valid_types):
                result['title'] = parser.fix_commit_format(result['title'], valid_types)
            
            # Validate title length
            max_length = config.get('commit_format', {}).get('max_title_length', 72)
            is_valid, fixed_title = parser.validate_title_length(result['title'], max_length)
            if not is_valid:
                result['title'] = fixed_title
            
            # Rebuild full message
            result['full_message'] = f"{result['title']}\n\n{result['body']}" if result['body'] else result['title']
            
            return result
            
        except Exception as e:
            # Return fallback message on error
            fallback = config.get('fallback_message', 'chore: update files')
            return {
                'reasoning': f"Error: {str(e)}",
                'title': fallback,
                'body': '',
                'full_message': fallback
            }
    
    def _call_gemini(self, system: str, prompt: str) -> str:
        """Call Google Gemini API.
        
        Args:
            system: System message
            prompt: User prompt
        
        Returns:
            AI response text
        """
        import requests
        
        # Gemini doesn't have separate system message, so combine them
        full_prompt = f"{system}\n\n{prompt}"
        
        data = {
            'contents': [
                {
                    'parts': [
                        {'text': full_prompt}
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.3,
                'maxOutputTokens': 1000,
            }
        }
        
        response = requests.post(
            f'{self.base_url}/models/{self.model}:generateContent?key={self.api_key}',
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """Validate Gemini configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.api_key:
            return False, "Gemini API key is not configured. Set it with: commit-ai config set gemini.api_key YOUR_KEY"
        
        return True, None
