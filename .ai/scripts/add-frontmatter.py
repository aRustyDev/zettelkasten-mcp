#!/usr/bin/env python3
"""Add YAML frontmatter to markdown documents."""

import re
import sys
import uuid
from datetime import date
from pathlib import Path


def generate_uuid():
    """Generate uppercase UUID v4."""
    return str(uuid.uuid4()).upper()


def extract_title(content):
    """Extract title from first H1 heading."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1) if match else "Untitled Document"


def has_frontmatter(content):
    """Check if document already has frontmatter."""
    return content.strip().startswith("---")


def determine_status(file_path):
    """Determine appropriate status based on file location/type."""
    path_str = str(file_path)

    if "/completed/" in path_str:
        return "✅ Completed"
    elif "adr-" in path_str:
        return "✅ Accepted"
    elif "INDEX.md" in path_str:
        return "⏳ Living Document"
    elif "FRONTMATTER_ADOPTION" in path_str:
        return "✅ Completed"
    else:
        return "📝 Draft"


def add_frontmatter(
    file_path, author="aRustyDev", doc_id=None, related=None, children=None
):
    """Add frontmatter to a markdown file."""
    # Read existing content
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Skip if already has frontmatter
    if has_frontmatter(content):
        print(f"⏭️  Skipping {file_path.name} (already has frontmatter)")
        return False

    # Generate or use provided UUID
    doc_id = doc_id or generate_uuid()

    # Extract title
    title = extract_title(content)

    # Determine status
    status = determine_status(file_path)

    # Build frontmatter
    frontmatter_lines = [
        "---",
        f"id: {doc_id}",
        f"title: {title}",
        f"status: {status}",
        f"date: {date.today().isoformat()}",
        f"author: {author}",
    ]

    # Add optional fields
    if related:
        frontmatter_lines.append("related:")
        for rel_id in related:
            frontmatter_lines.append(f"  - {rel_id}")

    if children:
        frontmatter_lines.append("children:")
        for child_id in children:
            frontmatter_lines.append(f"  - {child_id}")

    frontmatter_lines.append("---")
    frontmatter_lines.append("")  # Blank line after frontmatter

    # Combine frontmatter with content
    new_content = "\n".join(frontmatter_lines) + content

    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✓ Added frontmatter to {file_path.name} (UUID: {doc_id[:8]}...)")
    return doc_id


def main():
    if len(sys.argv) < 2:
        print("Usage: python add-frontmatter.py <file1.md> [file2.md] ...")
        print("   or: python add-frontmatter.py --glob 'pattern'")
        sys.exit(1)

    files = []
    if sys.argv[1] == "--glob":
        pattern = sys.argv[2]
        files = list(Path().glob(pattern))
    else:
        files = [Path(f) for f in sys.argv[1:]]

    for file_path in files:
        if file_path.exists() and file_path.suffix == ".md":
            add_frontmatter(file_path)
        else:
            print(f"❌ Skipping {file_path} (not found or not .md)")


if __name__ == "__main__":
    main()
