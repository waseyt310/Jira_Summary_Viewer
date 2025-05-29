"""
JIRA Client for Daily Activity Dashboard
Handles all JIRA API interactions and data processing
"""
import streamlit as st
from jira import JIRA
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JIRAClient:
    """JIRA API client with caching and error handling"""
    
    def __init__(self):
        self.config = get_config()
        self.jira = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to JIRA"""
        try:
            jira_config = self.config['jira']
            self.jira = JIRA(
                server=jira_config['JIRA_URL'],
                basic_auth=(
                    jira_config['JIRA_USERNAME'],
                    jira_config['JIRA_API_TOKEN']
                )
            )
            logger.info("Successfully connected to JIRA")
        except Exception as e:
            logger.error(f"Failed to connect to JIRA: {str(e)}")
            st.error(f"Failed to connect to JIRA: {str(e)}")
            raise
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_weekly_activity(_self, days_back: int = 7) -> pd.DataFrame:
        """Get JIRA issues updated in the last N days"""
        try:
            jql = _self.config['jql']['WEEKLY_ACTIVITY'].format(days=days_back)
            issues = _self.jira.search_issues(
                jql,
                maxResults=1000,
                expand='changelog'
            )
            
            data = []
            for issue in issues:
                issue_data = _self._extract_issue_data(issue)
                data.append(issue_data)
            
            df = pd.DataFrame(data)
            if not df.empty:
                # Convert date columns
                date_columns = ['created', 'updated', 'due_date', 'resolution_date']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            
            logger.info(f"Retrieved {len(data)} issues for weekly activity")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching weekly activity: {str(e)}")
            st.error(f"Error fetching weekly activity: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300, hash_funcs={"builtins.list": lambda x: str(sorted(x)) if x else "all"})  # Cache for 5 minutes with proper team member hashing
    def get_team_weekly_activity(_self, days_back: int = 7, selected_members: List[str] = None) -> pd.DataFrame:
        """Get JIRA issues updated in the last N days filtered by team members"""
        try:
            # Build JQL with team member filter
            base_jql = f"updated >= -{days_back}d OR created >= -{days_back}d"
            
            if selected_members:
                # Get email addresses for selected members
                team_config = _self.config['team_members']
                member_emails = []
                for member in selected_members:
                    if member in team_config:
                        member_emails.append(team_config[member])
                
                if member_emails:
                    # Create assignee filter
                    assignee_filter = " OR ".join([f'assignee = "{email}"' for email in member_emails])
                    jql = f"({base_jql}) AND ({assignee_filter}) ORDER BY updated DESC"
                else:
                    jql = f"{base_jql} ORDER BY updated DESC"
            else:
                jql = f"{base_jql} ORDER BY updated DESC"
            
            logger.info(f"Team activity JQL: {jql}")
            
            issues = _self.jira.search_issues(
                jql,
                maxResults=1000,
                expand='changelog'
            )
            
            data = []
            for issue in issues:
                issue_data = _self._extract_issue_data(issue)
                data.append(issue_data)
            
            df = pd.DataFrame(data)
            if not df.empty:
                # Convert date columns
                date_columns = ['created', 'updated', 'due_date', 'resolution_date']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            
            logger.info(f"Retrieved {len(data)} team issues for weekly activity")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching team weekly activity: {str(e)}")
            st.error(f"Error fetching team weekly activity: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_priority_issues(_self, priority_type: str = "current") -> pd.DataFrame:
        """Get priority issues based on priority field"""
        try:
            if priority_type == "current":
                jql = _self.config['jql']['CURRENT_PRIORITIES']
            else:
                jql = _self.config['jql']['UP_NEXT_PRIORITIES']
            
            logger.info(f"Priority {priority_type} JQL: {jql}")
            
            issues = _self.jira.search_issues(
                jql,
                maxResults=50,  # Limit to top 50 priority issues
                expand='changelog'
            )
            
            data = []
            for issue in issues:
                issue_data = _self._extract_issue_data(issue)
                data.append(issue_data)
            
            df = pd.DataFrame(data)
            if not df.empty:
                # Convert date columns
                date_columns = ['created', 'updated', 'due_date', 'resolution_date']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            
            logger.info(f"Retrieved {len(df)} {priority_type} priority issues")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {priority_type} priority issues: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)
    def get_my_issues(_self) -> pd.DataFrame:
        """Get issues assigned to current user"""
        try:
            jql = _self.config['jql']['MY_ISSUES']
            issues = _self.jira.search_issues(jql, maxResults=100)
            
            data = []
            for issue in issues:
                issue_data = _self._extract_issue_data(issue)
                data.append(issue_data)
            
            df = pd.DataFrame(data)
            if not df.empty:
                # Convert date columns
                date_columns = ['created', 'updated', 'due_date', 'resolution_date']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            
            logger.info(f"Retrieved {len(data)} issues assigned to current user")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching my issues: {str(e)}")
            st.error(f"Error fetching my issues: {str(e)}")
            return pd.DataFrame()
    
    def _extract_issue_data(self, issue) -> Dict[str, Any]:
        """Extract relevant data from JIRA issue"""
        try:
            # Basic issue information
            data = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name if issue.fields.status else 'Unknown',
                'issue_type': issue.fields.issuetype.name if issue.fields.issuetype else 'Unknown',
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown',
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'description': issue.fields.description[:200] + '...' if issue.fields.description and len(issue.fields.description) > 200 else issue.fields.description or '',
            }
            
            # Assignee field - handle different User object formats
            assignee_value = 'Unassigned'
            try:
                if issue.fields.assignee:
                    if hasattr(issue.fields.assignee, 'emailAddress'):
                        assignee_value = issue.fields.assignee.emailAddress
                    elif hasattr(issue.fields.assignee, 'name'):
                        assignee_value = issue.fields.assignee.name
                    elif hasattr(issue.fields.assignee, 'displayName'):
                        assignee_value = issue.fields.assignee.displayName
                    else:
                        assignee_value = str(issue.fields.assignee)
            except (AttributeError, TypeError):
                assignee_value = 'Unassigned'
            data['assignee'] = assignee_value
            
            # Priority field - handle PropertyHolder objects
            priority_value = 'None'
            try:
                if hasattr(issue.fields, 'priority') and issue.fields.priority:
                    if hasattr(issue.fields.priority, 'name'):
                        priority_value = issue.fields.priority.name
                    elif hasattr(issue.fields.priority, 'value'):
                        priority_value = issue.fields.priority.value
                    else:
                        priority_value = str(issue.fields.priority)
            except (AttributeError, TypeError):
                priority_value = 'None'
            data['priority'] = priority_value
            
            # Due date
            data['due_date'] = getattr(issue.fields, 'duedate', None)
            
            # Resolution date (if resolved)
            data['resolution_date'] = getattr(issue.fields, 'resolutiondate', None)
            
            # Labels
            data['labels'] = ', '.join(issue.fields.labels) if issue.fields.labels else ''
            
            # Components
            components = []
            if hasattr(issue.fields, 'components') and issue.fields.components:
                components = [comp.name for comp in issue.fields.components]
            data['components'] = ', '.join(components)
            
            # Story points (if available) - handle different custom field formats
            story_points = 0
            # Try common story points custom field IDs (added customfield_10015 based on JIRA verification)
            for field_id in ['customfield_10015', 'customfield_10016', 'customfield_10002', 'customfield_10004']:
                try:
                    field_value = getattr(issue.fields, field_id, None)
                    if field_value is not None:
                        # Convert to numeric value
                        if isinstance(field_value, (int, float)):
                            story_points = field_value
                            break
                        elif hasattr(field_value, 'value'):
                            # Handle select field objects
                            story_points = float(field_value.value) if field_value.value else 0
                            break
                        elif isinstance(field_value, str) and field_value.replace('.', '').isdigit():
                            # Handle string numbers
                            story_points = float(field_value)
                            break
                except (AttributeError, ValueError, TypeError):
                    continue
            data['story_points'] = story_points
            
            # Sprint information (if available)
            sprint_name = 'No Sprint'
            for field_id in ['customfield_10020', 'customfield_10001', 'customfield_10005']:
                try:
                    sprint_field = getattr(issue.fields, field_id, None)
                    if sprint_field and len(sprint_field) > 0:
                        sprint_str = str(sprint_field[0])
                        if 'name=' in sprint_str:
                            sprint_name = sprint_str.split('name=')[1].split(',')[0]
                            break
                except (AttributeError, TypeError, IndexError):
                    continue
            data['sprint'] = sprint_name
            
            # Epic link (if available)
            epic_link = ''
            for field_id in ['customfield_10014', 'customfield_10003', 'customfield_10006']:
                try:
                    epic_field = getattr(issue.fields, field_id, None)
                    if epic_field:
                        epic_link = str(epic_field)
                        break
                except (AttributeError, TypeError):
                    continue
            data['epic_link'] = epic_link
            
            # Try to extract ETA field (common custom field names)
            eta_value = None
            for field_id in ['customfield_10030', 'customfield_10031', 'customfield_10032', 'customfield_10033']:
                try:
                    eta_field = getattr(issue.fields, field_id, None)
                    if eta_field:
                        eta_value = str(eta_field)
                        break
                except (AttributeError, TypeError):
                    continue
            data['eta_custom'] = eta_value
            
            # Try to extract Impact field (common custom field names)
            impact_value = None
            for field_id in ['customfield_10040', 'customfield_10041', 'customfield_10042', 'customfield_10043']:
                try:
                    impact_field = getattr(issue.fields, field_id, None)
                    if impact_field:
                        if hasattr(impact_field, 'value'):
                            impact_value = impact_field.value
                        elif hasattr(impact_field, 'name'):
                            impact_value = impact_field.name
                        else:
                            impact_value = str(impact_field)
                        break
                except (AttributeError, TypeError):
                    continue
            data['impact_custom'] = impact_value
            
            # Extract actual story points from JIRA custom fields (not time tracking)
            actual_story_points = None
            try:
                # Extract actual story points from JIRA custom fields directly
                # RPA project (ID 11232) uses customfield_11580 for "Story Points actual"
                # Other projects (ID 11236) use customfield_11642 for "Story point actual"
                for field_id in ['customfield_11580', 'customfield_11642']:
                    try:
                        field_value = getattr(issue.fields, field_id, None)
                        if field_value is not None:
                            # Convert to numeric value
                            if isinstance(field_value, (int, float)):
                                actual_story_points = field_value
                                break
                            elif hasattr(field_value, 'value'):
                                # Handle select field objects
                                actual_story_points = float(field_value.value) if field_value.value else None
                                break
                            elif isinstance(field_value, str) and field_value.replace('.', '').isdigit():
                                # Handle string numbers
                                actual_story_points = float(field_value)
                                break
                    except (AttributeError, ValueError, TypeError):
                        continue
                        
            except (AttributeError, TypeError) as e:
                # Log the error for debugging
                logger.debug(f"Error extracting actual story points for {issue.key}: {str(e)}")
                pass
            
            data['actual_story_points'] = actual_story_points
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting data from issue {issue.key}: {str(e)}")
            return {
                'key': getattr(issue, 'key', 'Unknown'),
                'summary': 'Error loading issue data',
                'status': 'Unknown',
                'issue_type': 'Unknown',
                'priority': 'None',
                'assignee': 'Unknown',
                'reporter': 'Unknown',
                'created': None,
                'updated': None,
                'description': '',
                'due_date': None,
                'resolution_date': None,
                'labels': '',
                'components': '',
                'story_points': 0,
                'sprint': 'Unknown',
                'epic_link': '',
                'eta_custom': None,
                'impact_custom': None,
                'actual_story_points': None
            }
    
    def get_user_info(self) -> Dict[str, str]:
        """Get current user information"""
        try:
            user = self.jira.current_user()
            return {
                'username': user,
                'display_name': user,
                'email': self.config['jira']['JIRA_USERNAME']
            }
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return {
                'username': 'Unknown',
                'display_name': 'Unknown User',
                'email': self.config['jira']['JIRA_USERNAME']
            }
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_projects(_self) -> List[Dict[str, str]]:
        """Get list of projects"""
        try:
            projects = _self.jira.projects()
            return [{'key': p.key, 'name': p.name} for p in projects]
        except Exception as e:
            logger.error(f"Error fetching projects: {str(e)}")
            return []
    
    def search_issues_custom(self, jql: str, max_results: int = 100) -> pd.DataFrame:
        """Search issues with custom JQL"""
        try:
            issues = self.jira.search_issues(jql, maxResults=max_results)
            
            data = []
            for issue in issues:
                issue_data = self._extract_issue_data(issue)
                data.append(issue_data)
            
            df = pd.DataFrame(data)
            if not df.empty:
                # Convert date columns
                date_columns = ['created', 'updated', 'due_date', 'resolution_date']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error with custom JQL search: {str(e)}")
            st.error(f"Error with custom JQL search: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_team_priority_issues(_self, priority_type: str = "current", selected_members: List[str] = None) -> pd.DataFrame:
        """Get priority issues filtered by team members"""
        try:
            # Get base JQL for priority type
            if priority_type == "current":
                base_jql = "status = 'In Progress'"
                order_by = "ORDER BY updated DESC"
            else:
                base_jql = "status in ('To Do', 'Open', 'Backlog', 'Selected for Development')"
                order_by = "ORDER BY created ASC"
            
            # Build JQL with team member filter
            if selected_members:
                # Get email addresses for selected members
                team_config = _self.config['team_members']
                member_emails = []
                for member in selected_members:
                    if member in team_config:
                        member_emails.append(team_config[member])
                
                if member_emails:
                    # Create assignee filter
                    assignee_filter = " OR ".join([f'assignee = "{email}"' for email in member_emails])
                    jql = f"({base_jql}) AND ({assignee_filter}) {order_by}"
                else:
                    jql = f"{base_jql} {order_by}"
            else:
                jql = f"{base_jql} {order_by}"
            
            logger.info(f"Team priority {priority_type} JQL: {jql}")
            
            issues = _self.jira.search_issues(
                jql,
                maxResults=50,  # Limit to top 50 priority issues
                expand='changelog'
            )
            
            data = []
            for issue in issues:
                issue_data = _self._extract_issue_data(issue)
                data.append(issue_data)
            
            df = pd.DataFrame(data)
            if not df.empty:
                # Convert date columns
                date_columns = ['created', 'updated', 'due_date', 'resolution_date']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            
            logger.info(f"Retrieved {len(df)} team {priority_type} priority issues")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching team {priority_type} priority issues: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=60, hash_funcs={"builtins.list": lambda x: str(sorted(x)) if x else "all"})  # Cache for 1 minute with proper team member hashing
    def get_enhanced_priority_issues(_self, priority_type: str = "current", selected_members: List[str] = None) -> pd.DataFrame:
        """Get priority issues with enhanced criteria for Development status and To Do items"""
        try:
            # Build JQL based on priority type
            if priority_type == "current":
                # Current Priorities: Exactly "Development" status
                base_jql = 'status = "Development"'
                order_by = "ORDER BY priority DESC, duedate ASC, created ASC"
            else:
                # Up Next Priorities: To Do status items
                base_jql = 'status in ("To Do", "Open", "Backlog", "Selected for Development")'
                order_by = "ORDER BY priority DESC, created ASC"
            
            # Build JQL with team member filter
            if selected_members:
                # Get email addresses for selected members
                team_config = _self.config['team_members']
                member_emails = []
                for member in selected_members:
                    if member in team_config:
                        member_emails.append(team_config[member])
                
                if member_emails:
                    # Create assignee filter
                    assignee_filter = " OR ".join([f'assignee = "{email}"' for email in member_emails])
                    jql = f"({base_jql}) AND ({assignee_filter}) {order_by}"
                else:
                    jql = f"{base_jql} {order_by}"
            else:
                jql = f"{base_jql} {order_by}"
            
            logger.info(f"Enhanced priority {priority_type} JQL: {jql}")
            
            issues = _self.jira.search_issues(
                jql,
                maxResults=50,  # Limit to top 50 priority issues
                expand='changelog,worklog'  # Also expand worklog to get time tracking data
            )
            
            data = []
            for issue in issues:
                issue_data = _self._extract_issue_data(issue)
                # Add rank number based on priority and due date
                issue_data['rank'] = len(data) + 1
                data.append(issue_data)
            
            df = pd.DataFrame(data)
            if not df.empty:
                # Convert date columns
                date_columns = ['created', 'updated', 'due_date', 'resolution_date']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
                
                # Ensure all required columns exist with proper names
                df = df.rename(columns={
                    'rank': 'Priority',
                    'key': 'JIRA ID',
                    'status': 'Status',
                    'issue_type': 'Issue Type',
                    'created': 'Start Date',
                    'due_date': 'Due Date',
                    'story_points': 'Est. Story Points',
                    'actual_story_points': 'Act. Story Points',
                    'assignee': 'Assigned To',
                    'summary': 'Description'
                })
                
                # Reorder columns to match requirements (added Issue Type)
                columns = [
                    'Priority', 'JIRA ID', 'Issue Type', 'Status', 'Start Date', 
                    'Due Date', 'Est. Story Points', 'Act. Story Points', 
                    'Assigned To', 'Description'
                ]
                
                # Ensure all columns exist, fill missing with None
                for col in columns:
                    if col not in df.columns:
                        df[col] = None
                
                # Select and order columns
                df = df[columns]
            
            logger.info(f"Retrieved {len(df)} enhanced {priority_type} priority issues")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching enhanced {priority_type} priority issues: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300, hash_funcs={"builtins.list": lambda x: str(sorted(x)) if x else "all"})  # Cache for 5 minutes with proper team member hashing
    def get_last_week_completed(_self, selected_members: List[str] = None) -> pd.DataFrame:
        """Get issues completed last week for all relevant issue types"""
        try:
            # Build JQL for last week completed issues - expanded to include all work item types
            base_jql = "assignee = currentUser() AND status = Done AND updated >= startOfWeek(-1w) AND updated < startOfWeek() AND issueType in (Task, Bug, Enhancement, Support, Epic, Story)"
            
            if selected_members:
                # Get email addresses for selected members
                team_config = _self.config['team_members']
                member_emails = []
                for member in selected_members:
                    if member in team_config:
                        member_emails.append(team_config[member])
                
                if member_emails:
                    # Replace currentUser() with actual team member emails
                    assignee_filter = " OR ".join([f'assignee = "{email}"' for email in member_emails])
                    base_jql = f"({assignee_filter}) AND status = Done AND updated >= startOfWeek(-1w) AND updated < startOfWeek() AND issueType in (Task, Bug, Enhancement, Support, Epic, Story)"
                else:
                    # No valid team members, return empty
                    return pd.DataFrame()
            
            jql = f"{base_jql} ORDER BY updated DESC"
            
            logger.info(f"Last week completed JQL: {jql}")
            
            issues = _self.jira.search_issues(
                jql,
                maxResults=100,
                expand='changelog'
            )
            
            data = []
            for issue in issues:
                issue_data = _self._extract_issue_data(issue)
                data.append(issue_data)
            
            df = pd.DataFrame(data)
            if not df.empty:
                # Convert date columns
                date_columns = ['created', 'updated', 'due_date', 'resolution_date']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            
            logger.info(f"Retrieved {len(data)} completed issues from last week")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching last week completed issues: {str(e)}")
            st.error(f"Error fetching last week completed issues: {str(e)}")
            return pd.DataFrame() 