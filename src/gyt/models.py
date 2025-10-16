"""Data models for gyt."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import json


@dataclass
class Milestone:
    """A single milestone entry."""
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Milestone":
        return cls(
            message=data["message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            tags=data.get("tags", [])
        )


@dataclass
class Commit:
    """A commit containing one or more milestones."""
    message: str
    milestones: List[Milestone]
    timestamp: datetime = field(default_factory=datetime.now)
    commit_hash: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "milestones": [m.to_dict() for m in self.milestones],
            "timestamp": self.timestamp.isoformat(),
            "commit_hash": self.commit_hash
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Commit":
        return cls(
            message=data["message"],
            milestones=[Milestone.from_dict(m) for m in data["milestones"]],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            commit_hash=data.get("commit_hash")
        )


class Repository:
    """Manages the gyt repository state."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.gyt_dir = repo_path / ".gyt"
        self.staging_file = self.gyt_dir / "staging.json"
        self.commits_file = self.gyt_dir / "commits.json"
        self.config_file = self.gyt_dir / "config.json"

    def init(self) -> bool:
        """Initialize a new gyt repository."""
        if self.gyt_dir.exists():
            return False

        self.gyt_dir.mkdir(parents=True)
        self.staging_file.write_text("[]")
        self.commits_file.write_text("[]")
        self.config_file.write_text(json.dumps({
            "user": {
                "name": "",
                "email": ""
            },
            "remote": {
                "url": ""
            }
        }, indent=2))
        return True

    def is_initialized(self) -> bool:
        """Check if current directory is a gyt repository."""
        return self.gyt_dir.exists()

    def get_staged_milestones(self) -> List[Milestone]:
        """Get currently staged milestones."""
        if not self.staging_file.exists():
            return []
        data = json.loads(self.staging_file.read_text())
        return [Milestone.from_dict(m) for m in data]

    def add_milestone(self, milestone: Milestone):
        """Add a milestone to staging area."""
        staged = self.get_staged_milestones()
        staged.append(milestone)
        self.staging_file.write_text(json.dumps([m.to_dict() for m in staged], indent=2))

    def clear_staging(self):
        """Clear the staging area."""
        self.staging_file.write_text("[]")

    def get_commits(self) -> List[Commit]:
        """Get all commits."""
        if not self.commits_file.exists():
            return []
        data = json.loads(self.commits_file.read_text())
        return [Commit.from_dict(c) for c in data]

    def add_commit(self, commit: Commit):
        """Add a new commit to history."""
        commits = self.get_commits()

        # Generate simple hash from timestamp
        import hashlib
        hash_input = f"{commit.timestamp.isoformat()}{commit.message}"
        commit.commit_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]

        commits.append(commit)
        self.commits_file.write_text(json.dumps([c.to_dict() for c in commits], indent=2))

    def get_config(self) -> dict:
        """Get repository configuration."""
        if not self.config_file.exists():
            return {}
        return json.loads(self.config_file.read_text())

    def set_config(self, key: str, value: str):
        """Set a configuration value."""
        config = self.get_config()
        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        self.config_file.write_text(json.dumps(config, indent=2))
