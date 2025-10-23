"""
Milestone management functions for GitHub
"""

import json
from .utils import GitHubUtils

class MilestoneManager:
    """Manages GitHub repository milestones"""
    
    def __init__(self):
        self.utils = GitHubUtils()
    
    def check_milestone_exists(self, repo_owner, repo_name, milestone_title):
        """Check if a milestone exists in the repository"""
        print(f"\n💯 Checking if milestone '{milestone_title}' exists...")
        
        try:
            result = self.utils.run_gh_cmd(["api", f"/repos/{repo_owner}/{repo_name}/milestones"])
            milestones = json.loads(result)
            
            for milestone in milestones:
                if milestone["title"] == milestone_title:
                    print(f"✅ Milestone '{milestone_title}' exists with number: {milestone['number']}")
                    return True, milestone
            
            print(f"ℹ️ Milestone '{milestone_title}' does not exist")
            return False, None
            
        except RuntimeError as e:
            print(f"❌ Error checking milestones: {e}")
            return False, None

    def create_milestone(self, repo_owner, repo_name, title, description="", due_date=None, state="open"):
        """Create a new milestone in the repository"""
        print(f"\n➕ Creating milestone '{title}'...")
        
        milestone_data = {
            "title": title,
            "description": description,
            "state": state
        }
        
        if due_date:
            milestone_data["due_on"] = due_date
        
        try:
            result = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/milestones",
                "--method", "POST",
                "--input", "-"
            ], input_data=json.dumps(milestone_data))
            
            created_milestone = json.loads(result)
            print(f"✅ Milestone '{title}' created successfully with number: {created_milestone['number']}")
            return created_milestone
        except Exception as e:
            print(f"❌ Error creating milestone '{title}': {e}")
            return None

    def update_milestone(self, repo_owner, repo_name, milestone_number, title=None, description=None, due_date=None, state=None):
        """Update an existing milestone"""
        print(f"\n📝 Updating milestone #{milestone_number}...")
        
        milestone_data = {}
        if title:
            milestone_data["title"] = title
        if description is not None:
            milestone_data["description"] = description
        if due_date:
            milestone_data["due_on"] = due_date
        if state:
            milestone_data["state"] = state
        
        try:
            result = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/milestones/{milestone_number}",
                "--method", "PATCH",
                "--input", "-"
            ], input_data=json.dumps(milestone_data))
            
            updated_milestone = json.loads(result)
            print(f"✅ Milestone updated successfully")
            return updated_milestone
        except Exception as e:
            print(f"❌ Error updating milestone: {e}")
            return None

    def delete_milestone(self, repo_owner, repo_name, milestone_number):
        """Delete a milestone from the repository"""
        print(f"\n🗑️ Deleting milestone #{milestone_number}...")
        
        try:
            self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/milestones/{milestone_number}",
                "--method", "DELETE"
            ])
            print(f"✅ Milestone #{milestone_number} deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting milestone: {e}")
            return False

    def list_milestones(self, repo_owner, repo_name, state="open"):
        """List milestones in the repository"""
        print(f"\n📋 Listing {state} milestones...")
        try:
            result = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/milestones",
                "-F", f"state={state}"
            ])
            milestones = json.loads(result)
            print(f"✅ Found {len(milestones)} milestones")
            return milestones
        except Exception as e:
            print(f"❌ Error listing milestones: {e}")
            return []

    def list_all_milestones(self, repo_owner, repo_name):
        """List all milestones with detailed information"""
        print(f"\n📊 All Milestones Dashboard for {repo_owner}/{repo_name}")
        print("=" * 50)
        
        try:
            # Get open and closed milestones
            result_open = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/milestones",
                "-F", "state=open"
            ])
            result_closed = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/milestones", 
                "-F", "state=closed"
            ])
            
            open_milestones = json.loads(result_open)
            closed_milestones = json.loads(result_closed)
            all_milestones = open_milestones + closed_milestones
            
            print(f"📊 Summary: {len(open_milestones)} open, {len(closed_milestones)} closed, {len(all_milestones)} total")
            
            if all_milestones:
                print(f"\n📋 Milestone Details:")
                for milestone in all_milestones:
                    title = milestone.get('title', 'No title')
                    state = milestone.get('state', 'unknown')
                    due_on = milestone.get('due_on', 'No due date')
                    if due_on != 'No due date':
                        due_on = due_on.split('T')[0]  # Just date part
                    open_issues = milestone.get('open_issues', 0)
                    closed_issues = milestone.get('closed_issues', 0)
                    total_issues = open_issues + closed_issues
                    
                    progress = ""
                    if total_issues > 0:
                        percent = int((closed_issues / total_issues) * 100)
                        progress = f" ({percent}% complete)"
                    
                    print(f"   • {title} [{state}]")
                    print(f"     Due: {due_on}")
                    print(f"     Issues: {open_issues} open, {closed_issues} closed{progress}")
                    print()
            
            return all_milestones
        except Exception as e:
            print(f"❌ Error listing all milestones: {e}")
            return []

    def assign_milestone_to_issue(self, issue_url, milestone_title):
        """Assign a milestone to an issue"""
        print(f"\n🎯 Assigning milestone '{milestone_title}' to issue...")
        
        try:
            self.utils.run_gh_cmd([
                "issue", "edit", issue_url,
                "--milestone", milestone_title
            ])
            print(f"✅ Milestone '{milestone_title}' assigned successfully")
            return True
        except Exception as e:
            print(f"❌ Error assigning milestone: {e}")
            return False

    def remove_milestone_from_issue(self, issue_url):
        """Remove milestone from an issue"""
        print(f"\n🎯 Removing milestone from issue...")
        
        try:
            self.utils.run_gh_cmd([
                "issue", "edit", issue_url,
                "--milestone", ""
            ])
            print(f"✅ Milestone removed successfully")
            return True
        except Exception as e:
            print(f"❌ Error removing milestone: {e}")
            return False

    def close_milestone(self, repo_owner, repo_name, milestone_number):
        """Close a milestone"""
        return self.update_milestone(repo_owner, repo_name, milestone_number, state="closed")

    def reopen_milestone(self, repo_owner, repo_name, milestone_number):
        """Reopen a milestone"""
        return self.update_milestone(repo_owner, repo_name, milestone_number, state="open")

    def ensure_milestone_exists(self, repo_owner, repo_name, milestone_config):
        """Ensure milestone exists, create if it doesn't"""
        print(f"\n🎯 Ensuring milestone exists...")
        
        title = milestone_config["title"]
        exists, milestone_data = self.check_milestone_exists(repo_owner, repo_name, title)
        
        if not exists:
            milestone_data = self.create_milestone(
                repo_owner, repo_name,
                title,
                milestone_config.get("description", ""),
                milestone_config.get("due_date"),
                milestone_config.get("state", "open")
            )
        
        return milestone_data
