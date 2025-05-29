# 🚀 JIRA Dashboard - New Device Setup Guide

## 📋 **Prerequisites**

### Required Software
1. **Python 3.8+** - [Download from python.org](https://www.python.org/downloads/)
2. **pip** - Usually comes with Python
3. **Internet connection** - For JIRA API access

### Verify Installation
```bash
python --version    # Should show 3.8 or higher
pip --version       # Should show pip version
```

## 📁 **Step 1: Transfer Project Files**

### Option A: Copy Project Folder
1. Copy the entire `JIRA View daily` folder to the new device
2. Place it in a convenient location (e.g., Desktop, Documents)

### Option B: Manual File Transfer
Transfer these essential files:
```
📁 New Project Folder/
├── main.py
├── jira_client.py  
├── utils.py
├── config.py                 # ⚠️ CRITICAL - Contains JIRA credentials
├── requirements.txt
├── run_dashboard.bat         # For Windows
└── README.md
```

## 🔧 **Step 2: Install Dependencies**

### Windows
```cmd
# Navigate to project folder
cd "path\to\JIRA View daily"

# Install dependencies
pip install -r requirements.txt
```

### macOS/Linux
```bash
# Navigate to project folder
cd "path/to/JIRA View daily"

# Install dependencies
pip install -r requirements.txt

# Or use pip3 if needed
pip3 install -r requirements.txt
```

### Alternative: Manual Installation
If requirements.txt is missing, install manually:
```bash
pip install streamlit>=1.28.0
pip install pandas>=2.0.0
pip install plotly>=5.15.0
pip install jira>=3.5.0
pip install python-dateutil>=2.8.2
pip install requests>=2.31.0
```

## ⚙️ **Step 3: Configuration**

### JIRA Credentials (CRITICAL)
The `config.py` file contains your JIRA credentials. **This is already configured** with:
- JIRA URL: https://spreetail.atlassian.net
- Username: waseyt.ibrahim@spreetail.com
- API Token: [Your existing token]
- Team Members: All 6 team members pre-configured

**⚠️ No changes needed** - the configuration will work on any device!

### Network Access
Ensure the new device can access:
- `https://spreetail.atlassian.net` (JIRA instance)
- Internet connection for API calls

## 🚀 **Step 4: Run the Application**

### Windows
```cmd
# Option 1: Use the batch file (easiest)
double-click run_dashboard.bat

# Option 2: Command line
python -m streamlit run main.py --server.port 8504
```

### macOS/Linux
```bash
# Create a startup script (optional)
echo '#!/bin/bash' > run_dashboard.sh
echo 'python -m streamlit run main.py --server.port 8504' >> run_dashboard.sh
chmod +x run_dashboard.sh
./run_dashboard.sh

# Or run directly
python -m streamlit run main.py --server.port 8504
```

## 🌐 **Step 5: Access Dashboard**

1. **Automatic**: Browser should open automatically
2. **Manual**: Go to `http://localhost:8504`
3. **Network Access**: Use `http://[device-ip]:8504` for other devices on same network

## 🎯 **New Priority Dashboard Features**

### **Updated Priority Dashboard**
- **Table Format**: Professional table layout similar to project management tools
- **Real Priority Data**: Shows actual JIRA issues based on priority fields
- **Current Priorities**: High and Highest priority issues
- **Up Next**: Medium priority issues  
- **Interactive Features**: Clickable JIRA links, CSV export, summary metrics

### **Expected Data**
- **Current Priorities**: Issues with 'High' or 'Highest' priority
- **Up Next**: Issues with 'Medium' priority
- **Table Columns**: Priority ranking, Project, JIRA ID, Status, Dates, Story Points, Assignee

## 🔍 **Step 6: Verify Everything Works**

### Quick Test
```bash
# Test JIRA connection
python test_connection.py

# Check application status
python check_status.py
```

### Expected Results
- ✅ JIRA connection successful
- ✅ Team member filtering working
- ✅ Data loading (71+ issues for team)
- ✅ All 3 tabs functional

## 🛠️ **Troubleshooting**

### Common Issues & Solutions

#### 1. "streamlit not found"
```bash
# Solution: Install streamlit
pip install streamlit
```

#### 2. "Module not found" errors
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

#### 3. "JIRA connection failed"
- Check internet connection
- Verify firewall/proxy settings
- Ensure access to spreetail.atlassian.net

#### 4. "Port already in use"
```bash
# Solution: Use different port
python -m streamlit run main.py --server.port 8505
```

#### 5. No data showing
- Wait for initial data load (can take 30-60 seconds)
- Check JIRA permissions
- Verify team member email addresses

## 📱 **Platform-Specific Notes**

### Windows
- Use `run_dashboard.bat` for easy startup
- May need to allow Python through Windows Firewall
- Use Command Prompt or PowerShell

### macOS
- May need to install Python via Homebrew
- Use Terminal for commands
- Create `.command` file for easy startup

### Linux
- Use package manager for Python installation
- May need `python3` instead of `python`
- Create shell script for startup

## 🔒 **Security Considerations**

### API Token Security
- The API token is embedded in `config.py`
- Keep this file secure and don't share publicly
- Token provides read-only access to JIRA

### Network Security
- Dashboard runs on localhost by default
- To allow network access, use: `--server.address 0.0.0.0`
- Consider firewall rules for network access

## 📊 **Expected Performance**

### System Requirements
- **RAM**: 512MB minimum, 1GB recommended
- **CPU**: Any modern processor
- **Storage**: 100MB for application + dependencies
- **Network**: Stable internet for JIRA API calls

### Data Loading Times
- Initial load: 30-60 seconds
- Subsequent loads: 5-10 seconds (cached)
- Team filtering: Instant (real-time)

## ✅ **Success Checklist**

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Project files transferred
- [ ] Application starts without errors
- [ ] JIRA connection successful
- [ ] Team member filtering works
- [ ] All 3 tabs load properly
- [ ] Data exports work

## 🆘 **Getting Help**

### If You Get Stuck
1. Check the error messages in terminal/command prompt
2. Verify all files are present
3. Ensure internet connectivity
4. Try running `python test_connection.py`
5. Check the troubleshooting section above

### Log Files
- Application logs appear in the terminal
- Look for "INFO", "WARNING", or "ERROR" messages
- JIRA connection status is clearly indicated

---

**🎉 Once setup is complete, you'll have the full JIRA Dashboard with team filtering running on the new device!** 