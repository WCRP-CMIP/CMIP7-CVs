import os, re
import shutil
import subprocess
import tempfile
from typing import List, Tuple
import tarfile
import datetime
import argparse
# from .. import locations
from .server_patched import LocalServer, socketserver, http
# from ...locations import reverse_mapping
from ..git import io2repo
from ..logging.unique import UniqueLogger
log = UniqueLogger()
import urllib

class LD_server:
    def __init__(self, repos=None, zipfile=None, copy=None, override=None, use_ssl=None):
        '''
        If None provided all the cmipld repositories will be generated. 

        repos: List of tuples where each tuple is (repo_url, target_name).
        zipfile: Path to the tar.gz file.
        use_ssl: True to force SSL, False to disable SSL, None for auto-detection

        '''
        self.temp_dir = None
        self.use_ssl = use_ssl
        self.create_temp_dir()
        self.redirect_rules = {}

        # ignore
        # if not repos and not zipfile:
        #     print('No repositories or zip file provided. Generating all repositories')
        #     repos = location.reverse_mapping()

        if zipfile:
            self.from_zip(zipfile, override=override)
        if repos:
            self.clone_repos(repos, override=override)
        if copy:
            self.copy_existing_repos(copy, override=override)

    def create_temp_dir(self):
        """Create a temporary directory to hold repositories."""
        if not self.temp_dir:
            self.temp_dir = tempfile.TemporaryDirectory(
                prefix='cmipld_local_', suffix=datetime.datetime.now().isoformat().split('.')[0])
        return self.temp_dir.name

    def delete_temp_dir(self):
        """Delete the temporary directory."""
        if self.temp_dir:
            self.temp_dir.cleanup()
            self.temp_dir = None

    def clone_repos(self, repos: List[Tuple[str, str]], branch="production", dir='src-data', override='n'):
        """
        Clone a list of git repositories into the temporary directory.
        Args:
            repos: List of tuples where each tuple is (repo_url, target_name).
            branch: Branch to clone (default: 'production').
        """
        for repo_url, target_name in repos:
            print(repo_url, target_name, self.temp_dir.name)
            repo_path = os.path.join(self.temp_dir.name, target_name)

            if '.io' in repo_url:
                repo_url = io2repo(repo_url)

            if os.path.exists(repo_path):
                if override != 'y':
                    override = input(
                        f"Repo '{target_name}' already exists. Delete and replace? (y/n): ").lower()

                if override == 'y':
                    shutil.rmtree(repo_path)
                else:
                    log.warn(f'Repo {target_name} not replaced')
                    continue

            clone = os.popen(' '.join(
                ["git", "clone", "--branch", branch, "--single-branch", repo_url, repo_path])).read()
            log.debug(clone)

            assert 'fatal' not in clone

            # move the relevant repo into place. This is because our production branch serves only the src-data directory
            log.debug(os.popen(f'mv {repo_path}/{dir}/* {repo_path}').read())

        log.info(f"Repositories cloned into {self.temp_dir}")

    def copy_existing_repos(self, repo_paths: List[str], override='n'):
        """
        Copy existing repositories into the temporary directory.
        Args:
            repo_paths: List of file paths to existing repositories.

        E.g. [[path1,name1],[path2,name2]]
        """
        for tocopy in repo_paths:
            if len(tocopy) == 3:
                repo_path, repo_url, repo_name = tocopy
            else:
                raise ValueError(tocopy)
                # repo_path = tocopy
                # repo_name = tocopy
                # repo_url = tocopy

            log.debug(f'Copying the repo into LocalServer [#FF7900] {repo_path} --> {repo_name} [/]')

            # URL parsing functions for server
            parsed = urllib.parse.urlparse(repo_url)
            host = parsed.netloc
            path = parsed.path

            if host not in self.redirect_rules:
                # create a new rule for the host
                self.redirect_rules[host] = []
            self.redirect_rules[host].append({
                "regex_in": re.compile(rf"^{repo_url}"),
                "regex_out": f"/{repo_name}/"
            })

            # add to monkeypatch
            target_name = os.path.basename(repo_name)
            target_path = os.path.join(self.temp_dir.name, target_name)

            if os.path.exists(target_path):
                if override != 'y':
                    override = input(
                        f"Repo '{target_name}' already exists. Delete and replace? (y/n): ").lower()

                if override == 'y':
                    shutil.rmtree(target_path)
                else:
                    continue
            shutil.copytree(repo_path, target_path)

        log.debug(f"Repositories copied into [#FF7900] {self.temp_dir} [/]")

    def rollback_repo(self, repo_name: str, commit_hash: str):
        """
        Roll back a repository to a specific commit.
        Args:
            repo_name: Name of the repository to roll back.
            commit_hash: Commit hash to roll back to.
        """
        temp_dir = self.create_temp_dir()
        repo_path = os.path.join(temp_dir.name, repo_name)

        if not os.path.exists(repo_path):
            raise FileNotFoundError(
                f"Repository '{repo_name}' not found in {temp_dir}")

        subprocess.run(["git", "checkout", commit_hash],
                       cwd=repo_path, check=True)
        log.warn(f"Repository '{repo_name}' rolled back to commit {commit_hash}")

    def to_zip(self, output_file: str):
        """
        Create a gzipped tarball of the temporary directory.
        Args:
            output_file: Output tar.gz file path.
        """
        temp_dir = self.create_temp_dir()
        with tarfile.open(output_file, "w:gz") as tar:
            tar.add(temp_dir, arcname=os.path.basename(temp_dir.name))
        log.info(f"Repositories compressed into {output_file}")

    def from_zip(self, zip_path: str, override='n'):
        """
        Extract repositories from a gzipped tarball.
        Args:
            zip_path: Path to the tar.gz file.
            override: Override existing files ('y' or 'n')
        """
        temp_dir = self.create_temp_dir()
        with tarfile.open(zip_path, "r:gz") as tar:
            tar.extractall(temp_dir.name)
        log.info(f"Repositories extracted into {temp_dir}")

    def start_server(self, port=8081, nojson=False):
        '''
        Serve the directory at the specified port.
        '''
        # Pass the SSL configuration to LocalServer
        self.server = LocalServer(self.temp_dir.name, debug=True, use_ssl=self.use_ssl)

        self.url = self.server.start_server()

        if not nojson:
            # Add JSON redirect rule for wcrp-cmip.github.io
            self.server.requests.add_redirect(
                'wcrp-cmip.github.io',
                re.compile('^(?!.*(_context_|\\.json(?:ld)?|\/)$).*'),
                r'\g<0>.json'
            )

        # Apply custom redirect rules
        for i in self.redirect_rules:
            for j in self.redirect_rules[i]:
                self.server.requests.add_redirect(i, j['regex_in'], self.url + j['regex_out'])

        # List all redirects for debugging
        self.server.requests.list_redirects()

        return self.url

    def stop_server(self):
        self.server.stop_server()
        self.server = None
        self.url = None


