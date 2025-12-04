#!/usr/bin/env python
"""Post-generation hook for cleanup and project setup."""

import os
import shutil
import subprocess
import sys

# Get cookiecutter context values
CI_PLATFORM = "{{ cookiecutter.ci_platform }}"
LICENSE_CHOICE = "{{ cookiecutter.license }}"
PROJECT_SLUG = "{{ cookiecutter.project_slug }}"


def remove_file(filepath: str) -> None:
    """Remove a file if it exists."""
    if os.path.isfile(filepath):
        os.remove(filepath)
        print(f"  Removed: {filepath}")


def remove_dir(dirpath: str) -> None:
    """Remove a directory if it exists."""
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
        print(f"  Removed: {dirpath}/")


def run_command(cmd: list[str], description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"  {description}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Warning: {description} failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"  Warning: Command not found: {cmd[0]}")
        return False


def cleanup_ci_files() -> None:
    """Remove CI files based on selected platform."""
    print("\nConfiguring CI/CD...")

    if CI_PLATFORM == "github":
        remove_file(".gitlab-ci.yml")
    elif CI_PLATFORM == "gitlab":
        remove_dir(".github")
    else:  # "none"
        remove_file(".gitlab-ci.yml")
        remove_dir(".github")


def cleanup_license() -> None:
    """Remove LICENSE file if 'None' was selected."""
    if LICENSE_CHOICE == "None":
        print("\nRemoving LICENSE file...")
        remove_file("LICENSE")


def setup_project() -> None:
    """Initialize git, install dependencies, and copy env file."""
    print("\nSetting up project...")

    # Initialize git repository
    run_command(["git", "init"], "Initializing git repository")

    # Copy .env.example to .env
    if os.path.isfile(".env.example"):
        shutil.copy(".env.example", ".env")
        print("  Copied .env.example to .env")

    # Install dependencies with uv
    if run_command(["uv", "sync", "--all-groups"], "Installing dependencies with uv"):
        print("  Dependencies installed successfully")


def print_next_steps() -> None:
    """Print next steps for the user."""
    print(f"""
{'=' * 60}
Project '{PROJECT_SLUG}' created successfully!
{'=' * 60}

Next steps:

  cd {PROJECT_SLUG}

  # Activate virtual environment (if not using uv run)
  source .venv/bin/activate

  # Edit .env with your database credentials
  $EDITOR .env

  # Run database migrations
  uv run alembic upgrade head

  # Run all quality checks
  make

  # Start the development server
  uv run uvicorn main:app --reload

Happy coding!
""")


def main() -> None:
    """Run post-generation setup."""
    print(f"\nSetting up {PROJECT_SLUG}...")

    cleanup_ci_files()
    cleanup_license()
    setup_project()
    print_next_steps()


if __name__ == "__main__":
    main()
