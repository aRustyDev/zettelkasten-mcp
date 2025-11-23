#!/usr/bin/env python3
"""Validate YAML frontmatter in markdown documents."""

import re
import sys
from pathlib import Path


class FrontmatterValidator:
    """Validates markdown frontmatter against project standards."""

    REQUIRED_FIELDS = {"id", "title", "status", "date", "author"}
    UUID_PATTERN = re.compile(
        r"^[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$"
    )
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL | re.MULTILINE)

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.all_uuids = {}  # UUID -> file path

    def validate_file(self, file_path: Path) -> bool:
        """Validate a single markdown file."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if frontmatter exists
        if not content.strip().startswith("---"):
            self.errors.append(f"{file_path}: No frontmatter found")
            return False

        # Extract frontmatter
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            self.errors.append(f"{file_path}: Invalid frontmatter format")
            return False

        frontmatter = self._parse_frontmatter(match.group(1))

        # Validate required fields
        missing = self.REQUIRED_FIELDS - frontmatter.keys()
        if missing:
            self.errors.append(
                f"{file_path}: Missing required fields: {', '.join(missing)}"
            )
            return False

        # Validate UUID format
        if not self.UUID_PATTERN.match(frontmatter["id"]):
            self.errors.append(f"{file_path}: Invalid UUID format: {frontmatter['id']}")
            return False

        # Check for duplicate UUIDs
        if frontmatter["id"] in self.all_uuids:
            self.errors.append(
                f"{file_path}: Duplicate UUID {frontmatter['id']} "
                f"(also in {self.all_uuids[frontmatter['id']]})"
            )
            return False

        self.all_uuids[frontmatter["id"]] = file_path

        # Validate date format
        if not self.DATE_PATTERN.match(frontmatter["date"]):
            self.errors.append(
                f"{file_path}: Invalid date format: {frontmatter['date']}"
            )
            return False

        # Check title matches H1
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match and title_match.group(1) != frontmatter["title"]:
            self.warnings.append(
                f"{file_path}: Title mismatch - "
                f"frontmatter: '{frontmatter['title']}', "
                f"H1: '{title_match.group(1)}'"
            )

        return True

    def _parse_frontmatter(self, fm_text: str) -> dict[str, str]:
        """Parse YAML-like frontmatter into a dict."""
        result = {}
        current_key = None
        current_list = []

        for line in fm_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" in line and not line.startswith("-"):
                if current_key and current_list:
                    result[current_key] = current_list
                    current_list = []

                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if value:
                    result[key] = value
                else:
                    current_key = key
            elif line.startswith("-") and current_key:
                value = line[1:].strip().split("#")[0].strip()
                current_list.append(value)

        if current_key and current_list:
            result[current_key] = current_list

        return result

    def validate_uuid_references(self):
        """Validate that all UUID references in related/children exist."""
        valid_uuids = set(self.all_uuids.keys())

        for _uuid, file_path in self.all_uuids.items():
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            match = self.FRONTMATTER_PATTERN.match(content)
            if match:
                frontmatter = self._parse_frontmatter(match.group(1))

                # Check related UUIDs
                if "related" in frontmatter:
                    related = frontmatter["related"]
                    if isinstance(related, list):
                        for ref_uuid in related:
                            if ref_uuid and ref_uuid not in valid_uuids:
                                self.errors.append(
                                    f"{file_path}: Invalid UUID reference in 'related': {ref_uuid}"
                                )

                # Check children UUIDs
                if "children" in frontmatter:
                    children = frontmatter["children"]
                    if isinstance(children, list):
                        for ref_uuid in children:
                            if ref_uuid and ref_uuid not in valid_uuids:
                                self.errors.append(
                                    f"{file_path}: Invalid UUID reference in 'children': {ref_uuid}"
                                )


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-frontmatter.py <file1.md> [file2.md] ...")
        print("   or: python validate-frontmatter.py --glob 'pattern'")
        sys.exit(1)

    validator = FrontmatterValidator()
    files = []

    if sys.argv[1] == "--glob":
        pattern = sys.argv[2]
        files = list(Path().glob(pattern))
    else:
        files = [Path(f) for f in sys.argv[1:]]

    # Validate each file
    total = 0
    passed = 0

    for file_path in files:
        if file_path.exists() and file_path.suffix == ".md":
            total += 1
            if validator.validate_file(file_path):
                passed += 1

    # Validate UUID references
    validator.validate_uuid_references()

    # Print results
    print(f"\n{'=' * 60}")
    print("Frontmatter Validation Results")
    print(f"{'=' * 60}")
    print(f"Files validated: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    if validator.errors:
        print(f"\n❌ Errors ({len(validator.errors)}):")
        for error in validator.errors:
            print(f"  - {error}")

    if validator.warnings:
        print(f"\n⚠️  Warnings ({len(validator.warnings)}):")
        for warning in validator.warnings:
            print(f"  - {warning}")

    if not validator.errors and not validator.warnings:
        print("\n✅ All frontmatter is valid!")
        sys.exit(0)
    elif not validator.errors:
        print("\n✅ All frontmatter is valid (with warnings)")
        sys.exit(0)
    else:
        print("\n❌ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
