"""Prompt builder for AI commit message generation with reasoning."""

from typing import Dict, List


class PromptBuilder:
    """Builds structured prompts with reasoning steps for AI providers."""
    
    def __init__(self, config: Dict):
        """Initialize prompt builder with configuration.
        
        Args:
            config: Full application configuration
        """
        self.config = config
        self.prompt_config = config.get('prompt_engineering', {})
    
    def build_reasoning_prompt(self, diff: str, files: List[str]) -> Dict[str, str]:
        """Build a structured prompt with reasoning steps.
        
        Args:
            diff: Git diff output
            files: List of modified file paths
        
        Returns:
            Dictionary with 'system' and 'user' prompt messages
        """
        # System message sets the AI's role and context
        system = self.prompt_config.get(
            'system_message',
            "You are an expert software engineer who writes clear, concise, and meaningful "
            "git commit messages following conventional commit standards."
        )
        
        # Get reasoning template (use default if empty)
        reasoning_template = self.prompt_config.get('reasoning_template') or self._get_default_reasoning_template()
        
        # Get output format specification (use default if empty)
        output_format = self.prompt_config.get('output_format') or self._get_default_output_format()
        
        # Format examples for few-shot learning
        examples = self._format_examples()
        
        # Get commit format preferences
        commit_format = self.config.get('commit_format', {})
        types = ', '.join(commit_format.get('types', ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']))
        max_title = commit_format.get('max_title_length', 72)
        
        # Truncate diff if too long
        max_diff_lines = self.config.get('analysis', {}).get('max_diff_lines', 500)
        diff_lines = diff.split('\n')
        if len(diff_lines) > max_diff_lines:
            diff = '\n'.join(diff_lines[:max_diff_lines])
            diff += f"\n... (truncated, showing first {max_diff_lines} lines)"
        
        # Format file list
        file_list = '\n'.join([f"  - {f}" for f in files])
        
        # Build the complete prompt
        user_prompt = f"""{reasoning_template.format(diff=diff, files=file_list)}

{output_format}

{examples}

Remember:
- Title max {max_title} characters
- Use conventional commit types: {types}
- Be specific about what changed and why
- Follow the reasoning steps explicitly
- Use imperative mood in title (e.g., "add" not "added")
"""
        
        return {
            'system': system,
            'user': user_prompt
        }
    
    def _get_default_reasoning_template(self) -> str:
        """Get default reasoning template."""
        return """TASK: Generate a git commit message for the following changes.

IMPORTANT INSTRUCTIONS:
- DO NOT ask questions or be conversational
- DO NOT say "I'll help you" or similar phrases
- DIRECTLY generate the commit message
- Follow conventional commit format exactly
- Use imperative mood (e.g., "add" not "added")

Git Changes:
{diff}

Files Modified:
{files}

REQUIRED OUTPUT: Generate a commit message following these steps:
1. Determine change type (feat/fix/docs/style/refactor/test/chore/perf)
2. Write concise title (max 72 chars): type(scope): description
3. Write detailed body explaining what and why

Generate the commit message NOW:"""
    
    def _get_default_output_format(self) -> str:
        """Get default output format specification."""
        return """Provide your response in this exact format:

<reasoning>
[Your step-by-step analysis following the 6 steps above]
</reasoning>

<commit_title>
[type](scope): [concise description in imperative mood]
</commit_title>

<commit_body>
[Detailed explanation of what changed and why]
[Include bullet points if multiple changes]
[Mention breaking changes if any]
</commit_body>"""
    
    def _format_examples(self) -> str:
        """Format examples for the prompt."""
        examples = self.prompt_config.get('examples', self._get_default_examples())
        
        if not examples:
            return ""
        
        formatted = ["Examples of good commit messages:"]
        
        for i, ex in enumerate(examples, 1):
            formatted.append(f"""
Example {i}:
Changes: {ex.get('diff', 'N/A')}
Reasoning: {ex.get('reasoning', 'N/A')}
Output: {ex.get('output', 'N/A')}
""")
        
        return '\n'.join(formatted)
    
    def _get_default_examples(self) -> List[Dict]:
        """Get default examples."""
        return [
            {
                'diff': 'Added JWT validation middleware in auth.py',
                'reasoning': '1. ANALYZE: New middleware added\n2. CATEGORIZE: New feature (feat)\n3. IDENTIFY SCOPE: auth\n4. SUMMARIZE: add authentication middleware\n5. ELABORATE: Implements JWT validation\n6. FORMAT: feat(auth): add JWT validation middleware',
                'output': 'feat(auth): add JWT validation middleware\n\nImplements JWT-based authentication middleware to validate user tokens on protected routes. Includes error handling for expired and invalid tokens.'
            },
            {
                'diff': 'Fixed null pointer exception in user service',
                'reasoning': '1. ANALYZE: Bug fix in user service\n2. CATEGORIZE: Bug fix\n3. IDENTIFY SCOPE: user service\n4. SUMMARIZE: fix null pointer exception\n5. ELABORATE: Added null check before accessing user object\n6. FORMAT: fix(user): prevent null pointer exception',
                'output': 'fix(user): prevent null pointer exception in user service\n\nAdds null check before accessing user object properties to prevent crashes when user is not found.'
            }
        ]
