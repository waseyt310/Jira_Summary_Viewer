# Team Member Filtering Update

## Overview
Updated the Weekly Activity tab to include team member filtering functionality as requested. The tab now filters JIRA issues specifically for the configured team members with an easy-to-use selection interface.

## Changes Made

### 1. Configuration Updates (`config.py`)
- Added `TEAM_MEMBERS` configuration with the 6 specified team members:
  - Waseyt Ibrahim (waseyt.ibrahim@spreetail.com)
  - Donn Mailing (donn.mailing@spreetail.com)
  - Edu Cielo (edu.cielo@spreetail.com)
  - Mohammad Asim (mohammad.asim@spreetail.com)
  - Ryan Kieselhorst (ryan.kieselhorst@spreetail.com)
  - Shawn Parry (shawn.parry@spreetail.com)

### 2. JIRA Client Updates (`jira_client.py`)
- Added new method `get_team_weekly_activity()` that filters issues by selected team members
- Builds dynamic JQL queries based on team member email addresses
- Maintains existing caching for performance

### 3. UI Enhancements (`main.py`)
- **Multi-select dropdown** in sidebar for team member selection
- **All team members selected by default** for immediate visibility
- **Real-time filtering** - issues update based on selection
- **Team-specific metrics** including average issues per member
- **Enhanced workload chart** showing team member distribution with proper name mapping

### 4. Utility Functions (`utils.py`)
- Added `create_team_workload_chart()` for better team member visualization
- Added `filter_dataframe_by_team_members()` for consistent filtering
- Enhanced name mapping from email addresses to display names

## Features

### Team Member Selection
- **Multi-select interface**: Choose one or more team members
- **Default selection**: All team members selected initially
- **Dynamic updates**: Issue counts and charts update in real-time
- **Clear feedback**: Shows selected team members and issue counts

### Enhanced Analytics
- **Team metrics**: Average issues per member, total story points
- **Team workload chart**: Visual comparison of issue distribution
- **Filtered visualizations**: All charts respect team member selection
- **Export functionality**: CSV exports include only selected team data

### User Experience
- **Intuitive interface**: Clear labels and helpful tooltips
- **Performance optimized**: Caching prevents unnecessary API calls
- **Responsive design**: Works well on different screen sizes
- **Error handling**: Graceful handling of missing data or API issues

## Testing Results

The functionality has been tested and verified:
- ✅ **Connection test**: Successfully connects to JIRA
- ✅ **Team filtering**: Correctly filters by selected team members
- ✅ **Data retrieval**: Retrieved 72 issues for all team members, 25 for selected subset
- ✅ **Metrics calculation**: Proper calculation of team-specific metrics
- ✅ **Chart generation**: Team workload charts display correctly

## Usage Instructions

1. **Launch the application**: `streamlit run main.py`
2. **Navigate to Weekly Activity tab**
3. **Use the sidebar filters**:
   - Select desired team members from the multi-select dropdown
   - Choose time period (7, 14, 21, or 30 days)
   - Apply status filters if needed
4. **View results**:
   - Summary metrics show team-specific data
   - Charts update to reflect selected team members
   - Issue table shows only relevant issues
5. **Export data**: Use the CSV export button for external analysis

## Benefits

- **Focused visibility**: See only relevant team member activity
- **Flexible filtering**: Choose any combination of team members
- **Better insights**: Team-specific metrics and comparisons
- **Improved workflow**: Faster access to relevant information
- **Maintained performance**: Efficient caching and optimized queries 