def main():
    """Command line interface for LD_server with SSL options."""
    parser = argparse.ArgumentParser(
        description="CMIP-LD Local Server with SSL/TLS support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect SSL capability (default)
  python -m cmipld.utils.server_tools.offline --repos repo1,repo2
  
  # Force disable SSL (HTTP only)
  python -m cmipld.utils.server_tools.offline --no-ssl --repos repo1,repo2
  
  # Force enable SSL (will fail if neither OpenSSL nor cryptography available)
  python -m cmipld.utils.server_tools.offline --ssl --repos repo1,repo2
        """
    )
    
    # SSL options (mutually exclusive)
    ssl_group = parser.add_mutually_exclusive_group()
    ssl_group.add_argument(
        '--no-ssl', 
        action='store_true',
        help='Disable SSL/TLS - serve over HTTP only (useful when OpenSSL not available)'
    )
    ssl_group.add_argument(
        '--ssl', 
        action='store_true',
        help='Force enable SSL/TLS - will fail if SSL setup is not possible'
    )
    
    # Server options
    parser.add_argument('--port', type=int, default=8081, help='Port to serve on (default: 8081)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--nojson', action='store_true', help='Disable automatic .json suffix redirects')
    
    # Repository options
    parser.add_argument('--repos', help='Comma-separated list of repositories to clone')
    parser.add_argument('--zipfile', help='Path to tar.gz file to extract')
    parser.add_argument('--copy', help='Comma-separated list of local repository paths to copy')
    parser.add_argument('--override', choices=['y', 'n'], default='n', 
                       help='Override existing repositories without prompting (default: n)')
    
    args = parser.parse_args()
    
    # Determine SSL setting
    use_ssl = None  # Auto-detect by default
    if args.no_ssl:
        use_ssl = False
        log.info("SSL explicitly disabled - server will use HTTP")
    elif args.ssl:
        use_ssl = True
        log.info("SSL explicitly enabled - server will attempt HTTPS")
    
    # Parse repository lists
    repos = None
    if args.repos:
        repo_list = args.repos.split(',')
        repos = [(repo.strip(), repo.strip().split('/')[-1]) for repo in repo_list]
    
    copy_repos = None
    if args.copy:
        copy_list = args.copy.split(',')
        copy_repos = [[path.strip(), path.strip(), os.path.basename(path.strip())] for path in copy_list]
    
    try:
        # Create and start server
        server = LD_server(
            repos=repos,
            zipfile=args.zipfile,
            copy=copy_repos,
            override=args.override,
            use_ssl=use_ssl
        )
        
        url = server.start_server(port=args.port, nojson=args.nojson)
        log.info(f"Server started at: {url}")
        log.info("Press Ctrl+C to stop the server")
        
        # Keep the server running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Stopping server...")
            server.stop_server()
            
    except Exception as e:
        log.error(f"Failed to start server: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
