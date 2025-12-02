# Dependabot Alerts Checker

This repository includes a GitHub Action workflow and Python script to check Dependabot alerts across all repositories owned by a GitHub user or organization.

## Features

- 🔍 Scans all repositories for open Dependabot alerts
- 📊 Provides a summary of alerts by severity (Critical, High, Medium, Low)
- 🤖 Can be run automatically on a schedule or manually triggered
- 📦 Easy to use and understand output

## How It Works

The solution consists of two main components:

### 1. GitHub Action Workflow (`.github/workflows/check-dependabot-alerts.yml`)

This workflow:
- Runs daily at 9 AM UTC (configurable via cron schedule)
- Can be manually triggered via workflow_dispatch
- Uses the repository's GITHUB_TOKEN to authenticate
- Scans all repositories owned by the repository owner

### 2. Python Script (`scripts/check_dependabot_alerts.py`)

This script:
- Fetches all repositories for the specified owner
- Checks each repository for open Dependabot alerts
- Displays alerts with severity levels, package names, and CVE information
- Provides a summary of total alerts by severity

## Usage

### Running the Workflow Manually

1. Go to the **Actions** tab in your repository
2. Select **Check Dependabot Alerts** workflow
3. Click **Run workflow**
4. Select the branch and click **Run workflow**

### Running the Script Locally

You can also run the script locally if you have a GitHub personal access token:

```bash
# Install dependencies
pip install requests

# Set environment variables
export GITHUB_TOKEN=your_personal_access_token
export GITHUB_OWNER=Proce2

# Run the script
python scripts/check_dependabot_alerts.py
```

**Note:** Your GitHub token needs the following permissions:
- `repo` scope for private repositories
- `security_events` scope for reading security alerts

### Creating a Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **Generate new token (classic)**
3. Give it a descriptive name
4. Select these scopes:
   - `repo` (Full control of private repositories)
   - `security_events` (Read and write security events)
5. Click **Generate token**
6. Copy the token and use it as `GITHUB_TOKEN`

## Output Example

```
🔍 Checking Dependabot alerts for all repositories owned by Proce2

================================================================================

Found 8 repositories

📦 Repository: Proce2/android-App
   URL: https://github.com/Proce2/android-App
   Alerts: 3 open
   ----------------------------------------------------------------------
   🔴 CRITICAL
   Package: example-vulnerable-package
   Summary: Critical vulnerability in example package
   CVE: CVE-2024-1234
   Details: https://github.com/Proce2/android-App/security/dependabot/1

================================================================================
📊 SUMMARY
================================================================================
Total repositories scanned: 8
Repositories with alerts: 2
Total open alerts: 5

Alerts by severity:
  🔴 Critical: 2
  🟠 High: 2
  🟡 Medium: 1

⚠️  Please review and address these security alerts!
```

## Customization

### Change Schedule

Edit the cron schedule in `.github/workflows/check-dependabot-alerts.yml`:

```yaml
schedule:
  # Run daily at 9 AM UTC
  - cron: '0 9 * * *'
```

### Filter Alert States

By default, the script only checks for `open` alerts. You can modify the script to include other states like `dismissed` or `fixed` by editing the `params` in the `get_dependabot_alerts` function:

```python
params = {"state": "all", "per_page": 100}  # Check all states
```

## Permissions

The workflow requires the following permissions in the GitHub Action:

```yaml
permissions:
  contents: read
  security-events: read
```

These are automatically provided by the `GITHUB_TOKEN` in GitHub Actions.

## Troubleshooting

### 403 Forbidden Error

If you get a 403 error, it means:
- Dependabot is not enabled on that repository, or
- Your token doesn't have the required permissions, or
- The repository doesn't have Dependabot alerts enabled

To enable Dependabot:
1. Go to repository Settings → Security → Code security and analysis
2. Enable **Dependabot alerts**

### No Alerts Found

If no alerts are found, that's great! It means either:
- Your dependencies are up to date and secure, or
- Dependabot hasn't been enabled on your repositories

## License

This is free and unencumbered software released into the public domain.
