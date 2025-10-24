# Quick Start Guide - commit-ai

## What You Just Built

**commit-ai** - An AI-powered git commit message generator that automatically creates meaningful, conventional commit messages by analyzing your staged changes.

## Project Structure

```
commit-ai/
├── commit_ai/              # Main package
│   ├── ai_providers/       # AI provider implementations
│   │   ├── base.py        # Abstract base class
│   │   ├── ollama.py      # Local AI (default)
│   │   ├── openai.py      # OpenAI GPT
│   │   ├── anthropic.py   # Claude
│   │   └── gemini.py      # Google Gemini
│   ├── cli.py             # Command-line interface
│   ├── config.py          # Configuration management
│   ├── git_analyzer.py    # Git operations
│   ├── message_generator.py # Message orchestration
│   ├── prompt_builder.py  # AI prompt construction
│   ├── response_parser.py # Response parsing & validation
│   └── context_analyzer.py # Change type detection
├── install.sh             # Installation script
├── setup.py               # Python package setup
├── requirements.txt       # Dependencies
└── README.md              # Full documentation
```

## Installation & Testing

### 1. Install the Package

```bash
cd /Users/hassan/repos/commit-ai

# Install in development mode
pip3 install --user -e .

# Verify installation
commit-ai help
```

### 2. Test in a Demo Repository

```bash
# Create a test repo
cd /Users/hassan/Desktop
mkdir test-commit-ai
cd test-commit-ai
git init

# Initialize commit-ai
commit-ai setup
# Follow the wizard:
# - Choose Ollama (or any provider)
# - Accept defaults or customize
# - Install hook when prompted

# Create a test file
echo "def hello(): print('Hello, World!')" > app.py

# Stage and commit
git add app.py
git commit
# The editor will open with an AI-generated message!
```

### 3. Test Different Scenarios

```bash
# Bug fix
echo "def hello(): print('Hello, World!') if name else print('Error')" > app.py
git add app.py
git commit

# Documentation
echo "# My Project" > README.md
git add README.md
git commit

# Test command
commit-ai test  # Test generation without committing
```

## Key Features

### 1. Multi-Provider Support
- **Ollama** (local, free) - Default
- **OpenAI** (GPT-4)
- **Anthropic** (Claude)
- **Google** (Gemini)

### 2. Intelligent Analysis
- Detects change types (feat, fix, docs, etc.)
- Analyzes scope from file paths
- Generates reasoning-driven messages

### 3. Customizable
- Per-repo configuration
- Custom prompts & templates
- Adjustable formats

### 4. CLI Commands

```bash
# Setup & Management
commit-ai setup          # Run setup wizard
commit-ai install        # Install hook in current repo
commit-ai uninstall      # Remove hook

# Testing & Debug
commit-ai test           # Test message generation
commit-ai doctor         # Diagnose issues
commit-ai provider test  # Test AI connection

# Configuration
commit-ai config                      # Show config
commit-ai config set key value        # Set value
commit-ai provider switch ollama      # Switch provider
```

## Distribution

### For Local Use

The project is ready to use on your machine:
```bash
pip3 install --user -e /Users/hassan/repos/commit-ai
```

### For Public Distribution

1. **Create GitHub Repository**
   ```bash
   cd /Users/hassan/repos/commit-ai
   # Add remote
   git remote add origin https://github.com/hassan/commit-ai.git
   git push -u origin main
   ```

2. **One-Line Install**
   Users can then install with:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/hassan/commit-ai/main/install.sh | bash
   ```

3. **PyPI (Optional)**
   ```bash
   # Build distribution
   python3 setup.py sdist bdist_wheel
   
   # Upload to PyPI
   pip3 install twine
   twine upload dist/*
   
   # Then users can: pip install commit-ai
   ```

## Architecture Highlights

### AI Provider System
- Abstract base class ensures consistency
- Each provider implements same interface
- Easy to add new providers

### Prompt Engineering
- Reasoning-driven prompts
- Few-shot learning with examples
- Structured output format
- Validates conventional commit format

### Git Integration
- Uses prepare-commit-msg hook
- Runs before editor opens
- Silent failure - never blocks commits
- User can always edit or override

## Next Steps

1. **Test with Different Providers**
   ```bash
   # Try OpenAI
   commit-ai config set openai.api_key sk-your-key
   commit-ai provider switch openai
   commit-ai test
   ```

2. **Customize Prompts**
   Edit `commit-ai.conf` in any repo to customize:
   - System messages
   - Reasoning templates
   - Output formats
   - Examples

3. **Share on LinkedIn**
   Use the marketing content from our planning session to announce your project!

## Support

- Documentation: `README.md`
- Help: `commit-ai help`
- Issues: Report bugs or feature requests on GitHub

## Example Output

**Input:** Added JWT authentication
**Output:**
```
feat(auth): add JWT validation middleware

Implements JWT-based authentication middleware to validate user
tokens on protected routes. Includes error handling for expired
and invalid tokens to improve security.
```

---

**Built with** ❤️ **by Hassan**

*Stop wasting time on commit messages. Let AI do it for you.*
