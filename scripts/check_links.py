#!/usr/bin/env python3
"""
Markdown Link Checker
Checks all markdown files for broken internal links
"""

import os
import re
import sys


def find_markdown_files(root_dir):
    """Find all markdown files in the repository"""
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories and .claude, .pytest_cache
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in ["claude", "pytest_cache"]
        ]

        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files


def extract_links_from_file(file_path):
    """Extract all markdown links from a file"""
    links = []
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Find all markdown links [text](url)
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(link_pattern, content)

        for text, url in matches:
            # Skip external links (http/https)
            if not url.startswith(("http://", "https://", "mailto:", "#")):
                links.append(
                    {
                        "file": file_path,
                        "text": text,
                        "url": url,
                        "line": content[: content.find(f"[{text}]({url})")].count("\n")
                        + 1,
                    }
                )
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return links


def check_link_exists(link_url, from_file):
    """Check if a link target exists"""
    from_dir = os.path.dirname(from_file)
    target_path = os.path.normpath(os.path.join(from_dir, link_url))

    # Check if file exists
    if os.path.exists(target_path):
        return True, "exists"

    # Check if it's a directory with README.md
    if os.path.isdir(target_path):
        readme_path = os.path.join(target_path, "README.md")
        if os.path.exists(readme_path):
            return True, "directory with README"

    # Check if it's a file without extension (assume .md)
    if not os.path.splitext(target_path)[1]:
        md_path = target_path + ".md"
        if os.path.exists(md_path):
            return True, "file with .md extension"

    return False, "not found"


def main():
    root_dir = "."
    md_files = find_markdown_files(root_dir)

    print(f"Checking {len(md_files)} markdown files...")
    print("=" * 60)

    broken_links = []
    total_links = 0

    for md_file in md_files:
        links = extract_links_from_file(md_file)
        total_links += len(links)

        for link in links:
            exists, reason = check_link_exists(link["url"], md_file)
            if not exists:
                broken_links.append(link)
                print(f"❌ BROKEN: {md_file}:{link['line']}")
                print(f"   Link: [{link['text']}]({link['url']})")
                print(f"   Reason: {reason}")
                print()

    print("=" * 60)
    print("Summary:")
    print(f"  Total links checked: {total_links}")
    print(f"  Broken links: {len(broken_links)}")
    print(f"  Working links: {total_links - len(broken_links)}")

    if broken_links:
        print(f"\n❌ Found {len(broken_links)} broken links!")
        return 1
    else:
        print(f"\n✅ All {total_links} links are working!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
