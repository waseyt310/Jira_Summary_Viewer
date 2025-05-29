"""
Configuration file for JIRA Daily Activity Dashboard
"""
import os
import streamlit as st
from typing import Dict, Any

def get_jira_credentials():
    """Get JIRA credentials from Streamlit secrets or environment variables"""
    try:
        # Try to get from Streamlit secrets (for cloud deployment)
        if hasattr(st, 'secrets') and 'jira' in st.secrets:
            return {
                "JIRA_URL": st.secrets["jira"]["JIRA_URL"],
                "JIRA_USERNAME": st.secrets["jira"]["JIRA_USERNAME"], 
                "JIRA_API_TOKEN": st.secrets["jira"]["JIRA_API_TOKEN"]
            }
    except Exception:
        pass
    
    # Fallback to environment variables (for local development)
    return {
        "JIRA_URL": os.getenv("JIRA_URL", "https://spreetail.atlassian.net"),
        "JIRA_USERNAME": os.getenv("JIRA_USERNAME", ""),
        "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN", "")
    }

# JIRA Configuration - will be populated from secrets/env vars
JIRA_CONFIG = get_jira_credentials()

# Team Members Configuration - Updated to use JIRA display names for proper filtering
TEAM_MEMBERS = {
    "Waseyt Ibrahim": "Waseyt Ibrahim",
    "Donn Mailing": "Donn Mailing", 
    "Edu Cielo": "Edu Cielo",
    "Mohammad Asim": "Mohammad Asim",
    "Ryan Kieselhorst": "Ryan Kieselhorst",
    "Shawn Parry": "Shawn Parry"
}

# Application Settings
APP_CONFIG = {
    "PAGE_TITLE": "JIRA Daily Activity & Priority Dashboard",
    "PAGE_ICON": "📊",
    "LAYOUT": "wide",
    "INITIAL_SIDEBAR_STATE": "expanded"
}

# Date and Time Settings
DATE_CONFIG = {
    "DEFAULT_DAYS_BACK": 7,
    "TIMEZONE": "UTC",
    "DATE_FORMAT": "%Y-%m-%d",
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S"
}

# JIRA JQL Queries
JQL_QUERIES = {
    "WEEKLY_ACTIVITY": "updated >= -{days}d OR created >= -{days}d ORDER BY updated DESC",
    "CURRENT_PRIORITIES": "status = 'In Progress' ORDER BY updated DESC",
    "UP_NEXT_PRIORITIES": "status in ('To Do', 'Open', 'Backlog', 'Selected for Development') ORDER BY created ASC",
    "MY_ISSUES": "assignee = currentUser() AND status != 'Done' AND status != 'Closed' ORDER BY updated DESC"
}

# Status Color Mapping
STATUS_COLORS = {
    "To Do": "#6c757d",
    "In Progress": "#007bff",
    "Done": "#28a745",
    "Closed": "#28a745",
    "Blocked": "#dc3545",
    "In Review": "#ffc107",
    "Testing": "#17a2b8",
    "Backlog": "#6f42c1"
}

# Issue Type Icons
ISSUE_TYPE_ICONS = {
    "Task": "📋",
    "Bug": "🐛",
    "Story": "📖",
    "Epic": "🎯",
    "Subtask": "📝",
    "Improvement": "✨",
    "New Feature": "🚀"
}

def get_config() -> Dict[str, Any]:
    """Get complete application configuration"""
    return {
        "jira": get_jira_credentials(),  # Always get fresh credentials
        "team_members": TEAM_MEMBERS,
        "app": APP_CONFIG,
        "date": DATE_CONFIG,
        "jql": JQL_QUERIES,
        "colors": STATUS_COLORS,
        "icons": ISSUE_TYPE_ICONS
    } 