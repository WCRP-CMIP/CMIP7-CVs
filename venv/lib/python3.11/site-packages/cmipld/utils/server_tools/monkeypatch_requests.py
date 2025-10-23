import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse
import re

from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel


class PrefixResolvingSession(requests.Session):
    def __init__(self, prefix_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_map = prefix_map

    def request(self, method, url, *args, **kwargs):
        if ":" in url and not url.startswith(("http://", "https://")):
            prefix, path = url.split(":", 1)
            base = self.prefix_map.get(prefix)
            if base:
                url = base + path
            else:
                raise ValueError(f"Unknown prefix: {prefix}")
        return super().request(method, url, *args, **kwargs)


class URLRewritingAdapter(HTTPAdapter):
    def __init__(self, redirect_rules, **kwargs):
        self.redirect_rules = redirect_rules
        super().__init__(**kwargs)

    def send(self, request, **kwargs):
        parsed = urlparse(request.url)
        
        host = parsed.hostname

        rules = self.redirect_rules.get(host, [])
        for rule in rules:
            request.url = rule['regex_in'].sub( rule['regex_out'], request.url)
            request.headers['Host'] = urlparse(request.url).hostname  # Preserve original host

        return super().send(request, **kwargs)


class RequestRedirector:
    def __init__(self, redirect_rules={}, prefix_map=None):
        # self.redirect_rules = redirect_rules or {}
        self.redirect_rules = { 
            host: [
                {
                    **rule,
                    "regex_in": re.compile(rule["regex_in"]) 
                }
                for rule in rules
            ]
            for host, rules in redirect_rules.items()
        }
        
        self.default_rules = self.redirect_rules.copy()

        self.prefix_map = prefix_map or {}
        self.default_prefix_map = self.prefix_map.copy()

        self.default_session = requests.Session
        self._patch_requests()
        # self.list_redirects()
        

    def _patch_requests(self):
        session = PrefixResolvingSession(self.prefix_map)
        adapter = URLRewritingAdapter(self.redirect_rules)
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        requests.sessions.Session = lambda: session

    def restore_defaults(self):
        self.redirect_rules = self.default_rules.copy()
        self.prefix_map = self.default_prefix_map.copy()
        requests.sessions.Session = self.default_session
        print("Restored default session and redirect rules.")

    def add_redirect(self, host, regex_in, regex_out):
        self.redirect_rules.setdefault(host, []).append({
            "regex_in": re.compile(regex_in),
            "regex_out": regex_out
        })
        self._patch_requests()
        print(f"Added redirect: {host} | {regex_in} -> {regex_out}")

    def add_prefix(self, prefix, base_url):
        self.prefix_map[prefix] = base_url
        self._patch_requests()
        print(f"Added prefix: {prefix}: → {base_url}")

    def list_redirects(self):
        console = Console()
        table = Table(title="Regex-Based URL Redirects (by Host)", expand=True)

        table.add_column("Host", justify="center", style="cyan", no_wrap=True)
        table.add_column("Rules", justify="left", style="magenta")

        for host, rules in self.redirect_rules.items():
            host_panel = Panel(host, expand=True, width=30)
            rule_panels = [
                Panel(f"[bold]Match:[/bold] {rule['regex_in']}\n[bold]Replace:[/bold] {rule['regex_out']}", expand=True)
                for rule in rules
            ]
            rules_group = Group(*rule_panels)
            table.add_row(host_panel, rules_group)

        if self.prefix_map:
            prefix_panel = Panel(
                "\n".join(f"[cyan]{k}[/cyan]: {v}" for k, v in self.prefix_map.items()),
                title="Prefix Resolvers",
                border_style="green"
            )
            console.print(prefix_panel)

        console.print(table)

    @staticmethod
    def test_redirect(url, result=True):
        response = requests.get(url, verify=False)
        print(f"Original URL: {url}")
        print(f"Final URL: {response.url}")
        if result:
            print(f"Status Code: {response.status_code}")
            print(response.text[:300])

