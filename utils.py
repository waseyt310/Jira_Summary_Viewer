"""
Utility functions for JIRA Daily Activity Dashboard
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from config import get_config
import logging

config = get_config()
logger = logging.getLogger(__name__)

def format_date(date_value, format_type: str = "date") -> str:
    """Format date for display"""
    if pd.isna(date_value) or date_value is None:
        return "N/A"
    
    try:
        if isinstance(date_value, str):
            date_value = pd.to_datetime(date_value)
        
        if format_type == "date":
            return date_value.strftime("%Y-%m-%d")
        elif format_type == "datetime":
            return date_value.strftime("%Y-%m-%d %H:%M")
        elif format_type == "relative":
            now = datetime.now()
            if hasattr(date_value, 'tz_localize') and date_value.tz is None:
                date_value = date_value.tz_localize('UTC').tz_convert('UTC')
            elif hasattr(date_value, 'tz'):
                date_value = date_value.tz_convert('UTC')
            
            diff = now - date_value.replace(tzinfo=None)
            days = diff.days
            
            if days == 0:
                return "Today"
            elif days == 1:
                return "Yesterday"
            elif days < 7:
                return f"{days} days ago"
            elif days < 30:
                weeks = days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            else:
                months = days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
    except Exception:
        return "N/A"

def get_status_color(status: str) -> str:
    """Get color for status"""
    return config['colors'].get(status, "#6c757d")

def get_issue_type_icon(issue_type: str) -> str:
    """Get icon for issue type"""
    return config['icons'].get(issue_type, "📄")

def create_status_badge(status: str) -> str:
    """Create HTML badge for status"""
    color = get_status_color(status)
    return f"""
    <span style="
        background-color: {color};
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    ">{status}</span>
    """

def create_priority_badge(priority: str) -> str:
    """Create HTML badge for priority"""
    priority_colors = {
        "Highest": "#dc3545",
        "High": "#fd7e14",
        "Medium": "#ffc107",
        "Low": "#28a745",
        "Lowest": "#6c757d"
    }
    color = priority_colors.get(priority, "#6c757d")
    return f"""
    <span style="
        background-color: {color};
        color: white;
        padding: 2px 6px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        margin: 1px;
    ">{priority}</span>
    """

def filter_dataframe_by_status(df: pd.DataFrame, status_filter: str = "All") -> pd.DataFrame:
    """Filter dataframe by status"""
    if df.empty:
        return df
    
    if status_filter == "All":
        return df
    elif status_filter == "Completed":
        completed_statuses = ["Done", "Closed", "Resolved"]
        return df[df['status'].isin(completed_statuses)]
    elif status_filter == "In Progress":
        progress_statuses = ["In Progress", "In Review", "Testing"]
        return df[df['status'].isin(progress_statuses)]
    elif status_filter == "Blocked":
        return df[df['status'] == "Blocked"]
    else:
        return df[df['status'] == status_filter]

def create_status_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create status distribution pie chart"""
    if df.empty:
        return go.Figure()
    
    status_counts = df['status'].value_counts()
    colors = [get_status_color(status) for status in status_counts.index]
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Issue Status Distribution",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=True,
        height=400,
        font=dict(size=12)
    )
    
    return fig

