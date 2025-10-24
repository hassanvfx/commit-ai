"""Context analyzer for detecting change types and selecting appropriate templates."""

from typing import Dict, List


class ContextAnalyzer:
    """Analyzes git changes to determine change type and select appropriate templates."""
    
    @staticmethod
    def detect_change_type(diff: str, files: List[str]) -> str:
        """Detect likely change type from diff and file list.
        
        Args:
            diff: Git diff output
            files: List of modified file paths
        
        Returns:
            Change type: 'bugfix', 'feature', 'documentation', 'test', 'refactor', or 'default'
        """
        diff_lower = diff.lower()
        
        # Bug fix indicators
        if any(word in diff_lower for word in ['fix', 'bug', 'issue', 'error', 'crash', 'patch']):
            return 'bugfix'
        
        # New feature indicators
        if any(word in diff_lower for word in ['add', 'new', 'implement', 'feature', 'introduce']):
            # But check if it's test-related
            if not any(word in diff_lower for word in ['test', 'spec', 'jest', 'pytest']):
                return 'feature'
        
        # Documentation changes
        if any(f.endswith(('.md', '.rst', '.txt')) or 'doc' in f.lower() for f in files):
            return 'documentation'
        
        # Test files
        if any('test' in f.lower() or 'spec' in f.lower() for f in files):
            return 'test'
        
        # Refactoring indicators
        if any(word in diff_lower for word in ['refactor', 'restructure', 'reorganize', 'cleanup', 'simplify']):
            return 'refactor'
        
        # Performance improvements
        if any(word in diff_lower for word in ['performance', 'optimize', 'faster', 'efficient']):
            return 'performance'
        
        # Style/formatting changes
        if any(word in diff_lower for word in ['format', 'style', 'lint', 'prettier']):
            return 'style'
        
        return 'default'
    
    @staticmethod
    def select_template(change_type: str, templates: Dict) -> Dict:
        """Select appropriate template based on change type.
        
        Args:
            change_type: Detected change type
            templates: Dictionary of available templates
        
        Returns:
            Selected template configuration
        """
        return templates.get(change_type, templates.get('default', {}))
    
    @staticmethod
    def analyze_scope(files: List[str]) -> str:
        """Determine the scope/component affected by changes.
        
        Args:
            files: List of modified file paths
        
        Returns:
            Suggested scope name or empty string
        """
        if not files:
            return ""
        
        # Extract directory names
        directories = set()
        for file in files:
            parts = file.split('/')
            if len(parts) > 1:
                # Get the first meaningful directory (skip common prefixes)
                for part in parts[:-1]:  # Exclude filename
                    if part not in ['.', '..', 'src', 'lib', 'app']:
                        directories.add(part)
                        break
        
        # If all changes are in one directory, use it as scope
        if len(directories) == 1:
            scope = directories.pop()
            # Clean up scope name
            scope = scope.replace('_', '-').replace(' ', '-')
            return scope
        
        # Try to infer from file names
        common_patterns = {
            'auth': ['auth', 'login', 'session', 'token'],
            'api': ['api', 'endpoint', 'route'],
            'ui': ['component', 'view', 'page', 'ui', 'frontend'],
            'db': ['database', 'model', 'schema', 'migration'],
            'test': ['test', 'spec', '__tests__'],
            'docs': ['doc', 'readme', 'guide'],
            'config': ['config', 'settings', 'env'],
        }
        
        files_str = ' '.join(files).lower()
        for scope, keywords in common_patterns.items():
            if any(keyword in files_str for keyword in keywords):
                return scope
        
        return ""
    
    @staticmethod
    def should_include_body(diff: str, config: Dict) -> bool:
        """Determine if commit body should be included.
        
        Args:
            diff: Git diff output
            config: Application configuration
        
        Returns:
            True if body should be included
        """
        # Check config preference
        if not config.get('commit_format', {}).get('include_body', True):
            return False
        
        # Include body for significant changes
        diff_lines = len(diff.split('\n'))
        
        # If diff is very small, body might not be necessary
        if diff_lines < 5:
            return False
        
        # If diff is large, body is helpful
        if diff_lines > 20:
            return True
        
        # Check for multiple files
        if diff.count('diff --git') > 1:
            return True
        
        return True
