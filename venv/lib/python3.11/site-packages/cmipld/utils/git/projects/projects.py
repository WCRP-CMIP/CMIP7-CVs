"""
Project management functions for GitHub Projects v2
"""

import json
import time
from .utils import GitHubUtils

class ProjectManager:
    """Manages GitHub Projects (v2)"""
    
    def __init__(self):
        self.utils = GitHubUtils()
    
    def get_project_fields(self, project_id):
        """Get project fields using GraphQL"""
        print(f"\n🔍 Getting project fields...")
        
        fields_query = '''
        query ($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  __typename
                  ... on ProjectV2FieldCommon {
                    id
                    name
                    dataType
                  }
                }
              }
            }
          }
        }
        '''
        
        try:
            result = self.utils.run_gh_cmd([
                "api", "graphql",
                "-f", f"query={fields_query}",
                "-F", f"projectId={project_id}"
            ])
            
            data = json.loads(result)
            if "errors" in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return {}
            
            fields = {}
            for field in data["data"]["node"]["fields"]["nodes"]:
                if "name" in field and "id" in field:
                    fields[field["name"]] = field["id"]
                    print(f"  - {field['name']}: {field['id']}")
            
            return fields
        except Exception as e:
            print(f"❌ Error getting project fields: {e}")
            return {}

    def find_issue_in_project(self, project_id, issue_id):
        """Find if an issue is already in the project"""
        print(f"\n🔍 Searching for issue in project...")
        
        items_query = '''
        query ($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      id
                      number
                      title
                    }
                  }
                }
              }
            }
          }
        }
        '''
        
        try:
            result = self.utils.run_gh_cmd([
                "api", "graphql",
                "-f", f"query={items_query}",
                "-F", f"projectId={project_id}"
            ])
            
            data = json.loads(result)
            if "errors" in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return None
                
            items = data["data"]["node"]["items"]["nodes"]
            print(f"Found {len(items)} items in project")
            
            for item in items:
                content = item.get("content")
                if content and content.get("id") == issue_id:
                    print(f"✅ Issue found in project! Item ID: {item['id']}")
                    return item["id"]
            
            print("ℹ️ Issue not found in project")
            return None
        except Exception as e:
            print(f"❌ Error searching for issue: {e}")
            return None

    def add_issue_to_project(self, project_id, issue_id):
        """Add issue to project using GraphQL API"""
        print(f"\n➕ Adding issue to project...")
        
        mutation = '''
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item {
              id
            }
          }
        }
        '''
        
        try:
            result = self.utils.run_gh_cmd([
                "api", "graphql",
                "-f", f"query={mutation}",
                "-F", f"projectId={project_id}",
                "-F", f"contentId={issue_id}"
            ])
            
            data = json.loads(result)
            if "errors" in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            print("✅ Issue added to project")
            time.sleep(2)  # Wait for processing
            return True
        except Exception as e:
            print(f"❌ Error adding issue to project: {e}")
            return False

    def remove_issue_from_project(self, project_id, item_id):
        """Remove issue from project using GraphQL API"""
        print(f"\n🗑️ Removing issue from project...")
        
        mutation = '''
        mutation($projectId: ID!, $itemId: ID!) {
          deleteProjectV2Item(input: {projectId: $projectId, itemId: $itemId}) {
            deletedItemId
          }
        }
        '''
        
        try:
            result = self.utils.run_gh_cmd([
                "api", "graphql",
                "-f", f"query={mutation}",
                "-F", f"projectId={project_id}",
                "-F", f"itemId={item_id}"
            ])
            
            data = json.loads(result)
            if "errors" in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            print("✅ Issue removed from project")
            return True
        except Exception as e:
            print(f"❌ Error removing issue from project: {e}")
            return False

    def update_project_field(self, project_id, item_id, field_id, field_name, value, field_type="text"):
        """Update a project field using GraphQL API"""
        print(f"📝 Updating '{field_name}' to '{value}'")
        
        if field_type == "date":
            mutation = '''
            mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: Date!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $projectId
                itemId: $itemId
                fieldId: $fieldId
                value: { date: $value }
              }) {
                projectV2Item {
                  id
                }
              }
            }
            '''
        else:
            mutation = '''
            mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $projectId
                itemId: $itemId
                fieldId: $fieldId
                value: { text: $value }
              }) {
                projectV2Item {
                  id
                }
              }
            }
            '''
        
        try:
            result = self.utils.run_gh_cmd([
                "api", "graphql",
                "-f", f"query={mutation}",
                "-F", f"projectId={project_id}",
                "-F", f"itemId={item_id}",
                "-F", f"fieldId={field_id}",
                "-F", f"value={value}"
            ])
            
            data = json.loads(result)
            if "errors" in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            print(f"✅ '{field_name}' updated successfully")
            return True
        except Exception as e:
            print(f"❌ Error updating '{field_name}': {e}")
            return False

    def update_multiple_fields(self, project_id, item_id, field_updates):
        """Update multiple project fields"""
        print(f"\n📝 Updating multiple project fields...")
        
        success_count = 0
        for field_name, field_data in field_updates.items():
            field_id = field_data.get("id")
            value = field_data.get("value")
            field_type = field_data.get("type", "text")
            
            if self.update_project_field(project_id, item_id, field_id, field_name, value, field_type):
                success_count += 1
        
        print(f"✅ Updated {success_count}/{len(field_updates)} fields successfully")
        return success_count == len(field_updates)

    def add_issue_to_project_with_dates(self, project_id, issue_id, start_date=None, end_date=None):
        """Add issue to project and set start/end dates"""
        print(f"\n➕ Adding issue to project with dates...")
        
        try:
            # First add the issue to project
            success = self.add_issue_to_project(project_id, issue_id)
            if not success:
                return False
            
            # Find the item in the project
            item_id = self.find_issue_in_project(project_id, issue_id)
            if not item_id:
                print("❌ Could not find issue in project after adding")
                return False
            
            # Get project fields
            fields = self.get_project_fields(project_id)
            if not fields:
                print("⚠️ No project fields found")
                return True  # Issue was added, just couldn't set dates
            
            # Update date fields if they exist and dates are provided
            field_updates = {}
            
            if start_date and "Start date" in fields:
                field_updates["Start date"] = {
                    "id": fields["Start date"],
                    "value": start_date,
                    "type": "date"
                }
            
            if end_date and "End date" in fields:
                field_updates["End date"] = {
                    "id": fields["End date"], 
                    "value": end_date,
                    "type": "date"
                }
            
            # Try alternative field names if standard ones don't exist
            if start_date and not field_updates.get("Start date"):
                for field_name in ["Start", "Started", "Begin", "From"]:
                    if field_name in fields:
                        field_updates[field_name] = {
                            "id": fields[field_name],
                            "value": start_date,
                            "type": "date"
                        }
                        break
            
            if end_date and not field_updates.get("End date"):
                for field_name in ["End", "Due", "Finish", "To", "Target"]:
                    if field_name in fields:
                        field_updates[field_name] = {
                            "id": fields[field_name],
                            "value": end_date,
                            "type": "date"
                        }
                        break
            
            # Apply date updates
            if field_updates:
                success = self.update_multiple_fields(project_id, item_id, field_updates)
                if success:
                    print(f"✅ Issue added to project with dates: {start_date} to {end_date}")
                else:
                    print(f"✅ Issue added to project (dates update failed)")
            else:
                print(f"✅ Issue added to project (no compatible date fields found)")
                if fields:
                    print(f"   Available fields: {', '.join(fields.keys())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding issue with dates: {e}")
            return False

    def get_project_items(self, project_id, limit=50):
        """Get all items in a project"""
        print(f"\n📋 Getting project items...")
        
        items_query = f'''
        query ($projectId: ID!) {{
          node(id: $projectId) {{
            ... on ProjectV2 {{
              items(first: {limit}) {{
                nodes {{
                  id
                  content {{
                    ... on Issue {{
                      id
                      number
                      title
                      state
                    }}
                    ... on PullRequest {{
                      id
                      number
                      title
                      state
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        '''
        
        try:
            result = self.utils.run_gh_cmd([
                "api", "graphql",
                "-f", f"query={items_query}",
                "-F", f"projectId={project_id}"
            ])
            
            data = json.loads(result)
            if "errors" in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return []
            
            items = data["data"]["node"]["items"]["nodes"]
            print(f"✅ Found {len(items)} items in project")
            return items
        except Exception as e:
            print(f"❌ Error getting project items: {e}")
            return []

    def list_all_projects(self, org_name=None):
        """List all projects using GraphQL API"""
        print(f"\n📋 Listing projects...")
        
        if org_name:
            query = f'''
            query {{
              organization(login: "{org_name}") {{
                projectsV2(first: 50) {{
                  nodes {{
                    id
                    title
                    shortDescription
                    public
                    closed
                    createdAt
                    updatedAt
                    url
                  }}
                }}
              }}
            }}
            '''
        else:
            query = '''
            query {
              viewer {
                projectsV2(first: 50) {
                  nodes {
                    id
                    title
                    shortDescription
                    public
                    closed
                    createdAt
                    updatedAt
                    url
                  }
                }
              }
            }
            '''
        
        try:
            result = self.utils.run_gh_cmd([
                "api", "graphql",
                "-f", f"query={query}"
            ])
            
            data = json.loads(result)
            if "errors" in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return []
            
            if org_name:
                projects = data["data"]["organization"]["projectsV2"]["nodes"]
            else:
                projects = data["data"]["viewer"]["projectsV2"]["nodes"]
            
            print(f"✅ Found {len(projects)} projects")
            
            if projects:
                print(f"\n📋 Projects List:")
                for project in projects:
                    status = "closed" if project.get("closed") else "open"
                    visibility = "public" if project.get("public") else "private"
                    description = project.get("shortDescription", "No description")
                    print(f"  • {project['title']} ({status}, {visibility})")
                    print(f"    ID: {project['id']}")
                    print(f"    Description: {description}")
                    print(f"    URL: {project.get('url', 'N/A')}")
                    print()
            
            return projects
        except Exception as e:
            print(f"❌ Error listing projects: {e}")
            return []

    def project_dashboard(self, project_id):
        """Generate project dashboard with statistics"""
        print(f"\n📊 Project Dashboard")
        print("=" * 30)
        
        try:
            items = self.get_project_items(project_id)
            
            if not items:
                print("No items found in project")
                return {}
            
            issues = [item for item in items if "Issue" in str(item.get("content", {}))]
            prs = [item for item in items if "PullRequest" in str(item.get("content", {}))]
            
            open_issues = [i for i in issues if i.get("content", {}).get("state") == "OPEN"]
            closed_issues = [i for i in issues if i.get("content", {}).get("state") == "CLOSED"]
            
            stats = {
                "total_items": len(items),
                "issues": {"total": len(issues), "open": len(open_issues), "closed": len(closed_issues)},
                "pull_requests": len(prs)
            }
            
            print(f"📊 Total Items: {stats['total_items']}")
            print(f"📋 Issues: {stats['issues']['total']} (Open: {stats['issues']['open']}, Closed: {stats['issues']['closed']})")
            print(f"🔄 Pull Requests: {stats['pull_requests']}")
            
            print(f"\n📋 Recent Items:")
            for i, item in enumerate(items[:5], 1):
                content = item.get("content", {})
                item_type = "Issue" if "Issue" in str(content) else "PR"
                number = content.get("number", "N/A")
                title = content.get("title", "No title")
                state = content.get("state", "unknown")
                print(f"   {i}. [{item_type}] #{number}: {title} ({state})")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
            return {}
