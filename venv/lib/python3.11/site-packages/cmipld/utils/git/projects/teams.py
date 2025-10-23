"""
Team management functions for GitHub
"""

import json
from .utils import GitHubUtils

class TeamManager:
    """Manages GitHub organization teams"""
    
    def __init__(self):
        self.utils = GitHubUtils()
    
    def check_team_exists(self, org_name, team_name):
        """Check if a team exists in the organization"""
        print(f"\n👥 Checking if team '{team_name}' exists in org '{org_name}'...")
        
        try:
            result = self.utils.run_gh_cmd(["api", f"/orgs/{org_name}/teams/{team_name}"])
            team_data = json.loads(result)
            print(f"✅ Team '{team_name}' exists with ID: {team_data.get('id')}")
            return True, team_data
        except RuntimeError as e:
            if "404" in str(e) or "Not Found" in str(e):
                print(f"ℹ️ Team '{team_name}' does not exist")
                return False, None
            else:
                print(f"❌ Error checking team: {e}")
                return False, None

    def create_team(self, org_name, team_name, description="", privacy="closed", parent_team_id=None):
        """Create a new team in the organization"""
        print(f"\n➕ Creating team '{team_name}'...")
        
        team_data = {
            "name": team_name,
            "description": description,
            "privacy": privacy
        }
        
        if parent_team_id:
            team_data["parent_team_id"] = parent_team_id
        
        try:
            result = self.utils.run_gh_cmd([
                "api", f"/orgs/{org_name}/teams",
                "--method", "POST",
                "--input", "-"
            ], input_data=json.dumps(team_data))
            
            created_team = json.loads(result)
            print(f"✅ Team '{team_name}' created successfully with ID: {created_team.get('id')}")
            return created_team
        except Exception as e:
            print(f"❌ Error creating team '{team_name}': {e}")
            return None

    def delete_team(self, org_name, team_name):
        """Delete a team from the organization"""
        print(f"\n🗑️ Deleting team '{team_name}'...")
        
        try:
            self.utils.run_gh_cmd([
                "api", f"/orgs/{org_name}/teams/{team_name}",
                "--method", "DELETE"
            ])
            print(f"✅ Team '{team_name}' deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting team: {e}")
            return False

    def list_teams(self, org_name):
        """List all teams in the organization"""
        print(f"\n📋 Listing teams in org '{org_name}'...")
        try:
            result = self.utils.run_gh_cmd(["api", f"/orgs/{org_name}/teams"])
            teams = json.loads(result)
            print(f"✅ Found {len(teams)} teams")
            return teams
        except Exception as e:
            print(f"❌ Error listing teams: {e}")
            return []

    def get_child_teams(self, org_name, parent_team_name):
        """Get child teams of a parent team"""
        print(f"\n👥 Getting child teams of '{parent_team_name}'...")
        
        try:
            result = self.utils.run_gh_cmd(["api", f"/orgs/{org_name}/teams/{parent_team_name}/teams"])
            child_teams = json.loads(result)
            print(f"✅ Found {len(child_teams)} child teams")
            return child_teams
        except Exception as e:
            print(f"❌ Error getting child teams: {e}")
            return []

    def create_child_team(self, org_name, parent_team_name, child_team_name, description=None):
        """Create a child team under a parent team"""
        print(f"\n➕ Creating child team '{child_team_name}' under '{parent_team_name}'...")
        
        # Get parent team ID
        try:
            parent_result = self.utils.run_gh_cmd(["api", f"/orgs/{org_name}/teams/{parent_team_name}"])
            parent_data = json.loads(parent_result)
            parent_id = parent_data['id']
        except Exception as e:
            print(f"❌ Error getting parent team ID: {e}")
            return None
        
        description = description or f"Child team {child_team_name} for project management"
        return self.create_team(org_name, child_team_name, description, "closed", parent_id)

    def add_member_to_team(self, org_name, team_name, username, role="member"):
        """Add a member to a team"""
        print(f"\n👤 Adding {username} to team '{team_name}' as {role}...")
        
        try:
            self.utils.run_gh_cmd([
                "api", f"/orgs/{org_name}/teams/{team_name}/memberships/{username}",
                "--method", "PUT",
                "--field", f"role={role}"
            ])
            print(f"✅ {username} added to team successfully")
            return True
        except Exception as e:
            print(f"❌ Error adding member to team: {e}")
            return False

    def remove_member_from_team(self, org_name, team_name, username):
        """Remove a member from a team"""
        print(f"\n👤 Removing {username} from team '{team_name}'...")
        
        try:
            self.utils.run_gh_cmd([
                "api", f"/orgs/{org_name}/teams/{team_name}/memberships/{username}",
                "--method", "DELETE"
            ])
            print(f"✅ {username} removed from team successfully")
            return True
        except Exception as e:
            print(f"❌ Error removing member from team: {e}")
            return False

    def list_team_members(self, org_name, team_name):
        """List members of a team"""
        print(f"\n👥 Listing members of team '{team_name}'...")
        try:
            result = self.utils.run_gh_cmd(["api", f"/orgs/{org_name}/teams/{team_name}/members"])
            members = json.loads(result)
            print(f"✅ Found {len(members)} team members")
            return members
        except Exception as e:
            print(f"❌ Error listing team members: {e}")
            return []

    def assign_issue_to_team(self, issue_url, org_name, team_name):
        """Assign an issue to a team by adding comment and assigning to team member"""
        print(f"\n👥 Assigning issue to team '{team_name}'...")
        
        try:
            # Get team members
            members = self.list_team_members(org_name, team_name)
            
            comment = f"Assigned to team @{org_name}/{team_name}"
            
            if members:
                # Assign to first team member as representative
                first_member = members[0]['login']
                print(f"📝 Assigning to team member: {first_member}")
                
                try:
                    self.utils.run_gh_cmd([
                        "issue", "edit", issue_url,
                        "--add-assignee", first_member
                    ])
                    comment = f"Assigned to team @{org_name}/{team_name} (represented by @{first_member})"
                except Exception as e:
                    print(f"⚠️ Could not assign to user: {e}")
            else:
                print(f"⚠️ Team '{team_name}' has no members")
            
            # Add comment
            try:
                self.utils.run_gh_cmd([
                    "issue", "comment", issue_url,
                    "--body", comment
                ])
                print(f"✅ Team assignment comment added")
                return True
            except Exception as e:
                print(f"❌ Could not add comment: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error assigning issue to team: {e}")
            return False
