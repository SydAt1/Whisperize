import os
import librosa
import whisper
import soundfile as sf
from tqdm import tqdm
import json

def chunk_audio(mp3_path, chunk_dir, chunk_minutes=5):
    os.makedirs(chunk_dir, exist_ok=True)

    # Load audio
    y, sr = librosa.load(mp3_path, sr=None)

    # 5 minutes in samples
    chunk_length = chunk_minutes * 60 * sr  

    # Split into chunks
    chunk_files = []
    for i in tqdm(range(0, len(y), chunk_length), desc="Chunking audio"):
        chunk_path = os.path.join(chunk_dir, f"chunk_{i//chunk_length}.wav")
        sf.write(chunk_path, y[i:i+chunk_length], sr, format="WAV")
        chunk_files.append(chunk_path)

    return chunk_files



def transcribe_chunks(chunk_files, model_name="base"):
    model = whisper.load_model(model_name)
    transcripts = []

    for i, chunk_path in enumerate(chunk_files):
        chunk_path = os.path.abspath(chunk_path)  # make absolute path
        print(f"Processing chunk: {chunk_path}")
        
        if not os.path.exists(chunk_path):
            print(f"File not found: {chunk_path}")
            continue
        
        result = model.transcribe(chunk_path)
        transcripts.append({
            "chunk_id": i,
            "transcript": result["text"].strip()
        })

    return transcripts

def save_dataset(transcripts, output_file):
    data = []
    for t in transcripts:
        data.append({
            "transcript_chunk": t["transcript"],
            "summary": ""   # leave empty for now
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved dataset to {output_file}")


if __name__ == "__main__":
    mp3_path = "./dataset/test.mp3"
    chunk_dir = "./dataset/chunks"
    output_file = "./dataset/output/dataset.json"

    # Step 1: split
    chunk_files = chunk_audio(mp3_path, chunk_dir, chunk_minutes=5)

    # Step 2: transcribe
    transcripts = transcribe_chunks(chunk_files, model_name="base")

    # Step 3: save
    save_dataset(transcripts, output_file)
