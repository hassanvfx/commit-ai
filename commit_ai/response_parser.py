"""Response parser for AI-generated commit messages."""

import re
from typing import Dict, List, Tuple


class ResponseParser:
    """Parses and validates AI responses for commit messages."""
    
    @staticmethod
    def parse_structured_response(response: str) -> Dict[str, str]:
        """Parse AI response with reasoning and commit message.
        
        Args:
            response: Raw AI response text
        
        Returns:
            Dictionary with keys: 'reasoning', 'title', 'body', 'full_message'
        """
        # Extract reasoning
        reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', response, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
        
        # Extract commit title
        title_match = re.search(r'<commit_title>(.*?)</commit_title>', response, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        
        # Extract commit body
        body_match = re.search(r'<commit_body>(.*?)</commit_body>', response, re.DOTALL)
        body = body_match.group(1).strip() if body_match else ""
        
        # Fallback: if tags not found, try to parse plain text
        if not title:
            title, body = ResponseParser._parse_plain_response(response)
        
        # Clean up the title and body
        title = ResponseParser._clean_text(title)
        body = ResponseParser._clean_text(body)
        
        return {
            'reasoning': reasoning,
            'title': title,
            'body': body,
            'full_message': f"{title}\n\n{body}" if body else title
        }
    
    @staticmethod
    def _parse_plain_response(response: str) -> Tuple[str, str]:
        """Fallback parser for plain text responses.
        
        Args:
            response: Plain text response
        
        Returns:
            Tuple of (title, body)
        """
        # Remove reasoning tags if present but not properly closed
        response = re.sub(r'<reasoning>.*?</reasoning>', '', response, flags=re.DOTALL)
        response = re.sub(r'<commit_title>|</commit_title>|<commit_body>|</commit_body>', '', response)
        
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        
        if not lines:
            return "chore: update files", ""
        
        # First non-empty line is the title
        title = lines[0]
        
        # Rest is the body
        body = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        return title, body
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean up text by removing extra whitespace and newlines.
        
        Args:
            text: Text to clean
        
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Restore intentional line breaks in body text
        text = text.replace('. ', '.\n').replace(':\n', ': ')
        return text.strip()
    
    @staticmethod
    def validate_conventional_commit(title: str, valid_types: List[str]) -> bool:
        """Validate conventional commit format.
        
        Args:
            title: Commit title to validate
            valid_types: List of valid commit types
        
        Returns:
            True if valid conventional commit format
        """
        # Pattern: type(scope): description  OR  type: description
        pattern = r'^(' + '|'.join(re.escape(t) for t in valid_types) + r')(\(.+?\))?: .+'
        return bool(re.match(pattern, title))
    
    @staticmethod
    def fix_commit_format(title: str, valid_types: List[str]) -> str:
        """Attempt to fix commit title format.
        
        Args:
            title: Potentially malformed commit title
            valid_types: List of valid commit types
        
        Returns:
            Fixed commit title
        """
        title = title.strip()
        
        # Check if it already matches
        if ResponseParser.validate_conventional_commit(title, valid_types):
            return title
        
        # Try to extract type from the beginning
        for commit_type in valid_types:
            if title.lower().startswith(commit_type):
                # Extract the rest after the type
                rest = title[len(commit_type):].strip()
                
                # Remove leading colon or parenthesis if present
                rest = re.sub(r'^[:\(\)]?\s*', '', rest)
                
                # Check if there's a scope
                scope_match = re.match(r'\(([^)]+)\)\s*:?\s*(.+)', rest)
                if scope_match:
                    scope, description = scope_match.groups()
                    return f"{commit_type}({scope}): {description}"
                else:
                    # No scope, just add colon
                    if not rest.startswith(':'):
                        return f"{commit_type}: {rest}"
                    return f"{commit_type}{rest}"
        
        # If no type found, try to infer from content
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['add', 'new', 'implement', 'create']):
            return f"feat: {title}"
        elif any(word in title_lower for word in ['fix', 'bug', 'issue', 'resolve']):
            return f"fix: {title}"
        elif any(word in title_lower for word in ['update', 'modify', 'change']):
            return f"chore: {title}"
        elif any(word in title_lower for word in ['refactor', 'restructure', 'reorganize']):
            return f"refactor: {title}"
        elif any(word in title_lower for word in ['test', 'spec']):
            return f"test: {title}"
        elif any(word in title_lower for word in ['doc', 'readme']):
            return f"docs: {title}"
        else:
            # Default to chore
            return f"chore: {title}"
    
    @staticmethod
    def validate_title_length(title: str, max_length: int = 72) -> Tuple[bool, str]:
        """Validate commit title length.
        
        Args:
            title: Commit title
            max_length: Maximum allowed length
        
        Returns:
            Tuple of (is_valid, truncated_title_if_needed)
        """
        if len(title) <= max_length:
            return True, title
        
        # Try to truncate at a word boundary
        truncated = title[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:  # If we can keep at least 70% of length
            truncated = truncated[:last_space]
        
        return False, truncated.strip()
