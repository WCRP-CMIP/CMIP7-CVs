#!/usr/bin/env python3
"""
JSON File Validator and Fixer for CMIP-LD

This script validates and fixes JSON files in a directory structure, ensuring
they have required keys, proper ordering, matching IDs, and correct type prefixes.

Now includes support for adding Git co-authors when files are modified.
"""

import json
import os
import argparse
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Warning: tqdm not available. Install with 'pip install tqdm' for progress bars.")

from .logging.unique import UniqueLogger, logging
# Lazy import to avoid circular dependencies
git_coauthors = None

def _get_git_coauthors():
    global git_coauthors
    if git_coauthors is None:
        from .git import coauthors as _git_coauthors
        git_coauthors = _git_coauthors
    return git_coauthors

log = UniqueLogger()
log.logger.setLevel(logging.WARNING)  # Only show warnings and above by default

REQUIRED_KEYS = [
    'id',
    'validation-key',
    'ui-label',
    'description',
    '@context',
    'type'
]

DEFAULT_VALUES = {
    'id': '',
    'validation-key': '',
    'ui-label': '',
    '@context': '_context_',
    'type': [],
    'description': ''
}


class JSONValidator:
    def __init__(self, directory: str, max_workers: int = 4, dry_run: bool = False, 
                 add_coauthors: bool = False, use_last_author: bool = False,
                 auto_commit: bool = False):
        self.directory = Path(directory)
        self.max_workers = max_workers
        self.dry_run = dry_run
        self.add_coauthors = add_coauthors
        self.use_last_author = use_last_author
        self.auto_commit = auto_commit
        self.stats = {
            'processed': 0,
            'modified': 0,
            'errors': 0,
            'skipped': 0
        }
        self.stats_lock = Lock()
        self.modified_files = []
        self.modified_files_lock = Lock()
        
        # Check if we're in a git repo if co-author features are requested
        if (add_coauthors or use_last_author) and not _get_git_coauthors().is_git_repo(self.directory):
            log.warn("Not in a git repository. Co-author features will be disabled.")
            self.add_coauthors = False
            self.use_last_author = False

    def find_json_files(self) -> List[Path]:
        json_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(Path(root) / file)
        return json_files

    def validate_and_fix_json(self, file_path: Path) -> Tuple[bool, str]:
        if isinstance(file_path, str):
            file_path = Path(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content:
                return False, "Empty file"

            try:
                data = json.loads(content, object_pairs_hook=OrderedDict)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON: {e}"

            if not isinstance(data, dict):
                return False, "JSON root is not an object"

            modified = False
            current_filename = file_path.stem

            # Check required keys
            for key in REQUIRED_KEYS:
                if key not in data:
                    data[key] = DEFAULT_VALUES[key]
                    modified = True

            # Check ID
            if data.get('id') != current_filename:
                data['id'] = current_filename
                modified = True

            # Check type
            parent_folder = file_path.parent.name
            if parent_folder and parent_folder != '.':
                expected_type_part = f"wcrp:{parent_folder}"
                current_type = data.get('type', [])
                if not isinstance(current_type, list):
                    current_type = [current_type] if current_type else []
                if expected_type_part not in current_type:
                    current_type.append(expected_type_part)
                    data['type'] = current_type
                    modified = True

            # Check key order
            sorted_data = self.sort_json_keys(data)
            if list(data.keys()) != list(sorted_data.keys()):
                modified = True
                data = sorted_data
            else:
                data = sorted_data

            # Only write if modified
            if modified and not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    f.write('\n')
                with self.modified_files_lock:
                    self.modified_files.append(file_path)

            return modified, "Fixed" if modified else "Already valid"

        except Exception as e:
            log.debug(f"error {e}")
            return False, f"Error: {str(e)}"

    def sort_json_keys(self, data: Dict[str, Any]) -> OrderedDict:
        sorted_data = OrderedDict()
        priority_keys = ['id', 'validation-key', 'ui-label', 'description']
        for key in priority_keys:
            if key in data:
                sorted_data[key] = data[key]

        remaining_keys = sorted([
            k for k in data.keys()
            if k not in priority_keys and k not in ['@context', 'type']
        ])
        for key in remaining_keys:
            sorted_data[key] = data[key]

        if '@context' in data:
            sorted_data['@context'] = data['@context']
        if 'type' in data:
            sorted_data['type'] = data['type']

        return sorted_data

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        try:
            modified, message = self.validate_and_fix_json(file_path)

            with self.stats_lock:
                self.stats['processed'] += 1
                if modified:
                    self.stats['modified'] += 1

            return {
                'file': str(file_path.relative_to(self.directory)),
                'modified': modified,
                'message': message,
                'success': True
            }

        except Exception as e:
            with self.stats_lock:
                self.stats['errors'] += 1

            return {
                'file': str(file_path.relative_to(self.directory)),
                'modified': False,
                'message': f"Error: {str(e)}",
                'success': False
            }

    def run(self) -> bool:
        log.info(f"Scanning directory: {self.directory}")
        json_files = self.find_json_files()

        if not json_files:
            log.warn("No JSON files found")
            return True

        log.info(f"Found {len(json_files)} JSON files")

        if self.dry_run:
            log.info("🔍 DRY RUN MODE - No files will be modified")
            
        if self.add_coauthors:
            log.info("📝 Co-author mode enabled - will include historic authors for each file")
            
        if self.use_last_author:
            log.info("👤 Using last commit author mode")

        results = []

        if HAS_TQDM:
            progress = tqdm(total=len(json_files), desc="Processing JSON files", unit="file")
        else:
            progress = None
            log.debug(f"Processing {len(json_files)} files...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.process_file, file_path): file_path
                for file_path in json_files
            }

            for future in as_completed(future_to_file):
                result = future.result()
                
                # Only add to results if the file was modified or had an error
                if result['modified'] or not result['success']:
                    results.append(result)

                if progress:
                    progress.update(1)
                    progress.set_postfix({
                        'Modified': self.stats['modified'],
                        'Errors': self.stats['errors']
                    })
                else:
                    processed = self.stats['processed']
                    if processed % 10 == 0 or processed == len(json_files):
                        log.debug(f"Processed: {processed}/{len(json_files)} "
                                  f"(Modified: {self.stats['modified']}, Errors: {self.stats['errors']})")

        if progress:
            progress.close()

        self.report_results(results)
        
        # Handle auto-commit if requested
        if self.auto_commit and self.modified_files and not self.dry_run:
            self.create_commit_with_coauthors()
        
        return self.stats['errors'] == 0

    def create_commit_with_coauthors(self):
        """Create individual commits for each modified file with their respective co-authors."""
        if not self.modified_files:
            log.warn("No modified files to commit")
            return
            
        log.info(f"\n📦 Creating individual commits for {len(self.modified_files)} modified files...")
        
        successful_commits = 0
        failed_commits = 0
        
        for file_path in self.modified_files:
            # Get co-authors for this specific file
            coauthor_lines = _get_git_coauthors().get_coauthor_lines(file_path)
            
            # Create commit message for this file
            relative_path = file_path.relative_to(self.directory)
            commit_message = f"fix: validate and update {relative_path}\n\n" \
                            f"- Added missing required keys\n" \
                            f"- Fixed ID consistency\n" \
                            f"- Corrected type prefixes\n" \
                            f"- Reordered keys for consistency"
            
            # Add co-authors if any
            if coauthor_lines:
                commit_message += "\n\n" + "\n".join(coauthor_lines)
                log.info(f"\n📝 Committing {relative_path} with {len(coauthor_lines)} co-authors")
            else:
                log.info(f"\n📝 Committing {relative_path} (no co-authors found)")
            
            try:
                # Stage just this file
                subprocess.run(['git', 'add', str(file_path)], check=True)
                
                # Create commit
                result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    successful_commits += 1
                    log.debug(f"✅ Successfully committed {relative_path}")
                else:
                    failed_commits += 1
                    log.warn(f"❌ Failed to commit {relative_path}: {result.stderr}")
                    
            except subprocess.CalledProcessError as e:
                failed_commits += 1
                log.error(f"❌ Error committing {relative_path}: {e}")
        
        # Summary
        log.info(f"\n📊 Commit Summary:")
        log.info(f"   ✅ Successful commits: {successful_commits}")
        if failed_commits > 0:
            log.warn(f"   ❌ Failed commits: {failed_commits}")
        log.info(f"   Total: {len(self.modified_files)} files")

    def report_results(self, results: List[Dict[str, Any]]):
        print("\n" + "=" * 60)
        print("📊 PROCESSING SUMMARY")
        print("=" * 60)

        print(f"Total files processed: {self.stats['processed']}")
        print(f"Files modified: {self.stats['modified']}")
        print(f"Files already valid: {self.stats['processed'] - self.stats['modified'] - self.stats['errors']}")
        print(f"Errors encountered: {self.stats['errors']}")

        if self.dry_run and self.stats['modified'] > 0:
            print(f"\n💡 DRY RUN: {self.stats['modified']} files would be modified in actual run")

        errors = [r for r in results if not r['success']]
        if errors:
            print(f"\n❌ ERRORS ({len(errors)} files):")
            for error in errors[:10]:
                print(f"   {error['file']}: {error['message']}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more errors")

        modifications = [r for r in results if r['modified']]
        if modifications and len(modifications) <= 20:
            print(f"\n✅ MODIFIED FILES ({len(modifications)}):")
            for mod in modifications:
                print(f"   {mod['file']}")
        elif modifications:
            print(f"\n✅ MODIFIED: {len(modifications)} files (too many to list)")
            
        # Show co-author information if relevant
        if self.add_coauthors and self.modified_files and not self.dry_run:
            print(f"\n👥 CO-AUTHORS: Will create individual commits for {len(self.modified_files)} files")
            print("   Each file will be committed with its own historic authors")
            if self.auto_commit:
                print("   (Commits will be created automatically)")
            else:
                print("   (Use --auto-commit to create commits with co-authors)")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Validate and fix JSON files for CMIP-LD compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python -m cmipld.utils.validate_json .
  
  # Dry run to see what would change
  python -m cmipld.utils.validate_json /path/to/json/files --dry-run
  
  # Validate with more workers
  python -m cmipld.utils.validate_json /path/to/json/files --workers 8
  
  # Validate and add co-authors to modified files
  python -m cmipld.utils.validate_json . --add-coauthors
  
  # Validate, fix, and auto-commit with co-authors
  python -m cmipld.utils.validate_json . --add-coauthors --auto-commit
  
  # Use the last commit author instead of current user
  python -m cmipld.utils.validate_json . --use-last-author
        """
    )

    parser.add_argument('directory', help='Directory containing JSON files to validate')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Show changes without modifying files')
    parser.add_argument('--workers', '-w', type=int, default=4, help='Number of parallel workers (default: 4)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--add-coauthors', '-c', action='store_true', 
                       help='Add historic file authors as co-authors when modifying files')
    parser.add_argument('--use-last-author', '-l', action='store_true',
                       help='Use the author of the last commit instead of current user')
    parser.add_argument('--auto-commit', '-a', action='store_true',
                       help='Automatically create a commit with co-authors after modifications')

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"❌ Error: Directory '{args.directory}' does not exist")
        return 1

    if not os.path.isdir(args.directory):
        print(f"❌ Error: '{args.directory}' is not a directory")
        return 1

    if args.verbose:
        log.logger.setLevel(logging.DEBUG)
        log.debug("Verbose logging enabled")
        
    # Validate argument combinations
    if args.auto_commit and args.dry_run:
        print("❌ Error: Cannot use --auto-commit with --dry-run")
        return 1
        
    if args.auto_commit and not args.add_coauthors:
        print("ℹ️  Note: --auto-commit implies --add-coauthors")
        args.add_coauthors = True

    validator = JSONValidator(
        directory=args.directory,
        max_workers=args.workers,
        dry_run=args.dry_run,
        add_coauthors=args.add_coauthors,
        use_last_author=args.use_last_author,
        auto_commit=args.auto_commit
    )

    try:
        success = validator.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
