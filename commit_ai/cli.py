"""Command-line interface for commit-ai."""

import sys
import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from .config import Config
from .git_analyzer import GitAnalyzer
from .message_generator import MessageGenerator


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    
    command = sys.argv[1]
    
    commands = {
        'setup': cmd_setup,
        'install': cmd_install,
        'uninstall': cmd_uninstall,
        'generate': cmd_generate,
        'test': cmd_test,
        'config': cmd_config,
        'provider': cmd_provider,
        'doctor': cmd_doctor,
        'help': lambda: print_help(),
        '--help': lambda: print_help(),
        '-h': lambda: print_help(),
    }
    
    if command in commands:
        try:
            commands[command]()
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        print_help()
        sys.exit(1)


def print_help():
    """Print help message."""
    help_text = """
commit-ai - AI-powered git commit message generator

Usage:
  commit-ai <command> [options]

Commands:
  setup           Interactive setup wizard
  install         Install git hook in current repository
  uninstall       Remove git hook from current repository
  generate        Generate commit message (used by git hook)
  test            Test message generation without committing
  config          Manage configuration
  provider        Manage AI providers
  doctor          Diagnose setup issues
  help            Show this help message

Examples:
  commit-ai setup              # Run interactive setup
  commit-ai install            # Install hook in current repo
  commit-ai test               # Test commit message generation
  commit-ai provider switch ollama  # Switch to Ollama provider
  commit-ai config set openai.api_key YOUR_KEY

For more info: https://github.com/hassan/commit-ai
"""
    print(help_text)


def cmd_setup():
    """Interactive setup wizard."""
    print("🚀 commit-ai Setup Wizard\n")
    
    # Check if in git repo
    if not GitAnalyzer.is_git_repository():
        print("⚠️  Not in a git repository. Setup will create config but won't install hook.")
        print("   Run 'commit-ai install' in a git repo after setup.\n")
    
    # Select AI provider
    print("Step 1/3: Select AI Provider")
    print("  1) Ollama (local, free, no API key required) ⭐ Recommended")
    print("  2) OpenAI GPT (requires API key)")
    print("  3) Anthropic Claude (requires API key)")
    print("  4) Google Gemini (requires API key)")
    
    choice = input("\nChoose (1-4): ").strip()
    
    provider_map = {'1': 'ollama', '2': 'openai', '3': 'anthropic', '4': 'gemini'}
    provider = provider_map.get(choice, 'ollama')
    
    # Load config
    config = Config.load()
    config['ai_provider'] = provider
    
    # Configure provider
    print(f"\nStep 2/3: Configure {provider.title()}")
    
    if provider == 'ollama':
        setup_ollama(config)
    elif provider == 'openai':
        setup_openai(config)
    elif provider == 'anthropic':
        setup_anthropic(config)
    elif provider == 'gemini':
        setup_gemini(config)
    
    # Commit format preferences
    print("\nStep 3/3: Commit Format Preferences")
    use_conventional = input("Use conventional commits (feat:, fix:, etc.)? (y/n): ").strip().lower() == 'y'
    include_body = input("Include detailed body in commit messages? (y/n): ").strip().lower() == 'y'
    
    config['commit_format']['use_conventional_commits'] = use_conventional
    config['commit_format']['include_body'] = include_body
    
    # Save config
    Config.save(config)
    print(f"\n✓ Configuration saved to {Config.get_config_path()}")
    
    # Install hook if in git repo
    if GitAnalyzer.is_git_repository():
        install_hook = input("\nInstall git hook in this repository? (y/n): ").strip().lower() == 'y'
        if install_hook:
            cmd_install()
    
    print("\n✨ Setup complete!")
    print("\nNext steps:")
    print("  1. Make some changes: echo 'test' >> README.md")
    print("  2. Stage changes: git add README.md")
    print("  3. Commit: git commit")
    print("\nYour commit message will be auto-generated!")


def setup_ollama(config):
    """Setup Ollama provider."""
    if not shutil.which('ollama'):
        print("\n⚠️  Ollama not found.")
        install = input("Install Ollama? (y/n): ").strip().lower() == 'y'
        if install:
            print("\nInstalling Ollama...")
            try:
                subprocess.run(
                    'curl -fsSL https://ollama.ai/install.sh | sh',
                    shell=True,
                    check=True
                )
                print("✓ Ollama installed")
            except:
                print("❌ Failed to install Ollama. Install manually: https://ollama.ai")
                return
    
    # Select model
    print("\nSelect model:")
    print("  1) llama2:7b-chat (default, ~4GB)")
    print("  2) codellama:7b (~4GB, better for code)")
    print("  3) mistral:7b (~4GB, fast)")
    
    model_choice = input("Choose (1-3): ").strip()
    models = {'1': 'llama2:7b-chat', '2': 'codellama:7b', '3': 'mistral:7b'}
    model = models.get(model_choice, 'llama2:7b-chat')
    
    config['providers']['ollama']['model'] = model
    config['providers']['ollama']['enabled'] = True
    
    # Pull model
    print(f"\nPulling {model}... (this may take a few minutes)")
    try:
        subprocess.run(['ollama', 'pull', model], check=True)
        print("✓ Model ready")
    except:
        print("⚠️  Failed to pull model. Run manually: ollama pull " + model)


