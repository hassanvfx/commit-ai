"""Configuration management for commit-ai."""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class Config:
    """Manages commit-ai configuration."""
    
    DEFAULT_CONFIG = {
        "enabled": True,
        "ai_provider": "ollama",
        "providers": {
            "ollama": {
                "enabled": True,
                "base_url": "http://localhost:11434",
                "model": "llama2:7b-chat"
            },
            "openai": {
                "enabled": False,
                "api_key": "",
                "model": "gpt-4",
                "base_url": "https://api.openai.com/v1"
            },
            "anthropic": {
                "enabled": False,
                "api_key": "",
                "model": "claude-3-5-sonnet-20241022"
            },
            "gemini": {
                "enabled": False,
                "api_key": "",
                "model": "gemini-pro"
            }
        },
        "commit_format": {
            "use_conventional_commits": True,
            "types": ["feat", "fix", "docs", "style", "refactor", "test", "chore", "perf"],
            "max_title_length": 72,
            "include_body": True
        },
        "analysis": {
            "max_diff_lines": 500,
            "include_file_list": True,
            "analyze_context": True
        },
        "prompt_engineering": {
            "system_message": "You are an expert software engineer who writes clear, concise, and meaningful git commit messages following conventional commit standards.",
            "reasoning_template": "",
            "output_format": "",
            "examples": []
        },
        "fallback_message": "chore: update files"
    }
    
    @staticmethod
    def get_config_path() -> Path:
        """Get path to configuration file.
        
        Returns:
            Path to commit-ai.conf in current directory or repo root
        """
        # First check current directory
        current = Path.cwd() / 'commit-ai.conf'
        if current.exists():
            return current
        
        # Check git repo root
        from .git_analyzer import GitAnalyzer
        repo_root = GitAnalyzer.get_repo_root()
        if repo_root:
            repo_config = Path(repo_root) / 'commit-ai.conf'
            if repo_config.exists():
                return repo_config
        
        # Default to current directory
        return current
    
    @staticmethod
    def load() -> Dict:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        config_path = Config.get_config_path()
        
        if not config_path.exists():
            return Config.DEFAULT_CONFIG.copy()
        
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # Merge with defaults
            config = Config.DEFAULT_CONFIG.copy()
            Config._deep_merge(config, user_config)
            return config
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            return Config.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def save(config: Dict, path: Optional[Path] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            path: Optional path to save to (defaults to standard location)
        """
        if path is None:
            path = Config.get_config_path()
        
        try:
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save config to {path}: {e}")
    
    @staticmethod
    def create_default(path: Optional[Path] = None) -> None:
        """Create default configuration file.
        
        Args:
            path: Optional path to create config at
        """
        if path is None:
            path = Config.get_config_path()
        
        Config.save(Config.DEFAULT_CONFIG.copy(), path)
    
    @staticmethod
    def get_value(key: str, config: Optional[Dict] = None) -> Optional[any]:
        """Get configuration value by dot-notation key.
        
        Args:
            key: Key in dot notation (e.g., 'providers.ollama.model')
            config: Configuration dict (loads from file if not provided)
        
        Returns:
            Configuration value or None
        """
        if config is None:
            config = Config.load()
        
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        
        return value
    
    @staticmethod
    def set_value(key: str, value: any, config: Optional[Dict] = None) -> Dict:
        """Set configuration value by dot-notation key.
        
        Args:
            key: Key in dot notation (e.g., 'providers.ollama.model')
            value: Value to set
            config: Configuration dict (loads from file if not provided)
        
        Returns:
            Updated configuration dictionary
        """
        if config is None:
            config = Config.load()
        
        keys = key.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            elif not isinstance(current[k], dict):
                # If we encounter a non-dict value, we need to replace it
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        return config
    
    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> None:
        """Deep merge override dict into base dict.
        
        Args:
            base: Base dictionary to merge into
            override: Dictionary with values to override
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Config._deep_merge(base[key], value)
            else:
                base[key] = value
