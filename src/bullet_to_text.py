"""
After the bullet points are generated,
this script will allow users to see the bullets
in a more readable text format.
"""

import json
import sys
from pathlib import Path

def json_bullets_to_text(json_file, title="Bullet Summary"):
    """Convert JSON bullet summary to text format."""
    # Create a header
    header = f"{title.upper()}\n{'=' * len(title)}\n\n"

    text_content = []

    for i, item in enumerate(json_file):
        bullets = item.get("bullets", "")
        transcript_chunk = item.get("transcript_chunk", "")

        if bullets:
            # Ensure each bullet is on a separate line
            formatted_bullets = bullets.replace(". ", ".\n- ")
            if not formatted_bullets.startswith("- "):
                formatted_bullets = "- " + formatted_bullets

            text_content.append(f"Part {i + 1}:\n{formatted_bullets}")

        # Optional separator between chunks for readability
        if i < len(json_file) - 1 and transcript_chunk:
            text_content.append("\n" + "=" * 40 + "\n")

    return header + "\n".join(text_content)

def main():
    # Hardcoded file paths
    input_path = Path("./dataset/summarized/bullet/dataset_bullets.json")
    output_path = Path("./dataset/summarized/bullet/dataset_bullets.txt")
    title = "Bullet Summary"
    no_separator = False

    # Check if input file exists
    if not input_path.is_file():
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)

    try:
        # Read and parse the JSON file
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Convert JSON bullets to text
        text_content = json_bullets_to_text(json_data, title=title)

        # Remove separators if specified
        if no_separator:
            text_content = text_content.replace("\n" + "=" * 40 + "\n", "\n")

        # Write to output text file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        print(f"Bullet summary saved to {output_path}")
        print("Conversion completed successfully.")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
