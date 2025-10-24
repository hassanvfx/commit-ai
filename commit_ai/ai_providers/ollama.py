"""Ollama AI provider implementation."""

import json
import subprocess
import shutil
from typing import Dict, List
from .base import AIProvider
from ..prompt_builder import PromptBuilder
from ..response_parser import ResponseParser


class OllamaProvider(AIProvider):
    """Ollama local AI provider for commit message generation."""
    
    def __init__(self, config: Dict):
        """Initialize Ollama provider.
        
        Args:
            config: Provider-specific configuration
        """
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama2:7b-chat')
    
    def is_available(self) -> bool:
        """Check if Ollama is installed and running.
        
        Returns:
            True if Ollama is available
        """
        # Check if ollama command exists
        if not shutil.which('ollama'):
            return False
        
        # Check if ollama service is running by trying to list models
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def test_connection(self) -> bool:
        """Test Ollama connection and model availability.
        
        Returns:
            True if connection and model are available
        """
        if not self.is_available():
            return False
        
        try:
            # Check if the specific model is available
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return self.model.split(':')[0] in result.stdout
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def generate_commit_message(self, diff: str, files: List[str], config: Dict) -> Dict[str, str]:
        """Generate commit message using Ollama.
        
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
        
        # Call Ollama API
        try:
            response = self._call_ollama(
                prompt_data['system'],
                prompt_data['user']
            )
            
            # Parse structured response
            parser = ResponseParser()
            result = parser.parse_structured_response(response)
            
            # Validate conventional commit format
            valid_types = config.get('commit_format', {}).get('types', [])
            if valid_types and not parser.validate_conventional_commit(result['title'], valid_types):
                # Attempt to fix format
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
    
    def _call_ollama(self, system: str, prompt: str) -> str:
        """Call Ollama API using subprocess.
        
        Args:
            system: System message
            prompt: User prompt
        
        Returns:
            AI response text
        """
        # Combine system and user prompt
        full_prompt = f"System: {system}\n\nUser: {prompt}"
        
        # Call ollama via subprocess
        result = subprocess.run(
            ['ollama', 'run', self.model],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"Ollama error: {result.stderr}")
        
        return result.stdout.strip()
    
    def validate_config(self) -> tuple[bool, str]:
        """Validate Ollama configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.is_available():
            return False, "Ollama is not installed or not running. Install with: curl -fsSL https://ollama.ai/install.sh | sh"
        
        if not self.test_connection():
            return False, f"Model '{self.model}' is not available. Pull it with: ollama pull {self.model}"
        
        return True, None
