#!/bin/bash
# Generate UUID for markdown frontmatter
# Usage: .ai/scripts/generate-uuid.sh [--template]

set -e

# Generate uppercase UUID
uuid=$(uuidgen)

if [ "$1" == "--template" ]; then
    # Print full frontmatter template
    echo "Generated UUID: $uuid"
    echo ""
    echo "Frontmatter template:"
    echo "---"
    echo "id: $uuid"
    echo "title: <Document Title>"
    echo "status: 📝 Draft  # Or: ✅ Completed, ⏳ In Progress, 🗄️ Archived, 🔄 Under Review"
    echo "date: $(date +%Y-%m-%d)"
    echo "author: <Your-GitHub-Username>"
    echo "related:  # Optional: UUIDs of related documents"
    echo "  - <UUID>"
    echo "children:  # Optional: UUIDs of child documents"
    echo "  - <UUID>"
    echo "---"
else
    # Just print UUID
    echo "$uuid"
fi
