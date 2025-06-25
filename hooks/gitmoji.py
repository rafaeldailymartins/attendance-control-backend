import sys
from pathlib import Path
import re

EMOJIS = {
    "feat": "✨",  # :sparkles:
    "fix": "🐛",  # :bug:
    "docs": "📝",  # :memo:
    "style": "🎨",  # :art:
    "refactor": "♻️",  # :recycle:
    "test": "✅",  # :white_check_mark:
    "chore": "🔧",  # :wrench:
    "perf": "⚡️",  # :zap:
    "ci": "👷",  # :construction_worker:
}


def main():
    # Extract the commit message
    commit_message_path = Path(sys.argv[1])
    message = commit_message_path.read_text().strip()
    # Extract the pattern from message
    match = re.match(r"^(?P<type>\w+)(\(.+\))?:", message)
    if match:
        # Extract the commit type
        commit_type = match.group("type")
        # If there is an emoji for this type, add it to the commit message.
        emoji = EMOJIS.get(commit_type)
        if emoji:
            updated = f"{emoji} {message}"
            commit_message_path.write_text(updated)

    return 0


if __name__ == "__main__":
    sys.exit(main())
