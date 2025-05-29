# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Configuration
Edit `config.py` with your JIRA details:
```python
JIRA_CONFIG = {
    "JIRA_URL": "https://spreetail.atlassian.net",
    "JIRA_USERNAME": "waseyt.ibrahim@spreetail.com", 
    "JIRA_API_TOKEN": "YOUR_API_TOKEN_HERE"
}
```

### 3. Run the Application
```bash
streamlit run main.py
```

### 4. Access Dashboard
Open your browser to: http://localhost:8501

## 📊 What You'll See

### Tab 1: Weekly Activity 📊
- **Default View**: Issues updated in the last 7 days
- **Filters**: Adjust date range (1-30 days), filter by status, assignee
- **Charts**: Status distribution, issue types, activity timeline
- **Export**: Download data as CSV

### Tab 2: Priority Dashboard 🎯
- **Current Priorities**: Issues with `priority` label
- **Up Next**: Issues with `up-next` label
- **Priority Cards**: Rich issue details with status badges

### Tab 3: My Issues 👤
- **Personal View**: Your assigned issues
- **Filters**: Filter by status
- **Metrics**: Personal productivity summary

## 🏷️ Setting Up Priority Labels

To see data in the Priority Dashboard:

1. **In JIRA**: Go to any issue
2. **Add Labels**: 
   - Add `priority` label for current priorities
   - Add `up-next` label for upcoming priorities
3. **Refresh Dashboard**: Click "🔄 Refresh Data"

## 🎨 Key Features

✅ **Real-time Data**: 5-minute cache, manual refresh available  
✅ **Visual Analytics**: Interactive charts and graphs  
✅ **Filtering**: Status, assignee, date range filters  
✅ **Export**: CSV download for all views  
✅ **Responsive**: Works on desktop and mobile  
✅ **Secure**: Read-only JIRA access  

## 🔧 Troubleshooting

### Can't Connect to JIRA?
1. Verify JIRA URL is correct
2. Check API token permissions
3. Ensure network connectivity

### No Issues Showing?
1. Check date range filter
2. Verify project access permissions
3. Try expanding date range to 30 days

### Priority Dashboard Empty?
1. Add `priority` and `up-next` labels to JIRA issues
2. Or modify JQL queries in `config.py`

## 🚀 Next Steps

1. **Customize**: Edit `config.py` for your team's needs
2. **Extend**: Add custom JQL queries and metrics
3. **Share**: Deploy to cloud for team access

---

**Ready to track your JIRA activity! 📊** 