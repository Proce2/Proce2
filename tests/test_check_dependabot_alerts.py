#!/usr/bin/env python3
"""
Unit tests for the Dependabot alerts checker script.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import check_dependabot_alerts


class TestDependabotAlertsChecker(unittest.TestCase):
    """Test cases for the Dependabot alerts checker."""
    
    def test_format_severity_badge(self):
        """Test severity badge formatting."""
        self.assertEqual(
            check_dependabot_alerts.format_severity_badge("critical"),
            "🔴 CRITICAL"
        )
        self.assertEqual(
            check_dependabot_alerts.format_severity_badge("high"),
            "🟠 HIGH"
        )
        self.assertEqual(
            check_dependabot_alerts.format_severity_badge("medium"),
            "🟡 MEDIUM"
        )
        self.assertEqual(
            check_dependabot_alerts.format_severity_badge("low"),
            "🟢 LOW"
        )
        # Test case insensitivity
        self.assertEqual(
            check_dependabot_alerts.format_severity_badge("CRITICAL"),
            "🔴 CRITICAL"
        )
    
    @patch('check_dependabot_alerts.requests.get')
    def test_get_repositories_success(self, mock_get):
        """Test fetching repositories successfully."""
        # First page with data
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = [
            {"name": "repo1", "full_name": "owner/repo1"},
            {"name": "repo2", "full_name": "owner/repo2"}
        ]
        
        # Second page (empty)
        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = []
        
        mock_get.side_effect = [first_response, second_response]
        
        repos = check_dependabot_alerts.get_repositories("owner", "token")
        
        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]["name"], "repo1")
        self.assertEqual(repos[1]["name"], "repo2")
    
    @patch('check_dependabot_alerts.requests.get')
    def test_get_repositories_pagination(self, mock_get):
        """Test repository pagination."""
        # First page
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = [{"name": f"repo{i}"} for i in range(100)]
        
        # Second page (empty)
        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = []
        
        mock_get.side_effect = [first_response, second_response]
        
        repos = check_dependabot_alerts.get_repositories("owner", "token")
        
        self.assertEqual(len(repos), 100)
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('check_dependabot_alerts.requests.get')
    def test_get_dependabot_alerts_success(self, mock_get):
        """Test fetching Dependabot alerts successfully."""
        # First page with data
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = [
            {
                "number": 1,
                "security_advisory": {
                    "severity": "high",
                    "summary": "Test vulnerability",
                    "cve_id": "CVE-2024-1234",
                    "package": {"name": "test-package"}
                },
                "html_url": "https://github.com/owner/repo/security/dependabot/1"
            }
        ]
        
        # Second page (empty)
        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = []
        
        mock_get.side_effect = [first_response, second_response]
        
        alerts = check_dependabot_alerts.get_dependabot_alerts("owner", "repo", "token")
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["security_advisory"]["severity"], "high")
    
    @patch('check_dependabot_alerts.requests.get')
    def test_get_dependabot_alerts_pagination(self, mock_get):
        """Test pagination of Dependabot alerts."""
        # First page with 100 alerts
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = [
            {
                "number": i,
                "security_advisory": {
                    "severity": "high",
                    "summary": f"Test vulnerability {i}",
                    "cve_id": f"CVE-2024-{i}",
                    "package": {"name": "test-package"}
                },
                "html_url": f"https://github.com/owner/repo/security/dependabot/{i}"
            } for i in range(1, 101)
        ]
        
        # Second page (empty)
        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = []
        
        mock_get.side_effect = [first_response, second_response]
        
        alerts = check_dependabot_alerts.get_dependabot_alerts("owner", "repo", "token")
        
        self.assertEqual(len(alerts), 100)
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('check_dependabot_alerts.requests.get')
    def test_get_dependabot_alerts_not_found(self, mock_get):
        """Test handling of 404 error (Dependabot not enabled)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        alerts = check_dependabot_alerts.get_dependabot_alerts("owner", "repo", "token")
        
        self.assertEqual(len(alerts), 0)
    
    @patch('check_dependabot_alerts.requests.get')
    def test_get_dependabot_alerts_forbidden(self, mock_get):
        """Test handling of 403 error (access forbidden)."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
        
        alerts = check_dependabot_alerts.get_dependabot_alerts("owner", "repo", "token")
        
        self.assertEqual(len(alerts), 0)


if __name__ == '__main__':
    unittest.main()
