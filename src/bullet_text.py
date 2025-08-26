import json
from transformers import pipeline

# Load summarizer (BART or any summarization model)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def text_to_bullets(input_file, output_file, chunk_minutes=5):
    # Load dataset.json
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    bulletized = []
    for idx, entry in enumerate(data):
        start_min = idx * chunk_minutes
        end_min = (idx + 1) * chunk_minutes

        # Truncate input to 4000 characters
        chunk = entry["transcript_chunk"][:4000]

        # Convert to bullet points via summarization prompt
        bullet_prompt = f"Convert the following text into concise bullet points:\n{chunk}"
        bullets = summarizer(
            bullet_prompt,
            max_length=150, min_length=40, do_sample=False
        )[0]["summary_text"]

        # Prefix with time
        if idx == 0:
            prefixed = f"In the first {chunk_minutes} minutes:\n{bullets}"
        else:
            prefixed = f"In the {start_min}-{end_min} minutes:\n{bullets}"

        bulletized.append({
            "transcript_chunk": entry["transcript_chunk"],
            "bullets": prefixed
        })

    # Save new file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bulletized, f, indent=2, ensure_ascii=False)

    print(f"Bullet points saved to {output_file}")


if __name__ == "__main__":
    text_to_bullets(
        "./dataset/output/dataset.json",
        "./dataset/summarized/bullet/dataset_bullets.json",
        chunk_minutes=5
    )
