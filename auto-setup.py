#!/usr/bin/env python3
"""
Enhanced auto-setup script for MkDocs Publisher template.
Features: answer reuse, random color selection, create-new flag, FORCE OVERWRITE.
"""
import subprocess
import os
import json
import sys
import yaml
import random
import argparse
from pathlib import Path
from datetime import datetime

# Available header colors - sleek designer selection (Material Design compatible)
HEADER_COLORS = [
    'blue-grey', 'indigo', 'teal', 'cyan', 'deep-purple',
    'blue', 'green', 'grey', 'red', 'deep-orange',
    'purple', 'light-blue', 'orange', 'amber', 'pink',
    'light-green', 'lime', 'yellow', 'brown', 'black'
]

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Auto-setup MkDocs Publisher template',
        epilog='By default, previous configuration is automatically reused if found. Use --create-new for clean install.'
    )
    parser.add_argument('template_path', nargs='?', help='Path to copier template')
    parser.add_argument('destination', nargs='?', default='.', help='Destination directory (default: current directory)')
    parser.add_argument('--create-new', action='store_true', 
                       help='Create new configuration (clean install - ignores saved answers)')
    parser.add_argument('--color', choices=HEADER_COLORS, 
                       help='Header color theme (overrides saved color)')
    parser.add_argument('--no-confirm', action='store_true',
                       help='Skip confirmation prompts (for automation)')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity (no README content display)')
    parser.add_argument('--force-overwrite', action='store_true',
                       help='🔥 Force overwrite ALL files, ignoring _skip_if_exists exceptions')
    return parser.parse_args()


