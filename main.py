"""
JIRA Daily Activity & Priority Dashboard
Main Streamlit Application
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import time
import logging

# Import custom modules
from config import get_config
from jira_client import JIRAClient
from utils import (
    format_date, get_status_color, create_status_badge, create_priority_badge,
    filter_dataframe_by_status, create_status_distribution_chart, 
    create_issue_type_chart, create_activity_timeline_chart, 
    create_assignee_workload_chart, create_team_workload_chart,
    format_dataframe_for_display, get_summary_metrics, 
    create_metrics_cards, export_to_csv, create_jira_issue_link,
    filter_dataframe_by_team_members, truncate_text, get_issue_type_icon,
    create_priority_table, create_completed_issues_table
)

# Configure Streamlit page
config = get_config()
st.set_page_config(
    page_title=config['app']['PAGE_TITLE'],
    page_icon=config['app']['PAGE_ICON'],
    layout=config['app']['LAYOUT'],
    initial_sidebar_state=config['app']['INITIAL_SIDEBAR_STATE']
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tab-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: bold;
        color: #34495e;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 4px solid #3498db;
        margin: 0.8rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .stDataFrame {
        border: 1px solid #e1e4e8;
        border-radius: 0.8rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .priority-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin: 1.5rem 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .issue-card {
        background: white;
        padding: 1.5rem;
        margin: 0.8rem 0;
        border-radius: 0.8rem;
        border-left: 4px solid #3498db;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease-in-out;
    }
    .issue-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .refresh-info {
        background: linear-gradient(135deg, #e7f3ff 0%, #cce7ff 100%);
        padding: 0.8rem;
        border-radius: 0.5rem;
        font-size: 0.9rem;
        color: #0066cc;
        margin-bottom: 1.5rem;
        border: 1px solid #b3d9ff;
    }
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    /* Enhanced button styling */
    .stButton > button {
        border-radius: 0.5rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'jira_client' not in st.session_state:
        st.session_state.jira_client = None
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    if 'config' not in st.session_state:
        st.session_state.config = get_config()

def get_jira_client():
    """Get or create JIRA client instance"""
    if st.session_state.jira_client is None:
        try:
            with st.spinner("Connecting to JIRA..."):
                st.session_state.jira_client = JIRAClient()
                st.session_state.last_refresh = datetime.now()
        except Exception as e:
            st.error(f"Failed to connect to JIRA: {str(e)}")
            return None
    return st.session_state.jira_client

def render_header():
    """Render application header"""
    st.markdown('<div class="main-header">📊 JIRA Daily Activity & Priority Dashboard</div>', unsafe_allow_html=True)
    
    # Show last refresh info without the refresh button
    if st.session_state.last_refresh:
        st.markdown(f'<div class="refresh-info">Last refreshed: {st.session_state.last_refresh.strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)

def render_global_sidebar():
    """Render global sidebar with unified team member filter"""
    with st.sidebar:
        st.header("🌐 Global Filters")
        
        # Get team members from config
        team_members = list(st.session_state.config['team_members'].keys())
        
        # Global team member filter
        st.subheader("👥 Filter by Team Member(s)")
        selected_members = st.multiselect(
            "Select team members:",
            options=team_members,
            default=team_members,  # All selected by default
            help="This filter applies to ALL tabs. Select team members to view their issues across the entire dashboard.",
            key="global_team_filter"
        )
        
        # Show current selection info
        if selected_members:
            if len(selected_members) == len(team_members):
                st.info("📊 **Showing data for:** All Team Members")
            else:
                st.info(f"📊 **Showing data for:** {', '.join(selected_members)}")
        else:
            st.warning("⚠️ No team members selected. Please select at least one team member.")
        
        st.markdown("---")
        
        # Global refresh button
        st.subheader("🔄 Data Management")
        if st.button("🔄 Refresh All Data (Including Priority)", type="primary", key="global_refresh"):
            # Clear all cached data including priority data
            st.cache_data.clear()
            # Reset JIRA client to force reconnection
            st.session_state.jira_client = None
            st.success("✅ All data refreshed! Changes from JIRA should now be visible.")
            st.rerun()
        
        # Last refresh info
        if st.session_state.last_refresh:
            st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Help section
        st.subheader("ℹ️ How It Works")
        st.markdown("""
        **Global Team Filter:**
        - Applies to ALL tabs consistently
        - Shows issues where selected members are **Assignees**
        - Updates all data views simultaneously
        
        **Tab-Specific Filters:**
        - Weekly Activity: Date range, status
        - Priority Dashboard: Automatic status-based filtering
        """)
        
        if st.button("🔄 Force Refresh", help="Clear cache and fetch fresh data from JIRA"):
            # Clear all Streamlit cache
            st.cache_data.clear()
            st.rerun()
        
        # Debug info for selected team members
        if st.checkbox("🔍 Debug Info", help="Show selected team members for troubleshooting"):
            st.write("**Selected Members:**", selected_members)
            st.write("**Total Selected:**", len(selected_members))
        
        return selected_members

def show_weekly_activity(selected_members):
    """Display weekly activity tab with global team filtering"""
    st.header("📈 Weekly JIRA Issue Activity")
    
    # Initialize JIRA client if needed
    jira_client = get_jira_client()
    if jira_client is None:
        st.error("❌ Unable to connect to JIRA. Please check your configuration.")
        return
    
    # Check if team members are selected
    if not selected_members:
        st.warning("⚠️ Please select at least one team member in the sidebar to view activity.")
        return
    
    # Tab-specific filters (no team member filter here anymore)
    col1, col2 = st.columns(2)
    
    with col1:
        # Date range
        days_back = st.selectbox(
            "📅 Time Period",
            options=[7, 14, 21, 30],
            index=0,
            help="Number of days to look back for activity"
        )
    
    with col2:
        # Status filter
        status_filter = st.selectbox(
            "📊 Status Filter",
            options=["All", "In Progress", "Completed", "Blocked"],
            index=0
        )
    
    # Fetch data using global team filter
    with st.spinner("🔄 Fetching JIRA data..."):
        df = jira_client.get_team_weekly_activity(
            days_back=days_back,
            selected_members=selected_members
        )
    
    if df.empty:
        st.warning(f"📭 No issues found for the selected team members in the last {days_back} days.")
        return
    
    # Apply status filter
    filtered_df = filter_dataframe_by_status(df, status_filter)
    
    if filtered_df.empty:
        st.warning(f"📭 No issues found with status: {status_filter}")
        return
    
    # Display metrics
    st.subheader("📊 Summary Metrics")
    metrics = get_summary_metrics(filtered_df)
    create_metrics_cards(metrics)
    
    # Additional team metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Team Members", len(selected_members))
    with col2:
        avg_issues_per_member = metrics['total_issues'] / len(selected_members) if selected_members else 0
        st.metric("📋 Avg Issues/Member", f"{avg_issues_per_member:.1f}")
    with col3:
            total_story_points = filtered_df['story_points'].sum()
            st.metric("⭐ Total Story Points", f"{total_story_points:.0f}")
    
    # Charts
    st.subheader("📈 Visual Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Status distribution
        status_fig = create_status_distribution_chart(filtered_df)
        st.plotly_chart(status_fig, use_container_width=True)
        
        # Activity timeline
        timeline_fig = create_activity_timeline_chart(filtered_df)
        st.plotly_chart(timeline_fig, use_container_width=True)
    
    with chart_col2:
        # Issue type distribution
        type_fig = create_issue_type_chart(filtered_df)
        st.plotly_chart(type_fig, use_container_width=True)
        
        # Team member workload (only for selected members)
        if len(selected_members) > 1:
            workload_fig = create_team_workload_chart(filtered_df, st.session_state.config['team_members'])
            st.plotly_chart(workload_fig, use_container_width=True)
    
    # Issues Details section - properly organized under Weekly JIRA Issue Activity
    st.subheader("📋 Issues Details")
    
    # Table display options
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**{len(filtered_df)} issues found**")
    with col2:
        show_description = st.checkbox("Show Description", value=False)
    with col3:
        # Export button
        csv_data = export_to_csv(filtered_df, f"team_activity_{days_back}d.csv")
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"team_activity_{days_back}d_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Prepare display columns - ensure jira_link is available in the dataframe
    display_columns = [
        'key', 'summary', 'status', 'issue_type', 'assignee', 'priority', 'updated', 'due_date',
        'story_points', 'actual_story_points', 'assigned_to'
    ]
    if show_description:
        display_columns.insert(2, 'description')
    
    # Format and display table
    display_df = format_dataframe_for_display(filtered_df, display_columns)
    
    # Add JIRA Link column
    if not display_df.empty and 'Issue Key' in display_df.columns:
        jira_base_url = st.session_state.config['jira']['JIRA_URL']
        display_df['JIRA Link'] = display_df['Issue Key'].apply(
            lambda x: f"{jira_base_url}/browse/{x}" if pd.notna(x) else ""
        )
    
    # Make the table interactive
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        column_config={
            "Issue Key": st.column_config.TextColumn(
                "Issue Key",
                help="JIRA issue identifier",
                width="medium"
            ),
            "JIRA Link": st.column_config.LinkColumn(
                "JIRA Link",
                help="Click to open in JIRA",
                width="small"
            ),
            "Est. Story Points": st.column_config.NumberColumn(
                "Est. Story Points",
                help="Estimated effort in story points",
                format="%.1f",
                width="small"
            ),
            "Act. Story Points": st.column_config.NumberColumn(
                "Act. Story Points", 
                help="Actual effort logged from JIRA",
                format="%.1f",
                width="small"
            )
        }
    )
    
    # Add totals for story points with improved UI - positioned at the end of Issues Details
    st.markdown("### 📊 Story Points Summary")
    col1, col2 = st.columns(2)
    with col1:
        total_estimated = filtered_df['story_points'].sum()
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='margin: 0; color: #2E86AB;'>📈 Total Est. Story Points</h4>
            <h2 style='margin: 0; color: #2E86AB;'>{total_estimated:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        total_actual = filtered_df['actual_story_points'].sum()
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='margin: 0; color: #A23B72;'>✅ Total Act. Story Points</h4>
            <h2 style='margin: 0; color: #A23B72;'>{total_actual:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)

def render_priority_dashboard_tab(selected_members):
    """Render the Priority Dashboard tab with enhanced criteria and global team filtering"""
    st.header("🎯 Priority Dashboard")
    
    jira_client = get_jira_client()
    if jira_client is None:
        return
    
    # Check if team members are selected
    if not selected_members:
        st.warning("⚠️ Please select at least one team member in the sidebar to view priorities.")
        return
    
    # Information about the Priority Dashboard structure
    with st.expander("ℹ️ About Priority Dashboard Structure", expanded=False):
        st.markdown("""
        **Priority Dashboard Data Structure:**
        
        **Current Priorities (Due This Week & In Progress):**
        - Shows issues with "In Progress" status AND due date within current week (Monday to Sunday)
        - Current week: Monday, May 26, 2025 to Sunday, June 1, 2025 (dynamically calculated)
        - Ordered by Priority rank, then by Due Date (earliest first)
        - These are the most urgent items requiring immediate attention
        
        **Up Next Priorities (To Do for Future Work):**
        - Shows issues with "To Do", "Open", "Backlog", or "Selected for Development" status
        - Excludes items due this week (focuses on future work)
        - Ordered by Priority rank, then by creation date (oldest first)
        - These are items ready to be picked up after current priorities
        
        **Column Definitions:**
        - **Priority**: Numerical ranking (1, 2, 3...)
        - **Issue Key**: JIRA issue identifier (e.g., RPA-1349)
        - **JIRA Link**: Clickable link to open issue in JIRA
        - **Issue Type**: Type of JIRA issue (Story, Task, Bug, Epic, etc.)
        - **Status**: Current JIRA status
        - **Start Date**: Issue creation date
        - **Due Date**: Scheduled due date (if set)
        - **Est. Story Points**: Estimated effort
        - **Act. Story Points**: Actual effort logged (from time tracking)
        - **Assigned To**: Team member assigned to the issue
        - **Description**: Issue summary/title
        """)
    
    # Display current week information
    from datetime import datetime, timedelta
    today = datetime.now()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    st.info(f"📅 **Current Week:** {week_start.strftime('%B %d, %Y')} to {week_end.strftime('%B %d, %Y')}")
    
    # Add cache information
    st.markdown("""
    💡 **Data Refresh Info:** 
    - Priority data updates every **60 seconds** automatically
    - Story point changes in JIRA will appear within 1 minute
    - Use the "**Refresh All Data**" button in the sidebar for immediate updates
    """)
    
    # Fetch priority data with enhanced criteria and global team filtering
    with st.spinner("🔄 Fetching priority issues with enhanced criteria..."):
        current_priorities_df = jira_client.get_enhanced_priority_issues("current", selected_members)
        up_next_priorities_df = jira_client.get_enhanced_priority_issues("up_next", selected_members)
    
    # Current Priorities Section
    st.subheader("🔥 Current Priorities (Due This Week & In Progress)")
    st.markdown("*Issues that are both **In Progress** and **due within the current week***")
    
    if not current_priorities_df.empty:
        st.success(f"**{len(current_priorities_df)} critical issues** requiring immediate attention this week")
        
        # Create priority table
        priority_table_df = create_priority_table(current_priorities_df)
        
        # Transform JIRA ID column to contain full URLs for linking
        if not priority_table_df.empty and 'JIRA ID' in priority_table_df.columns:
            jira_base_url = st.session_state.config['jira']['JIRA_URL']
            # Create a new column with just the issue keys for display
            priority_table_df['Issue Key'] = priority_table_df['JIRA ID'].copy()
            # Transform JIRA ID column to contain full URLs
            priority_table_df['JIRA ID'] = priority_table_df['JIRA ID'].apply(
                lambda x: f"{jira_base_url}/browse/{x}" if pd.notna(x) else ""
            )
            # Reorder columns to put Issue Key before JIRA ID
            columns = priority_table_df.columns.tolist()
            # Remove Issue Key from its current position and insert it before JIRA ID
            columns.remove('Issue Key')
            jira_id_index = columns.index('JIRA ID')
            columns.insert(jira_id_index, 'Issue Key')
            priority_table_df = priority_table_df[columns]
        
        # Display as interactive table with enhanced column configuration
        st.dataframe(
            priority_table_df,
            use_container_width=True,
            height=400,
            column_config={
                "Priority": st.column_config.NumberColumn(
                    "Priority",
                    help="Priority ranking (1 = highest priority)",
                    format="%d",
                    width="small"
                ),
                "Issue Key": st.column_config.TextColumn(
                    "Issue Key",
                    help="JIRA issue identifier",
                    width="medium"
                ),
                "JIRA ID": st.column_config.LinkColumn(
                    "JIRA Link",
                    help="Click to open in JIRA",
                    width="small"
                ),
                "Issue Type": st.column_config.TextColumn(
                    "Issue Type",
                    help="JIRA issue type (e.g., Story, Task, Bug)",
                    width="small"
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Current JIRA status",
                    width="medium"
                ),
                "Start Date": st.column_config.DateColumn(
                    "Start Date",
                    help="Issue creation date",
                    width="small"
                ),
                "Due Date": st.column_config.DateColumn(
                    "Due Date",
                    help="Scheduled due date (within current week)",
                    width="small"
                ),
                "Est. Story Points": st.column_config.NumberColumn(
                    "Est. Story Points",
                    help="Estimated effort in story points",
                    format="%d",
                    width="small"
                ),
                "Act. Story Points": st.column_config.NumberColumn(
                    "Act. Story Points",
                    help="Actual effort logged from time tracking and worklogs (8 hours = 1 story point)",
                    format="%.1f",
                    width="small"
                ),
                "Assigned To": st.column_config.TextColumn(
                    "Assigned To",
                    help="Team member assigned to this issue",
                    width="medium"
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    help="Issue summary/title",
                    width="large"
                )
            }
        )
        
        # Export button for current priorities
        csv_data = export_to_csv(current_priorities_df, "current_priorities.csv")
        st.download_button(
            label="📥 Export Current Priorities",
            data=csv_data,
            file_name=f"current_priorities_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Add totals for story points with improved UI
        st.markdown("### 📊 Current Priorities - Story Points Summary")
        col1, col2 = st.columns(2)
        with col1:
            total_estimated = current_priorities_df['Est. Story Points'].sum()
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: #2E86AB;'>📈 Total Est. Story Points</h4>
                <h2 style='margin: 0; color: #2E86AB;'>{total_estimated:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            total_actual = current_priorities_df['Act. Story Points'].sum()
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: #A23B72;'>✅ Total Act. Story Points</h4>
                <h2 style='margin: 0; color: #A23B72;'>{total_actual:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("✅ No issues are both **In Progress** and **due this week** for the selected team members.")
        st.markdown("""
        **This is good news!** It means either:
        - All current week deadlines are being met
        - In Progress items have due dates beyond this week
        - Team is ahead of schedule
        
        *Check the "Up Next" section below for future work items.*
        """)
    
    st.markdown("---")
    
    # Up Next Priorities Section
    st.subheader("⏭️ Up Next (To Do for Future Work)")
    st.markdown("*Issues ready to be worked on (To Do status, not due this week)*")
    
    if not up_next_priorities_df.empty:
        st.info(f"**{len(up_next_priorities_df)} issues** ready for future work")
        
        # Create up next table
        up_next_table_df = create_priority_table(up_next_priorities_df)
        
        # Transform JIRA ID column to contain full URLs for linking
        if not up_next_table_df.empty and 'JIRA ID' in up_next_table_df.columns:
            jira_base_url = st.session_state.config['jira']['JIRA_URL']
            # Create a new column with just the issue keys for display
            up_next_table_df['Issue Key'] = up_next_table_df['JIRA ID'].copy()
            # Transform JIRA ID column to contain full URLs
            up_next_table_df['JIRA ID'] = up_next_table_df['JIRA ID'].apply(
                lambda x: f"{jira_base_url}/browse/{x}" if pd.notna(x) else ""
            )
            # Reorder columns to put Issue Key before JIRA Link
            columns = up_next_table_df.columns.tolist()
            # Remove Issue Key from its current position and insert it before JIRA ID
            columns.remove('Issue Key')
            jira_id_index = columns.index('JIRA ID')
            columns.insert(jira_id_index, 'Issue Key')
            up_next_table_df = up_next_table_df[columns]
        
        # Display as interactive table with same column configuration
        st.dataframe(
            up_next_table_df,
            use_container_width=True,
            height=300,
            column_config={
                "Priority": st.column_config.NumberColumn(
                    "Priority",
                    help="Priority ranking (1 = highest priority)",
                    format="%d",
                    width="small"
                ),
                "Issue Key": st.column_config.TextColumn(
                    "Issue Key",
                    help="JIRA issue identifier",
                    width="medium"
                ),
                "JIRA ID": st.column_config.LinkColumn(
                    "JIRA Link",
                    help="Click to open in JIRA",
                    width="small"
                ),
                "Issue Type": st.column_config.TextColumn(
                    "Issue Type",
                    help="JIRA issue type (e.g., Story, Task, Bug)",
                    width="small"
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Current JIRA status (To Do category)",
                    width="medium"
                ),
                "Start Date": st.column_config.DateColumn(
                    "Start Date",
                    help="Issue creation date",
                    width="small"
                ),
                "Due Date": st.column_config.DateColumn(
                    "Due Date",
                    help="Scheduled due date (future or not set)",
                    width="small"
                ),
                "Est. Story Points": st.column_config.NumberColumn(
                    "Est. Story Points",
                    help="Estimated effort in story points",
                    format="%d",
                    width="small"
                ),
                "Act. Story Points": st.column_config.NumberColumn(
                    "Act. Story Points",
                    help="Actual effort logged from time tracking and worklogs (8 hours = 1 story point)",
                    format="%.1f",
                    width="small"
                ),
                "Assigned To": st.column_config.TextColumn(
                    "Assigned To",
                    help="Team member assigned to this issue",
                    width="medium"
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    help="Issue summary/title",
                    width="large"
                )
            }
        )
        
        # Export button for up next priorities
        csv_data = export_to_csv(up_next_priorities_df, "up_next_priorities.csv")
        st.download_button(
            label="📥 Export Up Next Priorities",
            data=csv_data,
            file_name=f"up_next_priorities_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Add totals for up next story points
        st.markdown("### 📊 Up Next Priorities - Story Points Summary")
        col1, col2 = st.columns(2)
        with col1:
            total_estimated_next = up_next_priorities_df['Est. Story Points'].sum()
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: #2E86AB;'>📈 Total Est. Story Points</h4>
                <h2 style='margin: 0; color: #2E86AB;'>{total_estimated_next:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            total_actual_next = up_next_priorities_df['Act. Story Points'].sum()
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: #A23B72;'>✅ Total Act. Story Points</h4>
                <h2 style='margin: 0; color: #A23B72;'>{total_actual_next:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No future work items (To Do status) found for the selected team members.")
        st.markdown("**Up Next priorities show all issues with 'To Do', 'Open', 'Backlog', or 'Selected for Development' status.**")

def render_last_week_completed_tab(selected_members):
    """Render Last Week Completed tab with filtered issues"""
    st.markdown('<div class="tab-header">📋 Last Week Completed</div>', unsafe_allow_html=True)
    st.markdown("*Issues of type Task, Bug, or Enhancement that were completed last week*")
    
    if not selected_members:
        st.warning("⚠️ Please select at least one team member from the sidebar to view completed issues.")
        return
    
    jira_client = get_jira_client()
    if not jira_client:
        st.error("❌ Failed to connect to JIRA")
        return
    
    # Get last week completed issues
    with st.spinner("Loading last week's completed issues..."):
        completed_df = jira_client.get_last_week_completed(selected_members)
    
    if completed_df.empty:
        st.info("✅ No completed issues found for the selected team members from last week.")
        st.markdown("""
        **This could mean:**
        - No issues were completed during last week
        - All completed issues were of types other than Task, Bug, or Enhancement
        - Selected team members had no completed work last week
        """)
        return
    
    # Display summary metrics
    st.subheader("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='margin: 0; color: #28a745;'>✅ Total Completed</h4>
            <h2 style='margin: 0; color: #28a745;'>{len(completed_df)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        task_count = len(completed_df[completed_df['issue_type'] == 'Task'])
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='margin: 0; color: #007bff;'>📋 Tasks</h4>
            <h2 style='margin: 0; color: #007bff;'>{task_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        bug_count = len(completed_df[completed_df['issue_type'] == 'Bug'])
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='margin: 0; color: #dc3545;'>🐛 Bugs</h4>
            <h2 style='margin: 0; color: #dc3545;'>{bug_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        enhancement_count = len(completed_df[completed_df['issue_type'] == 'Enhancement'])
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='margin: 0; color: #ffc107;'>⚡ Enhancements</h4>
            <h2 style='margin: 0; color: #ffc107;'>{enhancement_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create and display the completed issues table
    st.subheader("📋 Completed Issues Details")
    completed_table_df = create_completed_issues_table(completed_df)
    
    if not completed_table_df.empty:
        # Transform JIRA ID column to contain full URLs for linking
        jira_base_url = st.session_state.config['jira']['JIRA_URL']
        # Create a new column with just the issue keys for display
        completed_table_df['Issue Key'] = completed_table_df['JIRA ID'].copy()
        # Transform JIRA ID column to contain full URLs
        completed_table_df['JIRA ID'] = completed_table_df['JIRA ID'].apply(
            lambda x: f"{jira_base_url}/browse/{x}" if pd.notna(x) else ""
        )
        # Reorder columns to put Issue Key before JIRA Link
        columns = completed_table_df.columns.tolist()
        # Remove Issue Key from its current position and insert it at the beginning
        columns.remove('Issue Key')
        columns.insert(0, 'Issue Key')
        completed_table_df = completed_table_df[columns]
        
        # Display as interactive table
        st.dataframe(
            completed_table_df,
            use_container_width=True,
            height=400,
            column_config={
                "Issue Key": st.column_config.TextColumn(
                    "Issue Key",
                    help="JIRA issue identifier",
                    width="medium"
                ),
                "JIRA ID": st.column_config.LinkColumn(
                    "JIRA Link",
                    help="Click to open in JIRA",
                    width="small"
                ),
                "Issue Type": st.column_config.TextColumn(
                    "Issue Type",
                    help="Type of JIRA issue",
                    width="small"
                ),
                "Summary": st.column_config.TextColumn(
                    "Summary",
                    help="Issue description/title",
                    width="large"
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Current status (should be Done)",
                    width="small"
                ),
                "Assigned To": st.column_config.TextColumn(
                    "Assigned To",
                    help="Team member who completed the issue",
                    width="medium"
                ),
                "Completed Date": st.column_config.DateColumn(
                    "Completed Date",
                    help="Date when the issue was completed",
                    width="medium"
                ),
                "Created Date": st.column_config.DateColumn(
                    "Created Date",
                    help="Date when the issue was created",
                    width="medium"
                ),
                "Est. Story Points": st.column_config.NumberColumn(
                    "Est. Story Points",
                    help="Estimated effort in story points",
                    format="%.1f",
                    width="small"
                ),
                "Act. Story Points": st.column_config.NumberColumn(
                    "Act. Story Points",
                    help="Actual effort logged from time tracking and worklogs (8 hours = 1 story point)",
                    format="%.1f",
                    width="small"
                )
            }
        )
        
        # Export button
        csv_data = export_to_csv(completed_df, "last_week_completed.csv")
        st.download_button(
            label="📥 Export Completed Issues",
            data=csv_data,
            file_name=f"last_week_completed_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Story points summary - matching Priority Dashboard format
        st.markdown("### 📊 Story Points Summary")
        col1, col2 = st.columns(2)
        with col1:
            total_estimated = completed_df.get('story_points', pd.Series(dtype='float64')).fillna(0).sum()
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: #2E86AB;'>📈 Total Est. Story Points</h4>
                <h2 style='margin: 0; color: #2E86AB;'>{total_estimated:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            total_actual = completed_df.get('actual_story_points', pd.Series(dtype='float64')).fillna(0).sum()
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='margin: 0; color: #A23B72;'>✅ Total Act. Story Points</h4>
                <h2 style='margin: 0; color: #A23B72;'>{total_actual:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("❌ Unable to format completed issues data for display")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Initialize JIRA client early to catch connection issues
    jira_client = get_jira_client()
    
    render_header()
    
    # Show connection status
    if jira_client is None:
        st.error("❌ Failed to connect to JIRA. Please check your configuration in config.py")
        st.info("📝 Make sure your JIRA URL, username, and API token are correct.")
        return
    else:
        st.success("✅ Connected to JIRA successfully!")
    
    # Render global sidebar once and get selected team members
    selected_members = render_global_sidebar()
    
    # Navigation tabs - added "Last Week Completed" tab
    tab1, tab2, tab3 = st.tabs(["📊 Weekly Activity", "🎯 Priority Dashboard", "📋 Last Week Completed"])
    
    with tab1:
        show_weekly_activity(selected_members)
    
    with tab2:
        render_priority_dashboard_tab(selected_members)
    
    with tab3:
        render_last_week_completed_tab(selected_members)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #7f8c8d; font-size: 0.9rem; padding: 1rem;">
            JIRA Daily Activity & Priority Dashboard | 
            <a href="https://spreetail.atlassian.net" target="_blank">Open JIRA</a> | 
            Data refreshes every 5 minutes | Global team filter applies to all tabs
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 