def setup_openai(config):
    """Setup OpenAI provider."""
    print("\nYou need an OpenAI API key.")
    print("Get one at: https://platform.openai.com/api-keys")
    api_key = input("\nEnter your OpenAI API key: ").strip()
    
    if api_key:
        config['providers']['openai']['api_key'] = api_key
        config['providers']['openai']['enabled'] = True
        print("✓ OpenAI configured")
    else:
        print("⚠️  No API key provided. You can set it later with:")
        print("  commit-ai config set openai.api_key YOUR_KEY")


def setup_anthropic(config):
    """Setup Anthropic provider."""
    print("\nYou need an Anthropic API key.")
    print("Get one at: https://console.anthropic.com/")
    api_key = input("\nEnter your Anthropic API key: ").strip()
    
    if api_key:
        config['providers']['anthropic']['api_key'] = api_key
        config['providers']['anthropic']['enabled'] = True
        print("✓ Anthropic configured")
    else:
        print("⚠️  No API key provided. You can set it later with:")
        print("  commit-ai config set anthropic.api_key YOUR_KEY")


def setup_gemini(config):
    """Setup Gemini provider."""
    print("\nYou need a Google Gemini API key.")
    print("Get one at: https://makersuite.google.com/app/apikey")
    api_key = input("\nEnter your Gemini API key: ").strip()
    
    if api_key:
        config['providers']['gemini']['api_key'] = api_key
        config['providers']['gemini']['enabled'] = True
        print("✓ Gemini configured")
    else:
        print("⚠️  No API key provided. You can set it later with:")
        print("  commit-ai config set gemini.api_key YOUR_KEY")


def cmd_install():
    """Install git hook."""
    if not GitAnalyzer.is_git_repository():
        print("❌ Not a git repository")
        sys.exit(1)
    
    repo_root = GitAnalyzer.get_repo_root()
    hook_path = Path(repo_root) / '.git' / 'hooks' / 'prepare-commit-msg'
    
    # Create hook
    hook_content = get_hook_content()
    
    # Check if hook already exists
    if hook_path.exists():
        backup = input(f"Hook already exists. Backup and replace? (y/n): ").strip().lower() == 'y'
        if backup:
            shutil.copy(hook_path, str(hook_path) + '.backup')
            print(f"✓ Backed up to {hook_path}.backup")
        else:
            print("❌ Installation cancelled")
            sys.exit(1)
    
    # Write hook
    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)  # Make executable
    
    # Create config if it doesn't exist
    config_path = Path(repo_root) / 'commit-ai.conf'
    if not config_path.exists():
        Config.create_default(config_path)
        print(f"✓ Created config at {config_path}")
    
    print(f"✓ Installed hook at {hook_path}")
    print("\n✨ commit-ai is ready!")
    print("Try: git commit")


def cmd_uninstall():
    """Uninstall git hook."""
    if not GitAnalyzer.is_git_repository():
        print("❌ Not a git repository")
        sys.exit(1)
    
    repo_root = GitAnalyzer.get_repo_root()
    hook_path = Path(repo_root) / '.git' / 'hooks' / 'prepare-commit-msg'
    
    if not hook_path.exists():
        print("✓ No hook to remove")
        return
    
    # Check if it's our hook
    content = hook_path.read_text()
    if 'commit-ai' not in content:
        print("⚠️  Hook exists but doesn't appear to be commit-ai hook")
        remove = input("Remove anyway? (y/n): ").strip().lower() == 'y'
        if not remove:
            sys.exit(1)
    
    hook_path.unlink()
    print("✓ Hook removed")


def cmd_generate():
    """Generate commit message."""
    try:
        config = Config.load()
        generator = MessageGenerator(config)
        result = generator.generate()
        
        # Print the full message
        print(result['full_message'])
    except Exception as e:
        # Use fallback
        config = Config.load()
        print(config.get('fallback_message', 'chore: update files'))


