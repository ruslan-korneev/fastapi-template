"""Setup CLI for FastAPI template project."""

import subprocess
from pathlib import Path
from typing import Literal

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from setup_project.config import ProjectConfig
from setup_project.updaters import apply_all_updates

console = Console()


def get_git_config(key: str) -> str | None:
    """Get git config value."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def get_default_project_name() -> str:
    """Get default project name from current directory."""
    return Path.cwd().name


def prompt_project_config(
    name: str | None,
    description: str | None,
) -> tuple[str, str, str, str]:
    """Prompt for project configuration."""
    console.print("[bold]Project Configuration[/bold]")

    project_name = (
        name
        if name
        else Prompt.ask(
            "  Project name (kebab-case)",
            default=get_default_project_name(),
        )
    )

    project_description = (
        description
        if description
        else Prompt.ask(
            "  Description",
            default="Production-ready FastAPI application",
        )
    )

    author_name = Prompt.ask(
        "  Author name",
        default=get_git_config("user.name") or "Your Name",
    )

    author_email = Prompt.ask(
        "  Author email",
        default=get_git_config("user.email") or "you@example.com",
    )

    console.print()
    return project_name, project_description, author_name, author_email


def prompt_db_config(project_name: str) -> tuple[str, str, str, str, int]:
    """Prompt for database configuration."""
    console.print("[bold]Database Configuration[/bold]")

    default_db_name = ProjectConfig.derive_db_name(project_name)

    db_name = Prompt.ask("  Database name", default=default_db_name)
    db_user = Prompt.ask("  Username", default="postgres")
    db_password = Prompt.ask("  Password", password=True, default="postgres")
    db_host = Prompt.ask("  Host", default="localhost")
    db_port = IntPrompt.ask("  Port", default=5432)

    console.print()
    return db_name, db_user, db_password, db_host, db_port


def prompt_ci_config(skip_ci: bool) -> tuple[Literal["github", "gitlab", "none"], str | None]:
    """Prompt for CI/CD configuration."""
    ci_platform: Literal["github", "gitlab", "none"] = "github"
    github_repo: str | None = None

    if skip_ci:
        return ci_platform, github_repo

    console.print("[bold]CI/CD Platform[/bold]")
    console.print("  [1] GitHub Actions")
    console.print("  [2] GitLab CI")
    console.print("  [3] None")

    ci_choice = Prompt.ask("  Select", choices=["1", "2", "3"], default="1")
    ci_map: dict[str, Literal["github", "gitlab", "none"]] = {
        "1": "github",
        "2": "gitlab",
        "3": "none",
    }
    ci_platform = ci_map[ci_choice]

    if ci_platform == "github":
        github_repo = Prompt.ask("  GitHub repo URL (for badges)", default="")
        if not github_repo:
            github_repo = None

    console.print()
    return ci_platform, github_repo


def print_summary(updated_files: list[str], db_name: str) -> None:
    """Print summary of changes."""
    for file in updated_files:
        if file.startswith("Removed"):
            console.print(f"  [yellow]{file}[/yellow]")
        else:
            console.print(f"  [green]{file}[/green]")

    console.print()
    console.print("[bold green]Done![/bold green] Next steps:")
    console.print("  1. [cyan]uv sync[/cyan]")
    console.print(f"  2. Create database: [cyan]{db_name}[/cyan]")
    console.print("  3. [cyan]make upgrade-db[/cyan]")
    console.print("  4. [cyan]make[/cyan]")
    console.print()


@click.command()
@click.option("--name", help="Project name (kebab-case)")
@click.option("--description", help="Project description")
@click.option("--skip-ci", is_flag=True, help="Skip CI/CD configuration prompts")
def main(name: str | None, description: str | None, skip_ci: bool) -> None:
    """Setup your FastAPI project from template."""
    console.print()
    console.print(Panel("[bold blue]FastAPI Template Setup[/bold blue]", expand=False))
    console.print()

    project_name, project_description, author_name, author_email = prompt_project_config(name, description)
    db_name, db_user, db_password, db_host, db_port = prompt_db_config(project_name)
    ci_platform, github_repo = prompt_ci_config(skip_ci)

    if not Confirm.ask("Apply changes?", default=True):
        console.print("[yellow]Aborted.[/yellow]")
        raise SystemExit(0)

    console.print()

    config = ProjectConfig(
        name=project_name,
        package_name=ProjectConfig.derive_package_name(project_name),
        description=project_description,
        author_name=author_name,
        author_email=author_email,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
        db_host=db_host,
        db_port=db_port,
        ci_platform=ci_platform,
        github_repo=github_repo,
    )

    console.print("[bold]Applying changes...[/bold]")
    updated_files = apply_all_updates(config)
    print_summary(updated_files, db_name)


if __name__ == "__main__":
    main()
