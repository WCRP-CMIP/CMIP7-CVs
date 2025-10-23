import os,re
import shutil
import subprocess
import tempfile
from typing import List, Tuple
import tarfile
import datetime
# from .. import locations
from .server import LocalServer, socketserver,http
# from ...locations import reverse_mapping
from ..git import io2repo
from ..logging.unique import UniqueLogger
log = UniqueLogger()
import urllib

# Apply global JSON-LD SSL compatibility patches
try:
    from .jsonld_ssl_debug import apply_global_jsonld_ssl_fix
    _ssl_restore_info = apply_global_jsonld_ssl_fix()
    log.debug("Global JSON-LD SSL compatibility patches applied")
except Exception as e:
    log.warn(f"Could not apply global SSL patches: {e}")
    _ssl_restore_info = None
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
        # '''
        # for _ in range(9):
        #     try:
        #         # we should know the redirects
        #         self.server = LocalServer(self.temp_dir.name, port,debug=True)
        #         break
        #     except:
        #         port += 1
        #         log.debug('Port in use, trying:'+ str(port))
        
        # with socketserver.TCPServer(("", 0), http.server.SimpleHTTPRequestHandler) as temp_server:
        #     free_port = temp_server.server_address[1]
        #     break
        
        self.server = LocalServer(self.temp_dir.name, debug=True, use_ssl=self.use_ssl)

        self.url = self.server.start_server()
        
        if not nojson:
            # {"wcrp-cmip.github.io":[{"regex_in" : re.compile(r'^(?!.*(_context_|\.json(?:ld|l)?)$).*'), "regex_out": ".json"}]} 
            self.server.requests.add_redirect(
                'wcrp-cmip.github.io',
                re.compile('^(?!.*(_context_|\\.json(?:ld)?|\/)$).*'),
                r'\g<0>.json'
            )
        
        for i in self.redirect_rules:
            for j in self.redirect_rules[i]:
                # self.server.redirect_rules[i]['regex_out'] = self.url+j['regex_out']
                
                self.server.requests.add_redirect(i, j['regex_in'],self.url+ j['regex_out'])
                
                
        # Finally if not set, make json files into json. 
        # This step is usually accomplished on the production branch and not an issue for the IO pages. 

                
        self.server.requests.list_redirects()
        
        # print('add the mappings here to the server')
        
        return self.url

    def stop_server(self):
        self.server.stop_server()
        self.server = None
        self.url = None
        # log.info("Server stopped.") displayed by server. 