def create_issue_type_chart(df: pd.DataFrame) -> go.Figure:
    """Create issue type distribution chart"""
    if df.empty:
        return go.Figure()
    
    type_counts = df['issue_type'].value_counts()
    
    fig = px.bar(
        x=type_counts.index,
        y=type_counts.values,
        title="Issue Type Distribution",
        labels={'x': 'Issue Type', 'y': 'Count'}
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig

def create_activity_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """Create activity timeline chart"""
    if df.empty:
        return go.Figure()
    
    # Group by date and count
    df['updated_date'] = df['updated'].dt.date
    daily_counts = df.groupby('updated_date').size().reset_index(name='count')
    
    fig = px.line(
        daily_counts,
        x='updated_date',
        y='count',
        title="Daily Issue Activity",
        labels={'updated_date': 'Date', 'count': 'Number of Issues Updated'}
    )
    
    fig.update_traces(mode='lines+markers')
    fig.update_layout(height=400)
    
    return fig

def create_assignee_workload_chart(df: pd.DataFrame) -> go.Figure:
    """Create assignee workload chart"""
    if df.empty:
        return go.Figure()
    
    assignee_counts = df['assignee'].value_counts().head(10)  # Top 10 assignees
    
    fig = px.bar(
        x=assignee_counts.values,
        y=assignee_counts.index,
        orientation='h',
        title="Top 10 Assignees by Issue Count",
        labels={'x': 'Number of Issues', 'y': 'Assignee'}
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_team_workload_chart(df: pd.DataFrame, team_members_config: Dict[str, str]) -> go.Figure:
    """Create team member workload chart with proper name mapping"""
    if df.empty:
        return go.Figure()
    
    # Create reverse mapping from email to display name
    email_to_name = {email: name for name, email in team_members_config.items()}
    
    # Count issues by assignee email and map to display names
    assignee_counts = df['assignee'].value_counts()
    
    # Map emails to display names
    display_data = {}
    for email, count in assignee_counts.items():
        display_name = email_to_name.get(email, email.split('@')[0] if '@' in email else email)
        display_data[display_name] = count
    
    # Sort by count
    sorted_data = dict(sorted(display_data.items(), key=lambda x: x[1], reverse=True))
    
    fig = px.bar(
        x=list(sorted_data.values()),
        y=list(sorted_data.keys()),
        orientation='h',
        title="Team Member Workload",
        labels={'x': 'Number of Issues', 'y': 'Team Member'},
        color=list(sorted_data.values()),
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        coloraxis_showscale=False
    )
    
    return fig

def filter_dataframe_by_team_members(df: pd.DataFrame, selected_members: List[str], team_config: Dict[str, str]) -> pd.DataFrame:
    """Filter dataframe by selected team members"""
    if df.empty or not selected_members:
        return df
    
    # Get email addresses for selected members
    member_emails = [team_config[member] for member in selected_members if member in team_config]
    
    if not member_emails:
        return df
    
    # Filter by assignee email
    return df[df['assignee'].isin(member_emails)]

def format_dataframe_for_display(df: pd.DataFrame, columns_to_show: List[str] = None) -> pd.DataFrame:
    """Format dataframe for display in Streamlit"""
    if df.empty:
        return df
    
    display_df = df.copy()
    
    # Default columns if not specified
    if columns_to_show is None:
        columns_to_show = ['key', 'summary', 'status', 'issue_type', 'assignee', 'updated', 'due_date']
    
    # Filter columns that exist in the dataframe
    columns_to_show = [col for col in columns_to_show if col in display_df.columns]
    display_df = display_df[columns_to_show]
    
    # Format date columns
    date_columns = ['created', 'updated', 'due_date', 'resolution_date']
    for col in date_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: format_date(x, "date"))
    
    # Rename columns for better display
    column_renames = {
        'key': 'Issue Key',
        'summary': 'Summary',
        'status': 'Status',
        'issue_type': 'Type',
        'assignee': 'Assignee',
        'reporter': 'Reporter',
        'priority': 'Priority',
        'created': 'Created',
        'updated': 'Updated',
        'due_date': 'Due Date',
        'resolution_date': 'Resolved',
        'story_points': 'Story Points',
        'sprint': 'Sprint',
        'labels': 'Labels',
        'components': 'Components'
    }
    
    display_df = display_df.rename(columns=column_renames)
    
    return display_df

def get_summary_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Get summary metrics from dataframe"""
    if df.empty:
        return {
            'total_issues': 0,
            'completed_issues': 0,
            'in_progress_issues': 0,
            'blocked_issues': 0,
            'completion_rate': 0,
            'avg_story_points': 0
        }
    
    completed_statuses = ["Done", "Closed", "Resolved"]
    # Updated logic: count "Development" status as "In Progress" for Weekly Activity
    progress_statuses = ["Development", "In Progress", "In Review", "Testing"]
    
    total_issues = len(df)
    completed_issues = len(df[df['status'].isin(completed_statuses)])
    in_progress_issues = len(df[df['status'].isin(progress_statuses)])
    blocked_issues = len(df[df['status'] == "Blocked"])
    completion_rate = (completed_issues / total_issues * 100) if total_issues > 0 else 0
    
    # Calculate average story points for completed issues with robust error handling
    avg_story_points = 0
    try:
        if 'story_points' in df.columns:
            completed_df = df[df['status'].isin(completed_statuses)]
            if not completed_df.empty:
                # Ensure story_points are numeric and handle any non-numeric values
                story_points_series = pd.to_numeric(completed_df['story_points'], errors='coerce')
                # Remove NaN values and calculate mean
                valid_story_points = story_points_series.dropna()
                if len(valid_story_points) > 0:
                    avg_story_points = valid_story_points.mean()
    except Exception as e:
        logger.error(f"Error calculating story points average: {str(e)}")
        avg_story_points = 0
    
    return {
        'total_issues': total_issues,
        'completed_issues': completed_issues,
        'in_progress_issues': in_progress_issues,
        'blocked_issues': blocked_issues,
        'completion_rate': completion_rate,
        'avg_story_points': avg_story_points or 0
    }

def create_metrics_cards(metrics: Dict[str, Any]) -> None:
    """Create metric cards using Streamlit columns"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Issues",
            value=metrics['total_issues']
        )
    
    with col2:
        st.metric(
            label="Completed",
            value=metrics['completed_issues'],
            delta=f"{metrics['completion_rate']:.1f}% completion rate"
        )
    
    with col3:
        st.metric(
            label="In Progress",
            value=metrics['in_progress_issues']
        )
    
    with col4:
        st.metric(
            label="Blocked",
            value=metrics['blocked_issues'],
            delta="🚫" if metrics['blocked_issues'] > 0 else None
        )

