"""GitHub Change Detection and Tracking"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv
from github import Github, GithubException

load_dotenv()


class GitHubTracker:
    """Track GitHub repository changes and commits"""

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment")

        self.gh = Github(self.token)
        self.storage_dir = Path("data/github_updates")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_last_sha(self, repo_name: str) -> Optional[str]:
        """Get the last checked SHA for a repository"""
        sha_file = self.storage_dir / f"{repo_name.replace('/', '_')}_last_sha.json"

        if sha_file.exists():
            try:
                with open(sha_file, "r") as f:
                    data = json.load(f)
                    return data.get("last_sha")
            except:
                pass

        return None

    def _save_last_sha(self, repo_name: str, sha: str):
        """Save the last checked SHA for a repository"""
        sha_file = self.storage_dir / f"{repo_name.replace('/', '_')}_last_sha.json"

        data = {
            "last_sha": sha,
            "last_checked": datetime.now().isoformat()
        }

        with open(sha_file, "w") as f:
            json.dump(data, f, indent=2)

    def check_updates(self, repo_name: str) -> Optional[Dict]:
        """
        Check for new commits in a repository

        Args:
            repo_name: Repository name in format "owner/repo" or just "repo"

        Returns:
            Dictionary with commit info if new commits found, None otherwise
        """
        try:
            # If no owner specified, get authenticated user
            if "/" not in repo_name:
                user = self.gh.get_user()
                repo_name = f"{user.login}/{repo_name}"

            repo = self.gh.get_repo(repo_name)
            commits = list(repo.get_commits()[:5])

            if not commits:
                return None

            last_sha = self._get_last_sha(repo_name)
            latest_commit = commits[0]

            # No new commits
            if latest_commit.sha == last_sha:
                return None

            # New commits detected!
            self._save_last_sha(repo_name, latest_commit.sha)

            # Extract task IDs from commit message (e.g., "Fix #15" or "Task #20")
            import re
            task_ids = re.findall(r'#(\d+)', latest_commit.commit.message)

            # Get changed files
            files_changed = [f.filename for f in latest_commit.files] if latest_commit.files else []

            return {
                "repo": repo_name,
                "latest_sha": latest_commit.sha,
                "message": latest_commit.commit.message,
                "author": latest_commit.commit.author.name,
                "date": latest_commit.commit.author.date.isoformat(),
                "files_changed": files_changed[:10],  # Limit to 10 files
                "url": latest_commit.html_url,
                "task_ids": task_ids,
                "stats": {
                    "additions": sum(f.additions for f in latest_commit.files) if latest_commit.files else 0,
                    "deletions": sum(f.deletions for f in latest_commit.files) if latest_commit.files else 0,
                    "total_files": len(latest_commit.files) if latest_commit.files else 0
                }
            }

        except GithubException as e:
            if e.status == 404:
                return {"error": f"Repository '{repo_name}' not found"}
            elif e.status == 403:
                return {"error": "Rate limit exceeded or insufficient permissions"}
            return {"error": f"GitHub API error: {e.status}"}
        except Exception as e:
            return {"error": str(e)}

    def get_all_repos(self) -> List[str]:
        """Get list of all user repositories"""
        try:
            user = self.gh.get_user()
            repos = [repo.full_name for repo in user.get_repos(type="owner")]
            return repos
        except Exception as e:
            return []

    def format_update_message(self, update: Dict) -> str:
        """Format update information for display/notification"""
        if "error" in update:
            return f"Error: {update['error']}"

        lines = [
            f"🔔 New commit in {update['repo']}",
            f"",
            f"Author: {update['author']}",
            f"Message: {update['message'][:100]}...",
            f"",
            f"Stats:",
            f"  +{update['stats']['additions']} additions",
            f"  -{update['stats']['deletions']} deletions",
            f"  {update['stats']['total_files']} files changed",
            f"",
            f"Files: {', '.join(update['files_changed'][:5])}",
            f"",
            f"View: {update['url']}"
        ]

        if update['task_ids']:
            lines.insert(4, f"Tasks mentioned: #{', #'.join(update['task_ids'])}")

        return "\n".join(lines)
