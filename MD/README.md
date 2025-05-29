# JIRA Daily Activity & Priority Dashboard

A comprehensive Streamlit application for tracking daily JIRA activity and managing priorities. This dashboard provides real-time insights into JIRA issue progress, team workload, and priority management.

## 🚀 Features

### 📊 Weekly JIRA Issue Activity
- **Real-time Data**: View JIRA issues updated or created in the last 7-30 days
- **Smart Filtering**: Filter by status (All, Completed, In Progress, Blocked) and assignee
- **Visual Analytics**: 
  - Status distribution pie charts
  - Issue type distribution
  - Daily activity timeline
  - Assignee workload analysis
- **Summary Metrics**: Total issues, completion rates, blocked issues
- **Export Capability**: Download filtered data as CSV

### 🎯 Priority Dashboard
- **Current Priorities**: Issues requiring immediate attention (labeled as 'priority')
- **Up Next**: Queued issues for upcoming work (labeled as 'up-next')
- **Priority Cards**: Rich cards showing issue details, status, assignee, and due dates
- **Priority Metrics**: Summary statistics for priority management

### 👤 My Issues
- **Personal View**: Issues assigned to the current user
- **Status Tracking**: Filter personal issues by status
- **Workload Management**: Visual metrics for personal productivity

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Access to JIRA Cloud instance
- JIRA API token

### Setup Instructions

1. **Clone or Download the Project**
   ```bash
   # Create project directory
   mkdir jira-dashboard
   cd jira-dashboard
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure JIRA Connection**
   
   Edit `config.py` to update your JIRA credentials:
   ```python
   JIRA_CONFIG = {
       "JIRA_URL": "https://your-domain.atlassian.net",
       "JIRA_USERNAME": "your-email@domain.com",
       "JIRA_API_TOKEN": "your-api-token"
   }
   ```

4. **Run the Application**
   ```bash
   streamlit run main.py
   ```

5. **Access Dashboard**
   - Open your browser to `http://localhost:8501`
   - The dashboard will automatically connect to JIRA and load data

## 🔧 Configuration

### JIRA API Token Setup

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Copy the token and update `config.py`

### Customizing Priority Identification

The dashboard identifies priorities using JIRA labels by default:
- **Current Priorities**: Issues with `priority` label
- **Up Next Priorities**: Issues with `up-next` label

To customize this behavior, modify the JQL queries in `config.py`:

```python
JQL_QUERIES = {
    # Example: Use custom fields instead of labels
    "CURRENT_PRIORITIES": "cf[10100] = 'High' AND status != 'Done' ORDER BY priority DESC",
    "UP_NEXT_PRIORITIES": "cf[10100] = 'Medium' AND status != 'Done' ORDER BY priority DESC",
}
```

### Status and Color Customization

Customize status colors and issue type icons in `config.py`:

```python
STATUS_COLORS = {
    "To Do": "#6c757d",
    "In Progress": "#007bff",
    "Done": "#28a745",
    # Add your custom statuses
}

ISSUE_TYPE_ICONS = {
    "Task": "📋",
    "Bug": "🐛",
    "Story": "📖",
    # Add your custom issue types
}
```

## 📁 Project Structure

```
jira-dashboard/
├── main.py              # Main Streamlit application
├── config.py            # Configuration settings
├── jira_client.py       # JIRA API client
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔄 Data Refresh

- **Automatic Caching**: Data is cached for 5 minutes to improve performance
- **Manual Refresh**: Use the "🔄 Refresh Data" button to force data reload
- **Real-time Updates**: Data reflects the most recent JIRA state

## 📊 Dashboard Tabs

### 1. Weekly Activity Tab

Track JIRA issues updated in the last 7-30 days with comprehensive filtering and analytics:

**Team Member Filtering:**
- **Multi-select dropdown** to choose specific team members
- Pre-configured team includes: Waseyt Ibrahim, Donn Mailing, Edu Cielo, Mohammad Asim, Ryan Kieselhorst, Shawn Parry
- Filter by individual team members or view all team activity
- Real-time issue count updates based on selection

**Features:**
- **Time Period Selection**: 7, 14, 21, or 30 days lookback
- **Status Filtering**: All, In Progress, Completed, or Blocked issues
- **Team Metrics**: Total issues, completion rates, average issues per member, story points
- **Visual Analytics**: 
  - Status distribution pie chart
  - Issue type distribution
  - Daily activity timeline
  - Team member workload comparison
- **Interactive Data Table**: Sortable, searchable issue list with JIRA links
- **CSV Export**: Download filtered results for external analysis

### 2. Priority Dashboard Tab
- **Purpose**: Manage current and upcoming priorities
- **Sections**: Current priorities, up-next priorities, summary metrics
- **Display**: Rich cards with issue details and status badges

### 3. My Issues Tab
- **Purpose**: Personal issue tracking
- **Features**: Assigned issues, status filtering, personal metrics
- **Export**: Personal issue CSV export

## 🎨 Visual Features

- **Modern UI**: Clean, professional interface with custom CSS
- **Color-coded Status**: Visual status indicators
- **Interactive Charts**: Plotly-powered visualizations
- **Responsive Design**: Works on desktop and mobile
- **Rich Cards**: Detailed issue information cards

## 🚀 Advanced Usage

### Custom JQL Queries

You can extend the dashboard with custom JQL queries:

```python
# In jira_client.py, use the search_issues_custom method
custom_df = jira_client.search_issues_custom(
    "project = 'PROJ' AND assignee = currentUser() AND created >= -1w"
)
```

### Adding New Metrics

Extend the `utils.py` file to add custom metrics:

```python
def get_velocity_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate team velocity metrics"""
    # Your custom metric calculations
    return metrics
```

### Custom Visualizations

Add new chart types using Plotly:

```python
def create_burndown_chart(df: pd.DataFrame) -> go.Figure:
    """Create sprint burndown chart"""
    # Your custom chart implementation
    return fig
```

## 🔧 Troubleshooting

### Common Issues

1. **JIRA Connection Failed**
   - Verify JIRA URL, username, and API token
   - Check network connectivity
   - Ensure API token has proper permissions

2. **No Data Displayed**
   - Check JQL queries in config.py
   - Verify project access permissions
   - Review JIRA field configurations

3. **Performance Issues**
   - Reduce date range for large datasets
   - Adjust cache TTL in `@st.cache_data` decorators
   - Optimize JQL queries

### Logging

The application includes comprehensive logging. Check the console output for detailed error messages and debugging information.

## 📈 Performance Optimization

- **Data Caching**: 5-minute cache for API calls
- **Efficient Queries**: Optimized JQL for faster retrieval
- **Lazy Loading**: Data loaded only when needed
- **Pagination**: Large datasets handled efficiently

## 🔒 Security

- **API Token**: Use JIRA API tokens instead of passwords
- **Read-Only**: Dashboard is read-only by default
- **Local Storage**: No sensitive data stored locally

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 💬 Support

For support and questions:
- Check the troubleshooting section
- Review JIRA API documentation
- Open an issue for bugs or feature requests

## 🔄 Updates

### Version 1.0.0
- Initial release with weekly activity and priority dashboard
- Full JIRA integration with caching
- Modern UI with custom styling
- Export capabilities
- Responsive design

---

**Happy JIRA tracking! 📊🎯** 