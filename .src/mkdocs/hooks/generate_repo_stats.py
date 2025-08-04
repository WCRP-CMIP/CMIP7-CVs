
#!/usr/bin/env python3
"""
Repository statistics generator that creates a top-level stats page.
Uses gh CLI commands to extract actual repository data.
"""

import json
import subprocess
import sys
from datetime import datetime
import mkdocs_gen_files

class StatsGenerator:
    def __init__(self, repo_owner="WCRP-CMIP", repo_name="CMIP7-CVs"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo = f"{repo_owner}/{repo_name}"
        
    def run_gh_command(self, command):
        """Run a gh command and return JSON result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout.strip()) if result.stdout.strip() else {}
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return {}
    
    def run_gh_command_text(self, command):
        """Run a gh command and return text result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    def get_repo_stats(self):
        """Get basic repository statistics."""
        return self.run_gh_command(f'gh repo view {self.repo} --json stargazerCount,forkCount,watchers,openIssues,createdAt,updatedAt,pushedAt,size,defaultBranchRef,licenseInfo,isPrivate,visibility')
    
    def get_contributors(self):
        """Get contributor information."""
        contributors = self.run_gh_command(f'gh api repos/{self.repo}/contributors --paginate')
        return contributors if isinstance(contributors, list) else []
    
    def get_languages(self):
        """Get programming languages."""
        return self.run_gh_command(f'gh api repos/{self.repo}/languages')
    
    def get_traffic_views(self):
        """Get traffic view statistics."""
        return self.run_gh_command(f'gh api repos/{self.repo}/traffic/views')
    
    def get_traffic_clones(self):
        """Get traffic clone statistics."""
        return self.run_gh_command(f'gh api repos/{self.repo}/traffic/clones')
    
    def get_popular_paths(self):
        """Get popular paths/files."""
        paths = self.run_gh_command(f'gh api repos/{self.repo}/traffic/popular/paths')
        return paths if isinstance(paths, list) else []
    
    def get_referrers(self):
        """Get referrer statistics."""
        referrers = self.run_gh_command(f'gh api repos/{self.repo}/traffic/popular/referrers')
        return referrers if isinstance(referrers, list) else []
    
    def get_releases(self):
        """Get release information."""
        releases = self.run_gh_command(f'gh api repos/{self.repo}/releases --paginate')
        return releases[:10] if isinstance(releases, list) else []  # Top 10 releases
    
    def get_issue_stats(self):
        """Get issue and PR statistics."""
        open_issues = self.run_gh_command_text(f'gh api search/issues -f q="repo:{self.repo} type:issue state:open" --jq ".total_count"')
        closed_issues = self.run_gh_command_text(f'gh api search/issues -f q="repo:{self.repo} type:issue state:closed" --jq ".total_count"')
        open_prs = self.run_gh_command_text(f'gh api search/issues -f q="repo:{self.repo} type:pr state:open" --jq ".total_count"')
        closed_prs = self.run_gh_command_text(f'gh api search/issues -f q="repo:{self.repo} type:pr state:closed" --jq ".total_count"')
        
        return {
            'open_issues': int(open_issues) if open_issues.isdigit() else 0,
            'closed_issues': int(closed_issues) if closed_issues.isdigit() else 0,
            'open_prs': int(open_prs) if open_prs.isdigit() else 0,
            'closed_prs': int(closed_prs) if closed_prs.isdigit() else 0
        }
    

    
    def generate_stats_page(self):
        """Generate the statistics page."""
        print("Extracting repository statistics via gh CLI...")
        
        # Get current timestamp
        run_time = datetime.now().strftime('%Y-%m-%d at %H:%M:%S UTC')
        
        # Extract all statistics
        repo_stats = self.get_repo_stats()
        contributors = self.get_contributors()
        languages = self.get_languages()
        traffic_views = self.get_traffic_views()
        traffic_clones = self.get_traffic_clones()
        popular_paths = self.get_popular_paths()
        referrers = self.get_referrers()
        releases = self.get_releases()
        issue_stats = self.get_issue_stats()
        
        # Start building the content with prettier design
        content = f"""# Repository Statistics

!!! info "Generation Information"
    **Generated on:** {run_time}  
    **Data source:** Real-time GitHub CLI extraction

## Repository Overview

| :material-database: Size | :material-source-branch: Default Branch | :material-sync: Last Push |
|:----------------------------:|:-----------------------------:|:-----------------------------:|
| **{repo_stats.get('size', 0) / 1024:.1f} MB** | **{repo_stats.get('defaultBranchRef', {}).get('name', 'main')}** | **{repo_stats.get('pushedAt', '')[:10]}** |

"""
        
        # Traffic Statistics
        total_views = traffic_views.get('count', 0)
        unique_visitors = traffic_views.get('uniques', 0)
        total_clones = traffic_clones.get('count', 0)
        unique_cloners = traffic_clones.get('uniques', 0)
        
        content += f"""## Traffic Statistics (Last 14 Days)

| :chart_with_upwards_trend: Total Views | :busts_in_silhouette: Unique Visitors | :arrow_down: Total Clones | :bust_in_silhouette: Unique Cloners |
|:--------------------------------:|:-------------------------------------:|:------------------------------------:|:------------------------------------:|
| **{total_views:,}** | **{unique_visitors:,}** | **{total_clones:,}** | **{unique_cloners:,}** |

"""
        
        # Popular Files
        if popular_paths:
            content += """## Most Popular Files

| Rank | Path | Views | Unique Visitors |
|------|------|-------|-----------------|
"""
            for i, path in enumerate(popular_paths[:15], 1):
                file_path = path.get('path', '')
                views = path.get('count', 0)
                uniques = path.get('uniques', 0)
                content += f"| {i} | `{file_path}` | {views:,} | {uniques:,} |\n"
        
        # Traffic Sources
        if referrers:
            content += """
## Traffic Sources

| Rank | Referrer | Views | Unique Visitors |
|------|----------|-------|-----------------|
"""
            for i, referrer in enumerate(referrers[:15], 1):
                source = referrer.get('referrer', 'Direct')
                views = referrer.get('count', 0)
                uniques = referrer.get('uniques', 0)
                content += f"| {i} | {source} | {views:,} | {uniques:,} |\n"
        
        # Programming Languages
        if languages:
            total_bytes = sum(languages.values())
            content += """
## Programming Languages

| Language | Bytes | Percentage |
|----------|-------|------------|
"""
            for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
                content += f"| {lang} | {bytes_count:,} | {percentage:.1f}% |\n"
        
        # Issues and Pull Requests
        total_issues = issue_stats['open_issues'] + issue_stats['closed_issues']
        total_prs = issue_stats['open_prs'] + issue_stats['closed_prs']
        issue_close_rate = (issue_stats['closed_issues'] / total_issues * 100) if total_issues > 0 else 0
        pr_close_rate = (issue_stats['closed_prs'] / total_prs * 100) if total_prs > 0 else 0
        
        content += f"""
## Issues and Pull Requests

| :green_circle: Open Issues | :red_circle: Closed Issues | :arrows_counterclockwise: Open PRs | :white_check_mark: Closed PRs |
|:---------------------------------------:|:-----------------------------------------:|:----------------------------------------:|:--------------------------------------------------:|
| **{issue_stats['open_issues']:,}** | **{issue_stats['closed_issues']:,}** ({issue_close_rate:.1f}% close rate) | **{issue_stats['open_prs']:,}** | **{issue_stats['closed_prs']:,}** ({pr_close_rate:.1f}% close rate) |

"""
        
        # Releases
        if releases:
            content += f"""## Recent Releases

**Total Releases:** {len(releases)}

| Release | Tag | Published |
|---------|-----|-----------|
"""
            for release in releases[:10]:
                name = release.get('name') or release.get('tag_name', 'Unnamed')
                tag = release.get('tag_name', 'N/A')
                published = release.get('published_at', '')[:10]
                content += f"| {name} | `{tag}` | {published} |\n"
        
        # Contributors section - moved to bottom
        content += f"""
## Contributors

**Total Contributors:** {len(contributors)}

| Rank | Contributor | Contributions | Avatar |
|------|-------------|---------------|--------|
"""
        
        # Add top 20 contributors with avatars
        for i, contributor in enumerate(contributors[:20], 1):
            username = contributor.get('login', 'Unknown')
            contributions = contributor.get('contributions', 0)
            avatar_url = contributor.get('avatar_url', '')
            avatar_html = f'<img src="{avatar_url}" width="40" height="40" style="border-radius: 50%" alt="{username}">' if avatar_url else ''
            content += f"| {i} | {username} | {contributions:,} | {avatar_html} |\n"
        
        # Create assets directory for visualizations
        try:
            with mkdocs_gen_files.open("assets/.gitkeep", "w") as f:
                f.write("")
            print("✅ Created assets directory", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Could not create assets directory: {e}", file=sys.stderr)
            
        # Create auxillary directory if it doesn't exist
        try:
            with mkdocs_gen_files.open("auxillary/.gitkeep", "w") as f:
                f.write("")
            print("✅ Created auxillary directory", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Could not create auxillary directory: {e}", file=sys.stderr)
            
        # Write the file to auxillary directory as specified
        with mkdocs_gen_files.open("auxillary/stats.md", "w") as f:
            f.write(content)
        
        # Also create a time series visualization of GitHub activity if available
        try:
            # Get commit activity from GitHub CLI
            print("Extracting commit activity data from GitHub...", file=sys.stderr)
            commit_activity = self.run_gh_command(f'gh api repos/{self.repo}/stats/commit_activity')
            
            if commit_activity and isinstance(commit_activity, list) and len(commit_activity) > 0:
                print(f"✅ Found commit activity data ({len(commit_activity)} weeks)", file=sys.stderr)
                
                # Process commit data for time series
                weeks = []
                commits = []
                
                # Last 52 weeks of data
                for i, week_data in enumerate(commit_activity[-52:]):
                    if 'week' in week_data and 'total' in week_data:
                        # Convert Unix timestamp to date
                        week_timestamp = week_data['week']
                        week_date = datetime.fromtimestamp(week_timestamp).strftime('%Y-%m-%d')
                        weeks.append(week_date)
                        commits.append(week_data['total'])
                
                if weeks and commits:
                    # Create time series visualization
                    time_series_data = {
                        "data": [
                            {
                                "type": "scatter",
                                "mode": "lines+markers",
                                "x": weeks,
                                "y": commits,
                                "name": "Weekly Commits",
                                "line": {"color": "rgb(70, 130, 180)", "width": 2},
                                "marker": {"size": 5, "color": "rgb(70, 130, 180)"}
                            }
                        ],
                        "layout": {
                            "title": "Repository Activity",
                            "xaxis": {"title": "Week", "tickangle": 45},
                            "yaxis": {"title": "Commits"},
                            "margin": {"l": 60, "r": 40, "t": 80, "b": 120},
                            "height": 400,
                            "width": 700
                        }
                    }
                    
                    # Create time series visualization with simple format
                    time_series_file = "commits_time_series.json"
                    
                    with mkdocs_gen_files.open(f"assets/{time_series_file}", "w") as f:
                        f.write(json.dumps(time_series_data, indent=2))
                    
                    # Add time series visualization to stats page with plain HTML
                    time_series_content = """## Commit Activity

This chart shows the weekly commit activity for the repository over time.

<div id="commit-activity-chart" style="height:400px; width:100%;"></div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Plotly !== 'undefined') {
        fetch('../../assets/commits_time_series.json')
            .then(response => response.json())
            .then(data => {
                Plotly.newPlot('commit-activity-chart', data.data, data.layout);
            })
            .catch(error => console.error('Error loading chart data:', error));
    } else {
        console.error('Plotly is not loaded');
    }
});
</script>
"""
                    
                    # Append to the auxillary file
                    with mkdocs_gen_files.open("auxillary/stats.md", "a") as f:
                        f.write(time_series_content)
                    
                    print("✅ Added commit activity time series visualization", file=sys.stderr)
                else:
                    print("⚠️ No usable commit data found", file=sys.stderr)
            else:
                print("⚠️ No commit activity data available", file=sys.stderr)
                
            # Also get code frequency (additions/deletions)
            code_frequency = self.run_gh_command(f'gh api repos/{self.repo}/stats/code_frequency')
            
            if code_frequency and isinstance(code_frequency, list) and len(code_frequency) > 0:
                print(f"✅ Found code frequency data ({len(code_frequency)} weeks)", file=sys.stderr)
                
                # Process code frequency data
                weeks = []
                additions = []
                deletions = []
                
                # Last 52 weeks of data
                for i, week_data in enumerate(code_frequency[-52:]):
                    if len(week_data) >= 3:
                        # Convert Unix timestamp to date
                        week_timestamp = week_data[0]
                        week_date = datetime.fromtimestamp(week_timestamp).strftime('%Y-%m-%d')
                        weeks.append(week_date)
                        additions.append(week_data[1])  # Additions
                        deletions.append(-week_data[2])  # Convert deletions to positive for visualization
                
                if weeks and additions and deletions:
                    # Create code frequency visualization
                    code_frequency_data = {
                        "data": [
                            {
                                "type": "bar",
                                "x": weeks,
                                "y": additions,
                                "name": "Additions",
                                "marker": {"color": "rgb(75, 192, 192)"}
                            },
                            {
                                "type": "bar",
                                "x": weeks,
                                "y": deletions,
                                "name": "Deletions",
                                "marker": {"color": "rgb(255, 99, 132)"}
                            }
                        ],
                        "layout": {
                            "title": "Code Changes Over Time",
                            "xaxis": {"title": "Week", "tickangle": 45},
                            "yaxis": {"title": "Lines of Code"},
                            "barmode": "group",
                            "margin": {"l": 60, "r": 40, "t": 80, "b": 120},
                            "height": 400,
                            "width": 700
                        }
                    }
                    
                    # Create code frequency visualization with simple format
                    code_frequency_file = "code_frequency.json"
                    
                    with mkdocs_gen_files.open(f"assets/{code_frequency_file}", "w") as f:
                        f.write(json.dumps(code_frequency_data, indent=2))
                    
                    # Add code frequency visualization to stats page with direct HTML
                    code_frequency_content = """## Code Changes

This chart shows code additions (green) and deletions (red) over time.

<div id="code-changes-chart" style="height:400px; width:100%;"></div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Plotly !== 'undefined') {
        fetch('../../assets/code_frequency.json')
            .then(response => response.json())
            .then(data => {
                Plotly.newPlot('code-changes-chart', data.data, data.layout);
            })
            .catch(error => console.error('Error loading chart data:', error));
    } else {
        console.error('Plotly is not loaded');
    }
});
</script>
"""
                    
                    # Append to the auxillary file
                    with mkdocs_gen_files.open("auxillary/stats.md", "a") as f:
                        f.write(code_frequency_content)
                    
                    print("✅ Added code frequency visualization", file=sys.stderr)
                else:
                    print("⚠️ No usable code frequency data found", file=sys.stderr)
            else:
                print("⚠️ No code frequency data available", file=sys.stderr)
                
        except Exception as e:
            print(f"⚠️ Error generating time series visualizations: {e}", file=sys.stderr)
        
        print(f"✅ Repository statistics generated successfully!")
        print(f"📊 Found {len(contributors)} contributors")
        print(f"👁️  {total_views:,} views, {unique_visitors:,} unique visitors")
        print(f"📁 {len(popular_paths)} popular files tracked")
        print(f"🔗 {len(referrers)} traffic sources")

# Main execution
print("Running repository statistics extraction...")
generator = StatsGenerator()
generator.generate_stats_page()