def export_to_csv(df: pd.DataFrame, filename: str) -> bytes:
    """Export dataframe to CSV"""
    return df.to_csv(index=False).encode('utf-8')

def create_jira_issue_link(issue_key: str, jira_url: str = None) -> str:
    """Create clickable link to JIRA issue"""
    if jira_url is None:
        jira_url = config['jira']['JIRA_URL']
    
    return f"{jira_url}/browse/{issue_key}"

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def create_priority_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create a priority table format matching the exact layout requirements"""
    if df.empty:
        return pd.DataFrame()
    
    # Create priority ranking based on order (most recently updated first for In Progress, oldest first for To Do)
    priority_table = df.copy()
    priority_table = priority_table.reset_index(drop=True)
    
    # Format assignee names better
    def format_assignee(assignee):
        if pd.isna(assignee) or assignee == 'Unassigned':
            return 'Unassigned'
        if '@' in str(assignee):
            # Extract name from email and format
            name_part = str(assignee).split('@')[0]
            # Convert email format to readable name (e.g., waseyt.ibrahim -> Waseyt Ibrahim)
            formatted_name = name_part.replace('.', ' ').title()
            return formatted_name
        return str(assignee)
    
    # Helper function to format dates safely
    def format_date_safe(date_series):
        try:
            if date_series is None or pd.isna(date_series).all():
                return 'N/A'
            # Ensure the series is datetime
            date_series = pd.to_datetime(date_series, errors='coerce', utc=True)
            formatted_dates = date_series.dt.strftime('%Y-%m-%d')
            return formatted_dates.fillna('N/A')
        except (AttributeError, TypeError):
            return 'N/A'
    
    # Return the DataFrame as is since columns are already properly named and ordered from get_enhanced_priority_issues
    # No longer need ETA and Impact calculations
    return priority_table

def create_completed_issues_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create a table format for last week completed issues"""
    if df.empty:
        return pd.DataFrame()
    
    # Create the completed issues table
    completed_table = df.copy()
    
    # Helper function to format assignee names
    def format_assignee(assignee):
        if pd.isna(assignee) or assignee == 'Unassigned':
            return 'Unassigned'
        if '@' in str(assignee):
            # Extract name from email and format
            name_part = str(assignee).split('@')[0]
            # Convert email format to readable name (e.g., waseyt.ibrahim -> Waseyt Ibrahim)
            formatted_name = name_part.replace('.', ' ').title()
            return formatted_name
        return str(assignee)

    # Helper function to format dates safely
    def format_date_safe(date_value):
        try:
            if pd.isna(date_value):
                return 'N/A'
            # Ensure the value is datetime
            date_value = pd.to_datetime(date_value, errors='coerce', utc=True)
            if pd.isna(date_value):
                return 'N/A'
            return date_value.strftime('%Y-%m-%d')
        except (AttributeError, TypeError):
            return 'N/A'

    # Helper function to truncate text
    def safe_truncate(text, max_length=80):
        if pd.isna(text):
            return 'N/A'
        text = str(text)
        return text[:max_length] + '...' if len(text) > max_length else text

    # Create the table with required columns - matching Priority Dashboard format
    table_data = {
        'JIRA ID': completed_table['key'],
        'Issue Type': completed_table['issue_type'],
        'Summary': completed_table['summary'].apply(lambda x: safe_truncate(x, 80)),
        'Status': completed_table['status'],
        'Assigned To': completed_table['assignee'].apply(format_assignee),
        'Completed Date': completed_table['updated'].apply(format_date_safe),
        'Created Date': completed_table['created'].apply(format_date_safe),
        'Est. Story Points': completed_table.get('story_points', 0).fillna(0),
        'Act. Story Points': completed_table.get('actual_story_points', 0).fillna(0)
    }
    
    result_df = pd.DataFrame(table_data)
    return result_df 