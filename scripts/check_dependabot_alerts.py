#!/usr/bin/env python3
"""
Script to check Dependabot alerts across all repositories for a GitHub user/organization.
"""

import os
import sys
import requests
from typing import List, Dict, Any


def get_repositories(owner: str, token: str) -> List[Dict[str, Any]]:
    """Fetch all repositories for the given owner."""
    repos = []
    page = 1
    per_page = 100
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    while True:
        url = f"https://api.github.com/users/{owner}/repos"
        params = {"page": page, "per_page": per_page, "type": "all"}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}")
            print(f"Response: {response.text}")
            break
        
        batch = response.json()
        if not batch:
            break
            
        repos.extend(batch)
        page += 1
    
    return repos


def get_dependabot_alerts(owner: str, repo: str, token: str) -> List[Dict[str, Any]]:
    """Fetch Dependabot alerts for a specific repository."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    url = f"https://api.github.com/repos/{owner}/{repo}/dependabot/alerts"
    params = {"state": "open", "per_page": 100}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 404:
        # Dependabot not enabled or no access
        return []
    elif response.status_code == 403:
        # Access forbidden
        return []
    elif response.status_code != 200:
        print(f"  Error fetching alerts for {repo}: {response.status_code}")
        return []
    
    return response.json()


def format_severity_badge(severity: str) -> str:
    """Format severity with emoji badge."""
    badges = {
        "critical": "🔴 CRITICAL",
        "high": "🟠 HIGH",
        "medium": "🟡 MEDIUM",
        "low": "🟢 LOW"
    }
    return badges.get(severity.lower(), severity.upper())


def main():
    token = os.environ.get("GITHUB_TOKEN")
    owner = os.environ.get("GITHUB_OWNER")
    
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    if not owner:
        print("Error: GITHUB_OWNER environment variable not set")
        sys.exit(1)
    
    print(f"🔍 Checking Dependabot alerts for all repositories owned by {owner}\n")
    print("=" * 80)
    
    # Fetch all repositories
    repos = get_repositories(owner, token)
    
    if not repos:
        print(f"No repositories found for {owner}")
        sys.exit(0)
    
    print(f"\nFound {len(repos)} repositories\n")
    
    # Track statistics
    total_alerts = 0
    repos_with_alerts = 0
    severity_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    # Check each repository for alerts
    for repo in repos:
        repo_name = repo["name"]
        repo_full_name = repo["full_name"]
        
        alerts = get_dependabot_alerts(owner, repo_name, token)
        
        if alerts:
            repos_with_alerts += 1
            total_alerts += len(alerts)
            
            print(f"\n📦 Repository: {repo_full_name}")
            print(f"   URL: {repo['html_url']}")
            print(f"   Alerts: {len(alerts)} open")
            print("   " + "-" * 70)
            
            for alert in alerts:
                severity = alert["security_advisory"]["severity"]
                severity_count[severity] += 1
                
                package = alert["security_advisory"]["package"]["name"]
                summary = alert["security_advisory"]["summary"]
                cve_id = alert["security_advisory"]["cve_id"]
                html_url = alert["html_url"]
                
                print(f"   {format_severity_badge(severity)}")
                print(f"   Package: {package}")
                print(f"   Summary: {summary}")
                if cve_id:
                    print(f"   CVE: {cve_id}")
                print(f"   Details: {html_url}")
                print()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total repositories scanned: {len(repos)}")
    print(f"Repositories with alerts: {repos_with_alerts}")
    print(f"Total open alerts: {total_alerts}")
    
    if total_alerts > 0:
        print("\nAlerts by severity:")
        if severity_count["critical"] > 0:
            print(f"  🔴 Critical: {severity_count['critical']}")
        if severity_count["high"] > 0:
            print(f"  🟠 High: {severity_count['high']}")
        if severity_count["medium"] > 0:
            print(f"  🟡 Medium: {severity_count['medium']}")
        if severity_count["low"] > 0:
            print(f"  🟢 Low: {severity_count['low']}")
        
        print("\n⚠️  Please review and address these security alerts!")
        sys.exit(1)
    else:
        print("\n✅ No open Dependabot alerts found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
