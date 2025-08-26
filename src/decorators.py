"""After the summarization is generated
this decorator will allow users to see the summary
in a more readable format i.e. in text format
"""

import json
import sys
from pathlib import Path

def json_to_text(json_file, title = "Summary"):
    """Convert JSON summary to text format."""
    # Creating a Header for the summary
    header = f"{title.upper()}\n{'=' * len(title)}\n\n"

    # Process the transcript chunks
    text_content = []

    for i, item in enumerate(json_file):
        # Extracting the summary and transcript chunk
        transcript_chunk = item.get("transcript_chunk", "")
        summary = item.get("summary", "")

        # Add transcript chunk and summary to text content
        # if transcript_chunk:
        #     text_content.append(transcript_chunk)

        # Add Summary to text content    
        if summary:
            text_content.append(f"Part {i + 1}: {summary}")

        # Add a separator for readability 
        if i < len(json_file) - 1 and transcript_chunk:
            text_content.append("\n" + "=" * 40 + "\n")
    return header + "\n".join(text_content)

def main():
    # Hardcoded file paths
    input_path = Path("./dataset/summarized/dataset_summarized.json")
    output_path = Path("./dataset/summarized/normal/dataset_summarized.txt")
    title = "Summary"
    no_separator = False

    # Check if input file exists
    if not input_path.is_file():
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)

    try:
        # Read and parse the JSON file
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Convert JSON to text format
        text_content = json_to_text(json_data, title=title)

        # If no separator is specified, remove them
        if no_separator:
            text_content = text_content.replace("\n" + "=" * 40 + "\n", "\n")

        # Write to the output text file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        
        print(f"Summary saved to {output_path}")
        print("Conversion completed successfully.")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



