"""CLI commands for gyt."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

from .models import Repository, Milestone, Commit

app = typer.Typer()
console = Console()


def get_repo() -> Repository:
    """Get the repository for the current directory."""
    return Repository(Path.cwd())


def ensure_repo() -> Repository:
    """Ensure we're in a gyt repository."""
    repo = get_repo()
    if not repo.is_initialized():
        console.print("[red]Not a gyt repository. Run 'gyt init' first.[/red]")
        raise typer.Exit(1)
    return repo


@app.command()
def init():
    """Initialize a new gyt repository in the current directory."""
    repo = get_repo()
    if repo.init():
        console.print("[green]Initialized empty gyt repository in .gyt/[/green]")
    else:
        console.print("[yellow]Repository already initialized.[/yellow]")


@app.command()
def add(
    message: Optional[str] = typer.Argument(None, help="Milestone message"),
    all: bool = typer.Option(False, "--all", "-a", help="Add a default milestone for today")
):
    """Add a milestone to the staging area."""
    repo = ensure_repo()

    if all or message == ".":
        # Simple default milestone
        milestone = Milestone(message="Daily progress")
    elif message:
        milestone = Milestone(message=message)
    else:
        console.print("[red]Please provide a milestone message or use --all/-a[/red]")
        raise typer.Exit(1)

    repo.add_milestone(milestone)
    console.print(f"[green]Added milestone:[/green] {milestone.message}")


@app.command()
def commit(
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
):
    """Commit staged milestones."""
    repo = ensure_repo()

    staged = repo.get_staged_milestones()
    if not staged:
        console.print("[yellow]No milestones staged. Use 'gyt add' first.[/yellow]")
        raise typer.Exit(1)

    commit = Commit(message=message, milestones=staged)
    repo.add_commit(commit)
    repo.clear_staging()

    console.print(f"[green]Committed {len(staged)} milestone(s):[/green] {message}")
    console.print(f"[dim]Commit hash: {commit.commit_hash}[/dim]")


@app.command()
def status():
    """Show the status of the repository."""
    repo = ensure_repo()

    staged = repo.get_staged_milestones()

    console.print(Panel("[bold]Gyt Status[/bold]"))

    if staged:
        console.print("\n[green]Staged milestones:[/green]")
        for i, milestone in enumerate(staged, 1):
            console.print(f"  {i}. {milestone.message}")
    else:
        console.print("\n[dim]No milestones staged[/dim]")

    console.print(f"\n[dim]Use 'gyt add <message>' to stage milestones[/dim]")
    console.print(f"[dim]Use 'gyt commit -m \"message\"' to commit staged milestones[/dim]")


@app.command()
def log(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of commits to show")
):
    """Show commit history."""
    repo = ensure_repo()

    commits = repo.get_commits()

    if not commits:
        console.print("[yellow]No commits yet.[/yellow]")
        return

    # Show most recent first
    for commit in reversed(commits[-limit:]):
        console.print(f"\n[yellow]commit {commit.commit_hash}[/yellow]")
        console.print(f"Date:   {commit.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"\n    {commit.message}\n")

        for milestone in commit.milestones:
            console.print(f"    • {milestone.message}")


@app.command()
def stats(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to show stats for")
):
    """Show milestone statistics."""
    repo = ensure_repo()

    commits = repo.get_commits()

    if not commits:
        console.print("[yellow]No commits yet.[/yellow]")
        return

    # Calculate stats
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)
    recent_commits = [c for c in commits if c.timestamp >= cutoff]

    total_milestones = sum(len(c.milestones) for c in recent_commits)

    table = Table(title=f"Stats for last {days} days")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Commits", str(len(recent_commits)))
    table.add_row("Total Milestones", str(total_milestones))
    if recent_commits:
        table.add_row("Avg Milestones/Commit", f"{total_milestones/len(recent_commits):.1f}")

    console.print(table)


@app.command()
def config(
    key: Optional[str] = typer.Argument(None, help="Config key (e.g., user.name)"),
    value: Optional[str] = typer.Argument(None, help="Config value"),
):
    """Get or set configuration values."""
    repo = ensure_repo()

    if key and value:
        repo.set_config(key, value)
        console.print(f"[green]Set {key} = {value}[/green]")
    elif key:
        config = repo.get_config()
        keys = key.split(".")
        current = config
        for k in keys:
            current = current.get(k, {})
        console.print(f"{key} = {current}")
    else:
        import json
        config = repo.get_config()
        console.print(json.dumps(config, indent=2))


@app.command()
def push(
    remote: Optional[str] = typer.Option(None, "--remote", help="Remote URL to push to")
):
    """Push commits to remote (gythub)."""
    repo = ensure_repo()

    config = repo.get_config()
    remote_url = remote or config.get("remote", {}).get("url", "")

    if not remote_url:
        console.print("[red]No remote configured. Use 'gyt config remote.url <url>' first.[/red]")
        raise typer.Exit(1)

    commits = repo.get_commits()

    if not commits:
        console.print("[yellow]No commits to push.[/yellow]")
        return

    # TODO: Implement actual API call to gythub server
    console.print(f"[yellow]Pushing {len(commits)} commit(s) to {remote_url}...[/yellow]")
    console.print("[dim]Note: Remote push not yet implemented. This will sync to gythub when available.[/dim]")

    # Placeholder for future implementation:
    # import requests
    # response = requests.post(f"{remote_url}/api/push", json={
    #     "commits": [c.to_dict() for c in commits],
    #     "user": config.get("user", {})
    # })
