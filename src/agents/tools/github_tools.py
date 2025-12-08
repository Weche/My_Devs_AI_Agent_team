"""GitHub integration tools for Albedo"""

import os
from typing import Optional, List, Dict
from dotenv import load_dotenv
import requests

load_dotenv()


def get_github_headers() -> Dict[str, str]:
    """Get headers for GitHub API requests"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


def list_github_repos_tool(username: Optional[str] = None) -> str:
    """
    List GitHub repositories for authenticated user or specified username.

    Args:
        username: GitHub username (optional, defaults to authenticated user)

    Returns:
        Formatted list of repositories
    """
    try:
        headers = get_github_headers()

        if username:
            url = f"https://api.github.com/users/{username}/repos"
        else:
            url = "https://api.github.com/user/repos"

        # Add parameters for sorting and type
        params = {
            "sort": "updated",
            "per_page": 20,
            "type": "owner"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        repos = response.json()

        if not repos:
            return "No repositories found"

        lines = [f"GitHub Repositories ({len(repos)}):\n"]
        for repo in repos:
            visibility = "🔒 Private" if repo.get("private") else "🌐 Public"
            language = repo.get("language") or "Unknown"
            updated = repo.get("updated_at", "")[:10]

            lines.append(
                f"- {repo['name']} ({visibility})\n"
                f"  Language: {language} | Updated: {updated}\n"
                f"  {repo.get('description', 'No description')}"
            )

        return "\n".join(lines)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "Error: Invalid GitHub token. Please check GITHUB_TOKEN in .env"
        return f"Error accessing GitHub API: {e.response.status_code}"
    except Exception as e:
        return f"Error listing repos: {str(e)}"


def get_github_repo_info_tool(repo_name: str, owner: Optional[str] = None) -> str:
    """
    Get detailed information about a GitHub repository.

    Args:
        repo_name: Name of the repository
        owner: Owner of the repo (optional, defaults to authenticated user)

    Returns:
        Detailed repository information
    """
    try:
        headers = get_github_headers()

        # If no owner specified, get authenticated user
        if not owner:
            user_response = requests.get("https://api.github.com/user", headers=headers)
            user_response.raise_for_status()
            owner = user_response.json()["login"]

        # Get repo info
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        repo = response.json()

        # Get recent commits
        commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
        commits_response = requests.get(commits_url, headers=headers, params={"per_page": 5})
        commits = commits_response.json() if commits_response.status_code == 200 else []

        # Get open issues count
        issues_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
        issues_response = requests.get(issues_url, headers=headers, params={"state": "open", "per_page": 1})
        open_issues = len(issues_response.json()) if issues_response.status_code == 200 else repo.get("open_issues_count", 0)

        # Format response
        lines = [
            f"Repository: {repo['full_name']}",
            f"Description: {repo.get('description', 'No description')}",
            f"Language: {repo.get('language', 'Unknown')}",
            f"Visibility: {'Private' if repo.get('private') else 'Public'}",
            f"Stars: {repo.get('stargazers_count', 0)} | Forks: {repo.get('forks_count', 0)}",
            f"Open Issues: {open_issues}",
            f"Default Branch: {repo.get('default_branch', 'main')}",
            f"Created: {repo.get('created_at', '')[:10]}",
            f"Last Updated: {repo.get('updated_at', '')[:10]}",
        ]

        if commits:
            lines.append("\nRecent Commits:")
            for commit in commits[:3]:
                commit_msg = commit['commit']['message'].split('\n')[0][:60]
                commit_date = commit['commit']['author']['date'][:10]
                lines.append(f"  - {commit_msg} ({commit_date})")

        return "\n".join(lines)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Error: Repository '{repo_name}' not found"
        return f"Error accessing GitHub API: {e.response.status_code}"
    except Exception as e:
        return f"Error getting repo info: {str(e)}"


def create_github_issue_tool(
    repo_name: str,
    title: str,
    body: str = "",
    labels: Optional[List[str]] = None,
    owner: Optional[str] = None
) -> str:
    """
    Create an issue in a GitHub repository.

    Args:
        repo_name: Name of the repository
        title: Issue title
        body: Issue description (optional)
        labels: List of label names (optional)
        owner: Owner of the repo (optional, defaults to authenticated user)

    Returns:
        Success message with issue URL
    """
    try:
        headers = get_github_headers()

        # If no owner specified, get authenticated user
        if not owner:
            user_response = requests.get("https://api.github.com/user", headers=headers)
            user_response.raise_for_status()
            owner = user_response.json()["login"]

        # Create issue
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"

        data = {
            "title": title,
            "body": body
        }

        if labels:
            data["labels"] = labels

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        issue = response.json()

        return (
            f"✓ Created issue #{issue['number']}: {title}\n"
            f"URL: {issue['html_url']}"
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Error: Repository '{repo_name}' not found or no access"
        elif e.response.status_code == 410:
            return f"Error: Issues are disabled for repository '{repo_name}'"
        return f"Error creating issue: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error creating issue: {str(e)}"


def list_github_issues_tool(
    repo_name: str,
    state: str = "open",
    owner: Optional[str] = None
) -> str:
    """
    List issues in a GitHub repository.

    Args:
        repo_name: Name of the repository
        state: Issue state (open, closed, all)
        owner: Owner of the repo (optional, defaults to authenticated user)

    Returns:
        Formatted list of issues
    """
    try:
        headers = get_github_headers()

        # If no owner specified, get authenticated user
        if not owner:
            user_response = requests.get("https://api.github.com/user", headers=headers)
            user_response.raise_for_status()
            owner = user_response.json()["login"]

        # Get issues
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
        params = {
            "state": state,
            "per_page": 15
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        issues = response.json()

        if not issues:
            return f"No {state} issues found in {repo_name}"

        lines = [f"Issues in {owner}/{repo_name} ({state}):\n"]
        for issue in issues:
            # Skip pull requests
            if "pull_request" in issue:
                continue

            labels_str = ", ".join([label["name"] for label in issue.get("labels", [])])
            labels_info = f" [{labels_str}]" if labels_str else ""

            lines.append(
                f"#{issue['number']}: {issue['title']}{labels_info}\n"
                f"  Created: {issue['created_at'][:10]} | Comments: {issue.get('comments', 0)}"
            )

        return "\n".join(lines)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Error: Repository '{repo_name}' not found"
        return f"Error listing issues: {e.response.status_code}"
    except Exception as e:
        return f"Error listing issues: {str(e)}"


def create_github_repo_tool(
    repo_name: str,
    description: str = "",
    private: bool = False,
    auto_init: bool = True
) -> str:
    """
    Create a new GitHub repository.

    Args:
        repo_name: Name of the repository
        description: Repository description (optional)
        private: Whether the repo should be private (default: False)
        auto_init: Initialize with README (default: True)

    Returns:
        Success message with repository URL
    """
    try:
        headers = get_github_headers()

        # Create repository
        url = "https://api.github.com/user/repos"

        data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": False
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        repo = response.json()

        visibility = "Private" if private else "Public"
        return (
            f"✓ Created repository: {repo['full_name']}\n"
            f"Visibility: {visibility}\n"
            f"Description: {description or 'No description'}\n"
            f"URL: {repo['html_url']}\n"
            f"Clone: {repo['clone_url']}"
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            error_data = e.response.json()
            if "errors" in error_data:
                errors = error_data["errors"]
                if any("already exists" in err.get("message", "").lower() for err in errors):
                    return f"Error: Repository '{repo_name}' already exists"
            return f"Error: {error_data.get('message', 'Validation failed')}"
        elif e.response.status_code == 403:
            return "Error: Insufficient permissions to create repository. Check GitHub token scopes."
        return f"Error creating repository: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error creating repository: {str(e)}"
