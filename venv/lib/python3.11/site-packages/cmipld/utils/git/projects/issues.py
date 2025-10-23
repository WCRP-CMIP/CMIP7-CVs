"""
Issue management functions for GitHub
"""

import json
from .utils import GitHubUtils

class IssueManager:
    """Manages GitHub issues"""
    
    def __init__(self):
        self.utils = GitHubUtils()
    
    def get_issue_info(self, issue_url):
        """Get issue information including ID"""
        print(f"\n🔍 Getting issue information from: {issue_url}")
        try:
            result = self.utils.run_gh_cmd(["issue", "view", issue_url, "--json", "id,number,title,body,state"])
            issue_data = json.loads(result)
            print(f"✅ Issue retrieved: #{issue_data['number']} - {issue_data['title']}")
            return issue_data
        except Exception as e:
            print(f"❌ Error getting issue info: {e}")
            return None
    
    def create_issue(self, repo_owner, repo_name, title, body="", labels=None, milestone=None, assignees=None, check_duplicates=True):
        """Create a new issue (checks for duplicates by title)"""
        print(f"\n➕ Creating issue: {title}")
        
        # Check for existing issue with same title
        if check_duplicates:
            existing_issues = self.list_issues(repo_owner, repo_name, "open", 100)
            for issue in existing_issues:
                if issue.get("title", "").lower() == title.lower():
                    print(f"⚠️ Issue with title '{title}' already exists: #{issue['number']}")
                    continue_anyway = input("Continue creating duplicate? (y/n): ").lower()
                    if continue_anyway != 'y':
                        print("❌ Issue creation cancelled")
                        return None
                    break
        
        cmd = [
            "issue", "create",
            "--repo", f"{repo_owner}/{repo_name}",
            "--title", title,
            "--body", body or "No description provided."
        ]
        
        if labels:
            for label in labels:
                cmd.extend(["--label", label])
        
        if milestone:
            cmd.extend(["--milestone", milestone])
        
        if assignees:
            for assignee in assignees:
                cmd.extend(["--assignee", assignee])
        
        try:
            result = self.utils.run_gh_cmd(cmd)
            print(f"✅ Issue created successfully")
            return result
        except Exception as e:
            print(f"❌ Error creating issue: {e}")
            return None

    def create_issue_safe(self, repo_owner, repo_name, title, body="", labels=None, milestone=None, assignees=None):
        """Create issue without duplicate check (for automated workflows)"""
        return self.create_issue(repo_owner, repo_name, title, body, labels, milestone, assignees, check_duplicates=False)
    
    def update_issue(self, issue_url, title=None, body=None, state=None):
        """Update an existing issue"""
        print(f"\n📝 Updating issue: {issue_url}")
        
        cmd = ["issue", "edit", issue_url]
        
        if title:
            cmd.extend(["--title", title])
        if body:
            cmd.extend(["--body", body])
        if state:
            cmd.extend(["--state", state])
        
        try:
            self.utils.run_gh_cmd(cmd)
            print(f"✅ Issue updated successfully")
            return True
        except Exception as e:
            print(f"❌ Error updating issue: {e}")
            return False
    
    def close_issue(self, issue_url):
        """Close an issue"""
        return self.update_issue(issue_url, state="closed")
    
    def reopen_issue(self, issue_url):
        """Reopen an issue"""
        return self.update_issue(issue_url, state="open")
    
    def delete_issue(self, repo_owner, repo_name, issue_number):
        """Delete an issue (requires admin permissions)"""
        print(f"\n🗑️ Deleting issue #{issue_number}...")
        try:
            self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/issues/{issue_number}",
                "--method", "DELETE"
            ])
            print(f"✅ Issue #{issue_number} deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting issue: {e}")
            return False
    
    def add_comment(self, issue_url, comment):
        """Add a comment to an issue"""
        print(f"\n💬 Adding comment to issue")
        try:
            self.utils.run_gh_cmd([
                "issue", "comment", issue_url,
                "--body", comment
            ])
            print(f"✅ Comment added successfully")
            return True
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return False
    
    def assign_issue(self, issue_url, assignees):
        """Assign users to an issue"""
        print(f"\n👤 Assigning issue to: {', '.join(assignees)}")
        
        cmd = ["issue", "edit", issue_url]
        for assignee in assignees:
            cmd.extend(["--add-assignee", assignee])
        
        try:
            self.utils.run_gh_cmd(cmd)
            print(f"✅ Issue assigned successfully")
            return True
        except Exception as e:
            print(f"❌ Error assigning issue: {e}")
            return False
    
    def unassign_issue(self, issue_url, assignees):
        """Unassign users from an issue"""
        print(f"\n👤 Unassigning issue from: {', '.join(assignees)}")
        
        cmd = ["issue", "edit", issue_url]
        for assignee in assignees:
            cmd.extend(["--remove-assignee", assignee])
        
        try:
            self.utils.run_gh_cmd(cmd)
            print(f"✅ Issue unassigned successfully")
            return True
        except Exception as e:
            print(f"❌ Error unassigning issue: {e}")
            return False
    
    def list_issues(self, repo_owner, repo_name, state="open", limit=30):
        """List issues in a repository"""
        print(f"\n📋 Listing {state} issues...")
        try:
            result = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/issues",
                "-F", f"state={state}",
                "-F", f"per_page={limit}"
            ])
            issues = json.loads(result)
            print(f"✅ Found {len(issues)} issues")
            return issues
        except Exception as e:
            print(f"❌ Error listing issues: {e}")
            return []

    def list_all_issues(self, repo_owner, repo_name, limit=50):
        """List all issues with detailed information"""
        print(f"\n📋 All Issues for {repo_owner}/{repo_name}")
        print("=" * 50)
        
        try:
            # Get both open and closed issues
            open_issues = self.list_issues(repo_owner, repo_name, "open", limit)
            closed_issues = self.list_issues(repo_owner, repo_name, "closed", limit//2)
            
            all_issues = open_issues + closed_issues
            
            if not all_issues:
                print("No issues found")
                return []
            
            print(f"📊 Summary: {len(open_issues)} open, {len(closed_issues)} closed")
            print(f"\n📋 Issue List:")
            
            for issue in all_issues[:limit]:
                labels = [l["name"] for l in issue.get("labels", [])]
                milestone = issue.get("milestone", {}).get("title", "No milestone") if issue.get("milestone") else "No milestone"
                assignees = [a["login"] for a in issue.get("assignees", [])]
                state_emoji = "✅" if issue["state"] == "open" else "❌"
                
                print(f"  {state_emoji} #{issue['number']}: {issue['title']}")
                print(f"     State: {issue['state']}")
                print(f"     Labels: {', '.join(labels) if labels else 'None'}")
                print(f"     Milestone: {milestone}")
                print(f"     Assignees: {', '.join(assignees) if assignees else 'Unassigned'}")
                print()
            
            if len(all_issues) > limit:
                print(f"... and {len(all_issues) - limit} more issues")
            
            return all_issues
            
        except Exception as e:
            print(f"❌ Error listing all issues: {e}")
            return []

    def all_issues_dashboard(self, repo_owner, repo_name):
        """Show comprehensive dashboard of all issues"""
        print(f"\n📊 All Issues Dashboard for {repo_owner}/{repo_name}")
        print("=" * 60)
        
        try:
            # Get open and closed issues
            open_issues = self.list_issues(repo_owner, repo_name, "open", 100)
            closed_issues = self.list_issues(repo_owner, repo_name, "closed", 50)
            all_issues = open_issues + closed_issues
            
            print(f"📊 Summary: {len(open_issues)} open, {len(closed_issues)} closed, {len(all_issues)} total")
            
            if all_issues:
                # Label statistics
                label_stats = {}
                for issue in all_issues:
                    for label in issue.get("labels", []):
                        name = label.get("name")
                        if name:
                            label_stats[name] = label_stats.get(name, 0) + 1
                
                if label_stats:
                    print(f"\n🏷️ Top Labels:")
                    sorted_labels = sorted(label_stats.items(), key=lambda x: x[1], reverse=True)
                    for label, count in sorted_labels[:5]:
                        print(f"   • {label}: {count} issues")
                
                # Milestone statistics
                milestone_stats = {}
                no_milestone = 0
                for issue in all_issues:
                    milestone = issue.get("milestone")
                    if milestone:
                        title = milestone.get("title")
                        if title:
                            milestone_stats[title] = milestone_stats.get(title, 0) + 1
                    else:
                        no_milestone += 1
                
                print(f"\n🎯 Milestones:")
                for milestone, count in milestone_stats.items():
                    print(f"   • {milestone}: {count} issues")
                if no_milestone > 0:
                    print(f"   • No milestone: {no_milestone} issues")
                
                # Recent open issues
                print(f"\n📋 Recent Open Issues:")
                for i, issue in enumerate(open_issues[:5], 1):
                    labels = [l["name"] for l in issue.get("labels", [])]
                    milestone = issue.get("milestone", {}).get("title", "No milestone") if issue.get("milestone") else "No milestone"
                    assignees = [a["login"] for a in issue.get("assignees", [])]
                    
                    print(f"   {i}. #{issue['number']}: {issue['title']}")
                    print(f"      Labels: {', '.join(labels) if labels else 'None'}")
                    print(f"      Milestone: {milestone}")
                    print(f"      Assignees: {', '.join(assignees) if assignees else 'Unassigned'}")
                    print()
            
            return {
                "open": len(open_issues),
                "closed": len(closed_issues),
                "total": len(all_issues),
                "label_stats": label_stats if 'label_stats' in locals() else {},
                "milestone_stats": milestone_stats if 'milestone_stats' in locals() else {}
            }
            
        except Exception as e:
            print(f"❌ Error generating issues dashboard: {e}")
            return {}

    def create_issues_bulk(self, repo_owner, repo_name, issues_data, add_to_project_id=None):
        """Create multiple issues from structured data with optional project integration"""
        print(f"\n🚀 Bulk creating {len(issues_data)} issues...")
        
        created_issues = []
        failed_issues = []
        
        for i, issue_data in enumerate(issues_data, 1):
            print(f"\n[{i}/{len(issues_data)}] Processing: {issue_data.get('title', 'Untitled')}")
            
            try:
                # Extract issue data
                title = issue_data.get('title', f'Issue {i}')
                body = issue_data.get('body', issue_data.get('content', 'No description'))
                labels = issue_data.get('labels', [])
                milestone = issue_data.get('milestone')
                assignees = issue_data.get('assignees', [])
                start_date = issue_data.get('start_date')
                end_date = issue_data.get('end_date')
                
                # Create issue (without duplicate check for bulk operations)
                issue_url = self.create_issue_safe(
                    repo_owner, repo_name, title, body, labels, milestone, assignees
                )
                
                if issue_url:
                    issue_info = self.get_issue_info(issue_url)
                    
                    # Add to project if specified
                    if add_to_project_id and issue_info:
                        try:
                            # Import here to avoid circular imports
                            from .projects import ProjectManager
                            project_mgr = ProjectManager()
                            
                            if start_date or end_date:
                                project_mgr.add_issue_to_project_with_dates(
                                    add_to_project_id, issue_info["id"], start_date, end_date
                                )
                            else:
                                project_mgr.add_issue_to_project(add_to_project_id, issue_info["id"])
                        except Exception as e:
                            print(f"⚠️ Failed to add to project: {e}")
                    
                    created_issues.append({
                        'title': title,
                        'url': issue_url,
                        'issue_info': issue_info
                    })
                    print(f"✅ Created successfully")
                else:
                    failed_issues.append(title)
                    print(f"❌ Failed to create")
                    
            except Exception as e:
                failed_issues.append(issue_data.get('title', f'Issue {i}'))
                print(f"❌ Error: {e}")
        
        print(f"\n🎉 Bulk creation completed:")
        print(f"   ✅ Created: {len(created_issues)} issues")
        print(f"   ❌ Failed: {len(failed_issues)} issues")
        
        if failed_issues:
            print(f"   Failed issues: {', '.join(failed_issues)}")
        
        return created_issues, failed_issues