def cmd_test():
    """Test commit message generation."""
    print("🧪 Testing commit message generation...\n")
    
    if not GitAnalyzer.is_git_repository():
        print("❌ Not a git repository")
        sys.exit(1)
    
    if not GitAnalyzer.has_staged_changes():
        print("❌ No staged changes")
        print("Try: git add <files>")
        sys.exit(1)
    
    print("Analyzing staged changes...")
    files = GitAnalyzer.get_staged_files()
    print(f"Files: {', '.join(files)}\n")
    
    print("Generating commit message...")
    config = Config.load()
    generator = MessageGenerator(config)
    
    try:
        result = generator.generate()
        print("\n" + "="*60)
        print(result['full_message'])
        print("="*60)
        
        if result.get('reasoning'):
            print(f"\nReasoning:\n{result['reasoning']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def cmd_config():
    """Manage configuration."""
    if len(sys.argv) < 3:
        # Show config
        config = Config.load()
        print(f"Configuration from: {Config.get_config_path()}\n")
        print(json.dumps(config, indent=2))
        return
    
    subcommand = sys.argv[2]
    
    if subcommand == 'show':
        config = Config.load()
        print(json.dumps(config, indent=2))
    elif subcommand == 'set' and len(sys.argv) >= 5:
        key = sys.argv[3]
        value = sys.argv[4]
        config = Config.set_value(key, value)
        Config.save(config)
        print(f"✓ Set {key} = {value}")
    elif subcommand == 'get' and len(sys.argv) >= 4:
        key = sys.argv[3]
        value = Config.get_value(key)
        print(value)
    else:
        print("Usage:")
        print("  commit-ai config show")
        print("  commit-ai config set <key> <value>")
        print("  commit-ai config get <key>")


def cmd_provider():
    """Manage AI providers."""
    if len(sys.argv) < 3:
        # List providers
        config = Config.load()
        current = config.get('ai_provider')
        providers = config.get('providers', {})
        
        print("Available providers:\n")
        for name, conf in providers.items():
            status = "✓" if name == current else " "
            enabled = "enabled" if conf.get('enabled') else "disabled"
            print(f"  [{status}] {name} ({enabled})")
        return
    
    subcommand = sys.argv[2]
    
    if subcommand == 'switch' and len(sys.argv) >= 4:
        provider = sys.argv[3]
        config = Config.set_value('ai_provider', provider)
        Config.save(config)
        print(f"✓ Switched to {provider}")
    elif subcommand == 'test':
        config = Config.load()
        generator = MessageGenerator(config)
        if generator.test_provider():
            print("✓ Provider is working")
        else:
            print("❌ Provider test failed")
    else:
        print("Usage:")
        print("  commit-ai provider")
        print("  commit-ai provider switch <name>")
        print("  commit-ai provider test")


def cmd_doctor():
    """Diagnose setup issues."""
    print("🔍 Diagnosing commit-ai setup...\n")
    
    issues = []
    
    # Check git
    print("Dependencies:")
    if shutil.which('git'):
        version = subprocess.run(['git', '--version'], capture_output=True, text=True).stdout.strip()
        print(f"  ✓ {version}")
    else:
        print("  ✗ Git: not found")
        issues.append("Git is not installed")
    
    # Check Python
    print(f"  ✓ Python: {sys.version.split()[0]}")
    
    # Check AI provider
    config = Config.load()
    provider = config.get('ai_provider')
    print(f"\nAI Provider: {provider}")
    
    if provider == 'ollama':
        if shutil.which('ollama'):
            print("  ✓ Ollama: installed")
        else:
            print("  ✗ Ollama: not found")
            issues.append("Ollama is not installed")
    
    # Check hook
    print("\nGit Hook:")
    if GitAnalyzer.is_git_repository():
        repo_root = GitAnalyzer.get_repo_root()
        hook_path = Path(repo_root) / '.git' / 'hooks' / 'prepare-commit-msg'
        if hook_path.exists():
            print(f"  ✓ Installed at {hook_path}")
        else:
            print("  ✗ Not installed")
            issues.append("Git hook not installed")
    else:
        print("  - Not in a git repository")
    
    # Check config
    print("\nConfiguration:")
    config_path = Config.get_config_path()
    if config_path.exists():
        print(f"  ✓ {config_path}")
    else:
        print(f"  ⚠️  No config file (using defaults)")
    
    # Summary
    if issues:
        print("\n⚠️  Issues Found:")
        for issue in issues:
            print(f"  • {issue}")
        print("\nSuggested fix:")
        print("  Run: commit-ai setup")
    else:
        print("\n✨ Everything looks good!")


def get_hook_content() -> str:
    """Get content for prepare-commit-msg hook."""
    return '''#!/usr/bin/env python3
"""Git prepare-commit-msg hook for commit-ai."""

import sys
import subprocess

def main():
    commit_msg_file = sys.argv[1]
    commit_source = sys.argv[2] if len(sys.argv) > 2 else ''
    
    # Only generate message for regular commits (not merge, squash, etc.)
    if commit_source in ['merge', 'squash', 'commit']:
        return
    
    # Generate commit message
    try:
        result = subprocess.run(
            ['commit-ai', 'generate'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Write generated message to file
            with open(commit_msg_file, 'w') as f:
                f.write(result.stdout)
    except Exception as e:
        # Silent failure - don't block commits
        pass

if __name__ == '__main__':
    main()
'''


if __name__ == '__main__':
    main()
