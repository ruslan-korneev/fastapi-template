#!/usr/bin/env python
"""Pre-generation hook for validating cookiecutter inputs."""

import re
import sys

project_slug = "{{ cookiecutter.project_slug }}"
author_email = "{{ cookiecutter.author_email }}"


def validate_project_slug(slug: str) -> bool:
    """Validate that project_slug is valid kebab-case."""
    pattern = r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$"
    return bool(re.match(pattern, slug))


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return True  # Email is optional
    pattern = r"^[\w.+-]+@[\w.-]+\.\w+$"
    return bool(re.match(pattern, email))


def main() -> None:
    """Run all validations."""
    errors = []

    if not validate_project_slug(project_slug):
        errors.append(
            f"ERROR: project_slug '{project_slug}' is not valid kebab-case.\n"
            "Use only lowercase letters, numbers, and hyphens. "
            "Must start with a letter and not end with a hyphen."
        )

    if not validate_email(author_email):
        errors.append(
            f"ERROR: '{author_email}' is not a valid email address format."
        )

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)

    print("Validation passed, generating project...")


if __name__ == "__main__":
    main()
