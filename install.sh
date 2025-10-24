#!/bin/bash
# commit-ai installation script

set -e

echo "🚀 Installing commit-ai..."
echo ""

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Linux*)     OS_TYPE="Linux";;
    Darwin*)    OS_TYPE="Mac";;
    *)          OS_TYPE="Unknown";;
esac

echo "Detected OS: $OS_TYPE"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Install Python 3: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Check Git
if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed."
    exit 1
fi
echo "✓ Git found"

# Parse arguments
AUTO_MODE=false
SKIP_CLINE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto)
            AUTO_MODE=true
            shift
            ;;
        --skip-cline)
            SKIP_CLINE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Install commit-ai package
echo ""
echo "📦 Installing commit-ai package..."

# Download or install from current directory
if [ -f "setup.py" ]; then
    # Installing from local directory
    pip3 install --user -e .
else
    # Installing from GitHub (future)
    # pip3 install --user git+https://github.com/hassan/commit-ai.git
    echo "❌ setup.py not found. Clone the repository first."
    exit 1
fi

# Verify installation
if command -v commit-ai &> /dev/null; then
    echo "✓ commit-ai installed successfully"
else
    echo "❌ Installation failed. commit-ai command not found."
    echo "   Make sure ~/.local/bin is in your PATH"
    exit 1
fi

# Check/Install Ollama (if not skipped)
echo ""
echo "🤖 Checking AI provider..."

if [ "$SKIP_CLINE" = false ]; then
    if command -v ollama &> /dev/null; then
        echo "✓ Ollama found"
    else
        echo "⚠️  Ollama not found."
        
        if [ "$AUTO_MODE" = true ]; then
            INSTALL_OLLAMA="y"
        else
            read -p "Install Ollama (local AI, no API key needed)? (y/n): " INSTALL_OLLAMA
        fi
        
        if [[ "$INSTALL_OLLAMA" =~ ^[Yy]$ ]]; then
            echo "Installing Ollama..."
            curl -fsSL https://ollama.ai/install.sh | sh
            
            if command -v ollama &> /dev/null; then
                echo "✓ Ollama installed"
                
                # Pull default model
                echo "Pulling llama2 model (this may take a few minutes)..."
                ollama pull llama2:7b-chat || echo "⚠️  Failed to pull model. Run: ollama pull llama2:7b-chat"
            else
                echo "⚠️  Ollama installation may have failed. Install manually: https://ollama.ai"
            fi
        else
            echo "Skipping Ollama installation."
            echo "You can install it later or configure a different AI provider."
        fi
    fi
fi

# Run setup wizard if in a git repo
echo ""
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✓ Git repository detected"
    
    if [ "$AUTO_MODE" = true ]; then
        RUN_SETUP="y"
    else
        read -p "Run setup wizard now? (y/n): " RUN_SETUP
    fi
    
    if [[ "$RUN_SETUP" =~ ^[Yy]$ ]]; then
        commit-ai setup
    else
        echo "You can run 'commit-ai setup' later to configure."
    fi
else
    echo "⚠️  Not in a git repository."
    echo "Navigate to a git repo and run: commit-ai setup"
fi

echo ""
echo "✨ Installation complete!"
echo ""
echo "Quick start:"
echo "  1. cd /path/to/your/git/repo"
echo "  2. commit-ai setup"
echo "  3. Make changes and commit: git commit"
echo ""
echo "For help: commit-ai help"
echo "Documentation: https://github.com/hassan/commit-ai"
