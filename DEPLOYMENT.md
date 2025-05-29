# Deployment Guide for JIRA Dashboard

## Quick Deployment Checklist

### 1. Prepare for GitHub Upload
- [x] Remove hardcoded credentials from config.py
- [x] Create .gitignore to exclude sensitive files  
- [x] Create secrets template
- [x] Update README with deployment instructions

### 2. Upload to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Check what will be committed (make sure no secrets are included)
git status

# Commit files
git commit -m "Prepare JIRA Dashboard for Streamlit Cloud deployment"

# Add your GitHub repository as remote
git remote add origin https://github.com/waseyt310/Jira_Summary_Viewer.git

# Push to GitHub
git push -u origin main
```

### 3. Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Repository: `waseyt310/Jira_Summary_Viewer`
   - Branch: `main`
   - Main file path: `main.py`
   - App URL: Choose a custom name (e.g., `jira-dashboard-spreetail`)

3. **Configure Secrets**
   - Go to your app settings → "Secrets"
   - Copy and paste this template with YOUR actual values:

```toml
[jira]
JIRA_URL = "https://your-domain.atlassian.net"
JIRA_USERNAME = "your-email@company.com"
JIRA_API_TOKEN = "your-actual-jira-api-token-here"
```

**⚠️ Important:** Replace the placeholder values above with your actual JIRA credentials:
- `JIRA_URL`: Your actual JIRA domain (e.g., "https://spreetail.atlassian.net")
- `JIRA_USERNAME`: Your actual email address
- `JIRA_API_TOKEN`: Your actual JIRA API token

4. **Deploy**
   - Click "Deploy" button
   - Wait for deployment to complete (usually 2-3 minutes)

### 4. Post-Deployment

1. **Test the App**
   - Click on your app URL
   - Verify JIRA connection works
   - Test all three tabs
   - Verify team member filtering

2. **Update README**
   - Replace the demo link in README.md with your actual app URL
   - Commit and push the change

## Security Notes

### ✅ What's Secure Now:
- Credentials are stored in Streamlit Cloud secrets (encrypted)
- No hardcoded tokens in the code
- .gitignore prevents accidental credential commits
- Config dynamically loads from secrets/environment

### ⚠️ Important Security Tips:
- Never commit secrets.toml to version control
- Use the Streamlit Cloud secrets interface only
- Regularly rotate your JIRA API tokens
- Monitor app access logs

## Troubleshooting

### Common Deployment Issues:

1. **"Failed to connect to JIRA"**
   ```
   Solution: Check your secrets configuration
   - Verify JIRA_URL format: https://domain.atlassian.net
   - Verify JIRA_USERNAME is correct email
   - Verify JIRA_API_TOKEN is valid and has permissions
   ```

2. **"No module named 'xxx'"**
   ```
   Solution: Check requirements.txt
   - Ensure all dependencies are listed
   - Check for version compatibility
   ```

3. **"Secrets not found"**
   ```
   Solution: Verify secrets configuration
   - Go to app settings → Secrets
   - Ensure proper TOML format
   - Check for typos in key names
   ```

4. **App won't start**
   ```
   Solution: Check logs
   - Go to app logs in Streamlit Cloud
   - Look for Python errors
   - Verify main.py is the correct entry point
   ```

## Team Configuration

After deployment, you may want to update team members:

1. Edit `config.py` in your repository
2. Update the `TEAM_MEMBERS` dictionary:
   ```python
   TEAM_MEMBERS = {
       "Your Name": "your.email@company.com",
       "Teammate": "teammate@company.com",
       # Add more team members
   }
   ```
3. Commit and push to trigger redeployment

## Monitoring

- **App URL**: Your Streamlit Cloud app URL
- **GitHub Repository**: https://github.com/waseyt310/Jira_Summary_Viewer
- **Logs**: Available in Streamlit Cloud dashboard
- **Usage**: Monitor through Streamlit Cloud analytics

## Next Steps

1. Share the app URL with your team
2. Set up regular JIRA API token rotation
3. Consider adding more features or customizations
4. Monitor usage and performance

---

**Need Help?** 
- Check Streamlit Cloud documentation: https://docs.streamlit.io/streamlit-community-cloud
- Review app logs for specific error messages
- Verify JIRA API token permissions 