def install_dependencies():
    """Install required dependencies if needed."""
    try:
        import copier
        import yaml
        print("✅ Dependencies already available")
        return True
    except ImportError:
        print("📦 Installing required dependencies...")
        try:
            subprocess.run([
                "pip", "install", "copier", "pyyaml", "mkdocs-literate-nav"
            ], check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            return False


def run_command(cmd, capture=True, cwd=None):
    """Run a command and return output or success status."""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
            return result.stdout.strip() if result.returncode == 0 else None
        else:
            result = subprocess.run(cmd, shell=True, cwd=cwd)
            return result.returncode == 0
    except Exception as e:
        print(f"⚠️  Command failed: {e}")
        return None


def get_github_username():
    """Get GitHub username using gh CLI."""
    username = run_command("gh api user --jq .login")
    if username:
        return username
    
    # Fallback: try gh auth status
    auth_output = run_command("gh auth status 2>&1")
    if auth_output and "Logged in to github.com" in auth_output:
        for line in auth_output.split('\\n'):
            if ' as ' in line and 'github.com' in line:
                username = line.split(' as ')[-1].split(' ')[0]
                if username and username != 'github.com':
                    return username
    return None


def get_git_config(key, default=""):
    """Get git config value."""
    value = run_command(f"git config --get {key}")
    return value if value else default


def get_remote_info():
    """Get git remote information and extract GitHub username/repo."""
    remote_url = run_command("git remote get-url origin")
    
    if not remote_url or 'github.com' not in remote_url:
        return None, None
    
    # Parse GitHub URL
    repo_path = remote_url
    
    # Handle different URL formats
    if remote_url.startswith('https://github.com/'):
        repo_path = remote_url.replace('https://github.com/', '')
    elif remote_url.startswith('git@github.com:'):
        repo_path = remote_url.replace('git@github.com:', '')
    elif 'https://' in remote_url and '@github.com/' in remote_url:
        repo_path = remote_url.split('@github.com/')[-1]
    
    # Clean up
    repo_path = repo_path.replace('.git', '').strip()
    
    if '/' in repo_path:
        parts = repo_path.split('/')
        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()
    
    return None, None


def save_answers(data, answers_file=".copier-answers.yml"):
    """Save answers to YAML file with metadata."""
    try:
        answers_with_meta = {
            '_src_path': data.get('template_path', ''),
            '_commit': 'HEAD',
            '_timestamp': datetime.now().isoformat(),
            '_auto_generated': True,
            '_script_version': '2.1'
        }
        
        # Add actual answers (excluding template_path)
        answers_with_meta.update({k: v for k, v in data.items() if k != 'template_path'})
        
        with open(answers_file, 'w') as f:
            yaml.dump(answers_with_meta, f, default_flow_style=False, sort_keys=False)
        
        print(f"💾 Saved configuration to {answers_file}")
        return True
        
    except Exception as e:
        print(f"⚠️  Error saving answers: {e}")
        return False


def load_previous_answers(answers_file=".copier-answers.yml"):
    """Load previous answers from YAML file."""
    answers_path = Path(answers_file)
    
    if not answers_path.exists():
        return None
    
    try:
        with open(answers_path, 'r') as f:
            answers = yaml.safe_load(f)
        
        if not answers:
            return None
        
        # Extract metadata
        metadata = {
            'src_path': answers.get('_src_path', ''),
            'timestamp': answers.get('_timestamp', ''),
            'auto_generated': answers.get('_auto_generated', False),
            'version': answers.get('_script_version', '1.0')
        }
        
        # Extract data (non-metadata)
        data = {k: v for k, v in answers.items() if not k.startswith('_')}
        
        return data, metadata
        
    except Exception as e:
        print(f"⚠️  Error loading previous answers: {e}")
        return None


def detect_template_path():
    """Detect template path relative to this script."""
    script_path = Path(__file__).parent
    
    possible_paths = [
        script_path,
        script_path.parent / "copier" / "mkdocs",
        Path.cwd() / "copier" / "mkdocs",
        script_path.parent.parent / "copier" / "mkdocs",
    ]
    
    for path in possible_paths:
        if (path / "copier.yml").exists():
            return str(path.resolve())
    
    return None


def select_random_color():
    """Select a random header color."""
    color = random.choice(HEADER_COLORS)
    print(f"🎨 Selected random color: {color}")
    return color


def validate_configuration(data):
    """Double-check and validate configuration."""
    print("\\n🔍 Validating configuration...")
    
    issues = []
    warnings = []
    
    # Required fields
    required_fields = ['project_name', 'repo_name', 'github_username']
    for field in required_fields:
        if not data.get(field):
            issues.append(f"Missing required field: {field}")
    
    # GitHub username validation
    username = data.get('github_username', '')
    if username and not username.replace('-', '').replace('_', '').isalnum():
        warnings.append(f"GitHub username '{username}' contains special characters")
    
    # Repo name validation
    repo_name = data.get('repo_name', '')
    if repo_name and ' ' in repo_name:
        warnings.append(f"Repository name '{repo_name}' contains spaces")
    
    # URL validation
    site_url = data.get('site_url', '')
    repo_url = data.get('repo_url', '')
    if site_url and not site_url.startswith('https://'):
        warnings.append("Site URL should start with https://")
    if repo_url and not repo_url.startswith('https://github.com/'):
        warnings.append("Repository URL should be a GitHub URL")
    
    # Template path validation
    template_path = data.get('template_path', '')
    if template_path and not Path(template_path).exists():
        issues.append(f"Template path does not exist: {template_path}")
    
    # Report issues
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    if warnings:
        print("⚠️  Configuration warnings:")
        for warning in warnings:
            print(f"   • {warning}")
    else:
        print("✅ Configuration looks good!")
    
    return True


def run_copier_with_data(template_path, data, destination=".", no_confirm=False, force_overwrite=False):
    """Run copier with the provided data using subprocess for proper escaping."""
    cmd = ["copier", "copy", template_path, destination]
    
    # Add overwrite flags
    if force_overwrite:
        cmd.extend(["--overwrite", "--force"])
        print("🔥 Force overwrite mode: ignoring _skip_if_exists exceptions")
    else:
        cmd.append("--overwrite")
    
    # Add data arguments with proper escaping
    for key, value in data.items():
        if key != 'template_path':
            # Convert value to string
            str_value = str(value)
            cmd.extend(["--data", f"{key}={str_value}"])
    
    # Add flags
    if no_confirm:
        cmd.append("--quiet")
    
    print(f"\\n🔄 Running copier...")
    if force_overwrite:
        print("   ⚠️  Force mode: Will overwrite ALL files including protected ones")
    
    if not no_confirm:
        print(f"   Command: copier copy {template_path} {destination}")
        if force_overwrite:
            confirm = input("\\n⚠️  FORCE OVERWRITE: This will replace ALL files. Proceed? [y/N]: ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("❌ Cancelled by user")
                return False
        else:
            confirm = input("\\nProceed with generation? [Y/n]: ").strip().lower()
            if confirm and confirm not in ['y', 'yes', '']:
                print("❌ Cancelled by user")
                return False
    
    # Use subprocess.run with list for proper argument handling
    try:
        result = subprocess.run(cmd, cwd=None)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running copier: {e}")
        return False


def create_new_configuration(args):
    """Create new configuration from scratch."""
    print("🔍 Detecting project information...")
    
    # Basic detection
    github_username = get_github_username()
    if github_username:
        print(f"✅ GitHub user: {github_username}")
    else:
        print("⚠️  GitHub CLI not authenticated")
    
    git_user = get_git_config('user.name', 'Your Name')
    git_email = get_git_config('user.email', 'your.email@example.com')
    
    remote_username, remote_repo = get_remote_info()
    if remote_username and remote_repo:
        print(f"✅ Git remote: {remote_username}/{remote_repo}")
        username = remote_username
        repo_name = remote_repo
    else:
        username = github_username or 'your-username'
        repo_name = Path.cwd().name
    
    project_name = repo_name.replace('-', ' ').replace('_', ' ')
    
    # Select color
    if args.color:
        header_color = args.color
        print(f"🎨 Using specified color: {header_color}")
    else:
        header_color = select_random_color()
    
    # Get template path
    template_path = args.template_path or detect_template_path()
    if not template_path:
        print("❌ Template path not found!")
        print("Usage: python auto-setup.py /path/to/template")
        sys.exit(1)
    
    # Build configuration
    data = {
        'project_name': f"{project_name} Documentation",
        'repo_name': repo_name,
        'author_name': git_user,
        'author_email': git_email,
        'github_username': username,
        'site_url': f"https://{username}.github.io/{repo_name}/",
        'repo_url': f"https://github.com/{username}/{repo_name}",
        'json_data_folder': 'json_data',
        'description': f"Documentation for {project_name}",
        'template_path': template_path,
        'header_color': header_color,
        'generate_static_files': True,
        'static_files_folder': 'static_output'
    }
    
    if not args.quiet:
        print("\\n📋 Configuration:")
        for key, value in data.items():
            if key == 'readme_content':
                print(f"   {key}: {str(value)[:50]}...")
            else:
                print(f"   {key}: {value}")
    
    return data


def print_next_steps(data):
    """Print next steps after successful generation."""
    print("\\n✅ Project generated successfully!")
    
    # Show configuration info
    print(f"   🎨 Theme color: {data.get('header_color', 'blue')}")
    print(f"   👤 Repository: {data.get('github_username', 'unknown')}/{data.get('repo_name', 'unknown')}")
    
    print("\\n📝 Next steps:")
    print("   1. mkdocs serve                     # Start development server")
    print("   2. mkdocs gh-deploy                 # Deploy to GitHub Pages")
    
    # Check key files
    key_files = ["mkdocs.yml", "docs/index.md", ".github/workflows"]
    print("\\n📄 Generated files:")
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
    
    # Tips
    json_folder = data.get('json_data_folder', 'json_data')
    if not Path(json_folder).exists():
        print(f"\\n💡 Tip: Create {json_folder}/ folder and add .json files for auto-generated pages")
    
    print(f"\\n💾 Configuration saved to .copier-answers.yml")
    print(f"   🔄 Next run will automatically reuse this configuration")
    print(f"   🆕 Use --create-new flag to force clean install")
    print(f"   🔥 Use --force-overwrite to ignore _skip_if_exists exceptions")


def main():
    """Enhanced main function with automatic answer reuse and force overwrite."""
    args = parse_arguments()
    
    print("🚀 MkDocs Publisher Auto-Setup v2.1")
    if args.force_overwrite:
        print("🔥 FORCE OVERWRITE MODE ENABLED")
    
    # Install dependencies if needed
    if not install_dependencies():
        sys.exit(1)
    
    answers_file = ".copier-answers.yml"
    
    # Check for create-new flag (clean install)
    if args.create_new:
        print("🆕 Creating new configuration (--create-new flag)")
        data = create_new_configuration(args)
    else:
        # Try to load and auto-reuse previous answers
        previous_data = load_previous_answers(answers_file)
        
        if previous_data:
            data, metadata = previous_data
            print("✅ Found previous configuration - auto-reusing")
            
            # Show what we're reusing
            print(f"   📁 Project: {data.get('project_name', 'Unknown')}")
            print(f"   🎨 Color: {data.get('header_color', 'blue')}")
            print(f"   👤 GitHub: {data.get('github_username', 'Unknown')}/{data.get('repo_name', 'Unknown')}")
            if metadata.get('timestamp'):
                try:
                    timestamp = datetime.fromisoformat(metadata['timestamp'])
                    print(f"   🕐 Created: {timestamp.strftime('%Y-%m-%d %H:%M')}")
                except:
                    pass
            
            # Override color if specified
            if args.color and args.color != data.get('header_color'):
                print(f"🎨 Overriding color: {data.get('header_color')} → {args.color}")
                data['header_color'] = args.color
            
            # Update template path if provided
            template_path = args.template_path or metadata.get('src_path') or detect_template_path()
            if template_path:
                data['template_path'] = template_path
            else:
                print("❌ Template path not found")
                sys.exit(1)
        else:
            print("📝 No previous configuration found, creating new")
            data = create_new_configuration(args)
    
    # Validate configuration
    if not validate_configuration(data):
        print("❌ Configuration validation failed")
        sys.exit(1)
    
    # Save configuration
    save_answers(data, answers_file)
    
    # Run copier with force overwrite option
    success = run_copier_with_data(
        data['template_path'], 
        data, 
        args.destination, 
        args.no_confirm,
        args.force_overwrite
    )
    
    if success:
        print_next_steps(data)
    else:
        print("❌ Failed to generate project")
        sys.exit(1)


if __name__ == "__main__":
    main()
