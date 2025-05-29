# JIRA Daily Activity & Priority Dashboard

A comprehensive Streamlit dashboard for visualizing JIRA issues, team activity, and priorities.

## Features

- **📊 Weekly Activity**: View team issue activity with customizable time periods and filters
- **🎯 Priority Dashboard**: Current priorities and upcoming work with smart filtering
- **📋 Last Week Completed**: Track completed work from the previous week
- **👥 Global Team Filtering**: Filter data across all tabs by team members
- **📈 Interactive Charts**: Visual analytics for status distribution, issue types, and timelines
- **🔗 JIRA Integration**: Clickable links to open issues directly in JIRA
- **⚡ Real-time Data**: Cached data with manual refresh options

## Live Demo

🚀 **[View Live Dashboard](https://your-app-name.streamlit.app)** (Update this link after deployment)

## Quick Start (Local Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/waseyt310/Jira_Summary_Viewer.git
   cd Jira_Summary_Viewer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export JIRA_URL="https://your-domain.atlassian.net"
   export JIRA_USERNAME="your-email@domain.com"
   export JIRA_API_TOKEN="your-api-token"
   ```

4. **Run the dashboard**
   ```bash
   streamlit run main.py
   ```

## Deployment to Streamlit Cloud

### Prerequisites

1. **JIRA API Token**: 
   - Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Give it a label (e.g., "Streamlit Dashboard")
   - Copy the generated token

2. **GitHub Repository**: Fork or clone this repository to your GitHub account

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub account
   - Select repository: `your-username/Jira_Summary_Viewer`
   - Set main file path: `main.py`
   - Click "Deploy"

3. **Configure Secrets**
   - In your Streamlit Cloud app, go to "Settings" → "Secrets"
   - Copy the content from `secrets.toml.template`
   - Replace the placeholder values with your actual JIRA credentials:
   ```toml
   [jira]
   JIRA_URL = "https://your-domain.atlassian.net"
   JIRA_USERNAME = "your-email@domain.com"
   JIRA_API_TOKEN = "your-actual-api-token"
   ```
   - Save the secrets

4. **Update Team Configuration** (Optional)
   - Edit `config.py` to update the `TEAM_MEMBERS` dictionary with your team's information
   - Commit and push changes to trigger redeployment

## Configuration

### Team Members
Edit the `TEAM_MEMBERS` dictionary in `config.py` to match your team:

```python
TEAM_MEMBERS = {
    "John Doe": "john.doe@company.com",
    "Jane Smith": "jane.smith@company.com",
    # Add your team members here
}
```

### JIRA Filters
The dashboard uses intelligent JQL queries to filter issues:

- **Current Priorities**: Issues with "Development" status
- **Up Next**: Issues with "To Do", "Open", "Backlog", or "Selected for Development" status  
- **Weekly Activity**: Issues updated or created in the selected time period
- **Completed**: Issues with "Done" status from last week

## Project Structure

```
├── main.py                    # Main Streamlit application
├── jira_client.py            # JIRA API client and data fetching
├── utils.py                  # Utility functions for data processing
├── config.py                 # Configuration and credentials management
├── requirements.txt          # Python dependencies
├── secrets.toml.template     # Template for Streamlit Cloud secrets
├── .gitignore               # Git ignore file
├── archived_files/          # Archived development files
└── README.md               # This file
```

## Dependencies

- `streamlit>=1.28.0` - Web framework
- `pandas>=2.0.0` - Data manipulation  
- `plotly>=5.15.0` - Interactive charts
- `jira>=3.5.0` - JIRA API client
- `python-dateutil>=2.8.2` - Date utilities
- `requests>=2.31.0` - HTTP requests
- `pytz>=2023.3` - Timezone handling

## Security Notes

- ✅ **Credentials are secure**: Uses Streamlit Cloud secrets management
- ✅ **No hardcoded tokens**: All sensitive data is externalized
- ✅ **Git-safe**: `.gitignore` prevents accidental credential commits
- ✅ **Environment fallback**: Works with environment variables for local development

## Troubleshooting

### Common Issues

1. **"Failed to connect to JIRA"**
   - Verify your JIRA URL, username, and API token in Streamlit Cloud secrets
   - Ensure the API token has proper permissions

2. **"No team members selected"**
   - Update the `TEAM_MEMBERS` configuration to match your JIRA users
   - Ensure email addresses match exactly with JIRA user accounts

3. **"No issues found"**
   - Check if the team members have issues assigned in JIRA
   - Verify the date range covers periods with activity

### Support

If you encounter issues:
1. Check the Streamlit Cloud logs for error details
2. Verify your JIRA credentials and permissions
3. Ensure team member email addresses match JIRA users exactly

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- JIRA integration via [jira-python](https://jira.readthedocs.io/)
- Charts powered by [Plotly](https://plotly.com) 