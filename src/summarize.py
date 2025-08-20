import json
from transformers import pipeline

# Load summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_existing_dataset(input_file, output_file, chunk_minutes=5):
    # Load dataset.json
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    summarized = []
    for idx, entry in enumerate(data):
        start_min = idx * chunk_minutes
        end_min = (idx + 1) * chunk_minutes

        # Summarize transcript
        # Truncate input to 4000 characters (safe for BART)
        chunk = entry["transcript_chunk"][:4000] # Bart can handle up to 4000 characters or 1024 tokens
        summary_text = summarizer(
            chunk,
            max_length=80, min_length=20, do_sample=False
        )[0]["summary_text"]

        # Prefix with time
        if idx == 0:
            prefixed = f"In the first {chunk_minutes} minutes, {summary_text}"
        else:
            prefixed = f"In the {start_min}-{end_min} minutes, {summary_text}"

        summarized.append({
            "transcript_chunk": entry["transcript_chunk"],
            "summary": prefixed
        })

    # Save new file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summarized, f, indent=2, ensure_ascii=False)

    print(f"Summaries saved to {output_file}")


if __name__ == "__main__":
    summarize_existing_dataset("./dataset/output/dataset.json", "./dataset/summarized/dataset_summarized.json", 5)