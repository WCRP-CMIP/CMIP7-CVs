"""
Label management functions for GitHub
"""

import json
from .utils import GitHubUtils

class LabelManager:
    """Manages GitHub repository labels"""
    
    def __init__(self):
        self.utils = GitHubUtils()
    
    def check_label_exists(self, repo_owner, repo_name, label_name):
        """Check if a label exists in the repository"""
        print(f"\n🏷️ Checking if label '{label_name}' exists...")
        
        try:
            result = self.utils.run_gh_cmd(["api", f"/repos/{repo_owner}/{repo_name}/labels/{label_name}"])
            label_data = json.loads(result)
            print(f"✅ Label '{label_name}' exists")
            return True, label_data
        except RuntimeError as e:
            if "404" in str(e) or "Not Found" in str(e):
                print(f"ℹ️ Label '{label_name}' does not exist")
                return False, None
            else:
                print(f"❌ Error checking label: {e}")
                return False, None

    def create_label(self, repo_owner, repo_name, name, description="", color="FFFFFF"):
        """Create a new label in the repository"""
        print(f"\n➕ Creating label '{name}'...")
        
        label_data = {
            "name": name,
            "description": description,
            "color": color
        }
        
        try:
            result = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/labels",
                "--method", "POST",
                "--input", "-"
            ], input_data=json.dumps(label_data))
            
            created_label = json.loads(result)
            print(f"✅ Label '{name}' created successfully")
            return created_label
        except Exception as e:
            print(f"❌ Error creating label '{name}': {e}")
            return None

    def update_label(self, repo_owner, repo_name, old_name, new_name=None, description=None, color=None):
        """Update an existing label"""
        print(f"\n📝 Updating label '{old_name}'...")
        
        label_data = {}
        if new_name:
            label_data["name"] = new_name
        if description is not None:
            label_data["description"] = description
        if color:
            label_data["color"] = color
        
        try:
            result = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/labels/{old_name}",
                "--method", "PATCH",
                "--input", "-"
            ], input_data=json.dumps(label_data))
            
            updated_label = json.loads(result)
            print(f"✅ Label updated successfully")
            return updated_label
        except Exception as e:
            print(f"❌ Error updating label: {e}")
            return None

    def delete_label(self, repo_owner, repo_name, label_name):
        """Delete a label from the repository"""
        print(f"\n🗑️ Deleting label '{label_name}'...")
        
        try:
            self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/labels/{label_name}",
                "--method", "DELETE"
            ])
            print(f"✅ Label '{label_name}' deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting label: {e}")
            return False

    def list_labels(self, repo_owner, repo_name):
        """List all labels in the repository"""
        print(f"\n📋 Listing labels...")
        try:
            result = self.utils.run_gh_cmd([
                "api", f"/repos/{repo_owner}/{repo_name}/labels"
            ])
            labels = json.loads(result)
            print(f"✅ Found {len(labels)} labels")
            return labels
        except Exception as e:
            print(f"❌ Error listing labels: {e}")
            return []

    def assign_labels_to_issue(self, issue_url, label_names):
        """Assign labels to an issue"""
        print(f"\n🏷️ Assigning labels to issue: {', '.join(label_names)}...")
        
        try:
            cmd = ["issue", "edit", issue_url]
            for label in label_names:
                cmd.extend(["--add-label", label])
            
            self.utils.run_gh_cmd(cmd)
            print(f"✅ Labels assigned successfully: {', '.join(label_names)}")
            return True
        except Exception as e:
            print(f"❌ Error assigning labels: {e}")
            return False

    def remove_labels_from_issue(self, issue_url, label_names):
        """Remove labels from an issue"""
        print(f"\n🏷️ Removing labels from issue: {', '.join(label_names)}...")
        
        try:
            cmd = ["issue", "edit", issue_url]
            for label in label_names:
                cmd.extend(["--remove-label", label])
            
            self.utils.run_gh_cmd(cmd)
            print(f"✅ Labels removed successfully: {', '.join(label_names)}")
            return True
        except Exception as e:
            print(f"❌ Error removing labels: {e}")
            return False

    def ensure_labels_exist(self, repo_owner, repo_name, labels_config):
        """Ensure labels exist, create if they don't"""
        print(f"\n🏷️ Ensuring labels exist...")
        
        created_labels = []
        existing_labels = []
        
        for label_info in labels_config:
            name = label_info["name"]
            exists, _ = self.check_label_exists(repo_owner, repo_name, name)
            
            if not exists:
                created_label = self.create_label(
                    repo_owner, repo_name, 
                    name, 
                    label_info.get("description", ""),
                    label_info.get("color", "FFFFFF")
                )
                if created_label:
                    created_labels.append(name)
            else:
                existing_labels.append(name)
        
        print(f"✅ Labels management completed")
        print(f"   Created: {len(created_labels)} labels")
        print(f"   Existing: {len(existing_labels)} labels")
        
        return created_labels, existing_labels
