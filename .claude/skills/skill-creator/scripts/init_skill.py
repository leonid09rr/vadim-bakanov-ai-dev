#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill directory with template files

Usage:
    python init_skill.py <skill-name> --path <output-directory>

Example:
    python init_skill.py my-skill --path ./skills
"""

import os
import sys
from pathlib import Path


def to_title_case(hyphen_name):
    """Convert hyphen-case to Title Case"""
    return " ".join(word.capitalize() for word in hyphen_name.split("-"))


SKILL_MD_TEMPLATE = """---
name: {skill_name}
description: TODO: Add a description of what this skill does and when it should be used. Include specific triggers and contexts.
---

# {skill_title}

TODO: Add instructions for using this skill.

## Overview

Describe what this skill does and its main purpose.

## Workflow

### Step 1: [First Step]

Instructions for the first step.

### Step 2: [Second Step]

Instructions for the second step.

## Resources

### Scripts

- `scripts/example.py` - Example script (delete if not needed)

### References

- `references/example.md` - Example reference (delete if not needed)

### Assets

- `assets/` - Templates and files for output (delete if not needed)
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example script for {skill_title}

Delete this file if not needed.
"""

def main():
    print("Hello from {skill_name}!")


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Example Reference

This is an example reference file for {skill_title}.

Delete this file if not needed.

## Section 1

Add reference content here.

## Section 2

Add more reference content here.
"""


def init_skill(skill_name, output_path):
    """Initialize a new skill directory with template files"""
    skill_path = Path(output_path) / skill_name
    skill_title = to_title_case(skill_name)

    # Check if directory already exists
    if skill_path.exists():
        print(f"❌ Error: Directory already exists: {skill_path}")
        return False

    try:
        # Create directories
        skill_path.mkdir(parents=True)
        (skill_path / "scripts").mkdir()
        (skill_path / "references").mkdir()
        (skill_path / "assets").mkdir()

        # Create SKILL.md
        skill_md_content = SKILL_MD_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)
        (skill_path / "SKILL.md").write_text(skill_md_content)

        # Create example script
        example_script_content = EXAMPLE_SCRIPT.format(skill_name=skill_name, skill_title=skill_title)
        example_script_path = skill_path / "scripts" / "example.py"
        example_script_path.write_text(example_script_content)
        os.chmod(example_script_path, 0o755)

        # Create example reference
        example_ref_content = EXAMPLE_REFERENCE.format(skill_name=skill_name, skill_title=skill_title)
        (skill_path / "references" / "example.md").write_text(example_ref_content)

        # Create .gitkeep in assets
        (skill_path / "assets" / ".gitkeep").write_text("")

        print(f"✅ Successfully created skill: {skill_path}")
        print()
        print("Next steps:")
        print(f"  1. Edit {skill_path / 'SKILL.md'} - update the TODO placeholders")
        print("  2. Customize or delete example files in scripts/, references/, assets/")
        print(f"  3. Run quick_validate.py {skill_path} to validate")
        print(f"  4. Run package_skill.py {skill_path} to package")
        return True

    except Exception as e:
        print(f"❌ Error creating skill: {e}")
        return False


def main():
    if len(sys.argv) != 4 or sys.argv[2] != "--path":
        print("Usage: python init_skill.py <skill-name> --path <output-directory>")
        print()
        print("Arguments:")
        print("  skill-name       Hyphen-case identifier (e.g., 'data-analyzer')")
        print("                   Use only lowercase letters, digits, and hyphens")
        print("                   Maximum 40 characters")
        print("  --path           Output directory for the new skill")
        print()
        print("Example:")
        print("  python init_skill.py my-skill --path ./skills")
        sys.exit(1)

    skill_name = sys.argv[1]
    output_path = sys.argv[3]

    # Validate skill name
    import re

    if not re.match(r"^[a-z0-9-]+$", skill_name):
        print(f"❌ Error: Skill name '{skill_name}' must use only lowercase letters, digits, and hyphens")
        sys.exit(1)
    if skill_name.startswith("-") or skill_name.endswith("-") or "--" in skill_name:
        print(f"❌ Error: Skill name '{skill_name}' cannot start/end with hyphen or contain consecutive hyphens")
        sys.exit(1)
    if len(skill_name) > 40:
        print(f"❌ Error: Skill name is too long ({len(skill_name)} characters). Maximum is 40 characters.")
        sys.exit(1)

    success = init_skill(skill_name, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
