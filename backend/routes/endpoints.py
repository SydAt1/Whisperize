from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from src.audio_to_text import chunk_audio, transcribe_chunks, save_dataset
from src.summarize import summarize_existing_dataset
from src.bullet_text import text_to_bullets
from src.decorators import json_to_text
from src.bullet_to_text import json_bullets_to_text
from util.recorder import record_audio
import tempfile
import shutil
import json

app = FastAPI(
    title="Audio Processing API",
    description="AI-powered audio transcription and summarization service",
    version="1.0.0"
)

# Import CORS configuration
try:
    from backend.config.CORS import get_cors_config
    cors_config = get_cors_config()
except ImportError:
    # Fallback configuration if config module doesn't exist
    cors_config = {
        "allow_origins": [
            "http://localhost:3000",
            "http://localhost:8080", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Accept", "Accept-Language", "Content-Language",
            "Content-Type", "Authorization", "X-Requested-With",
            "Origin", "Cache-Control", "Pragma",
        ],
    }

# CORS middleware configuration
app.add_middleware(CORSMiddleware, **cors_config)

# Serve the frontend static files directly from FastAPI
from fastapi.staticfiles import StaticFiles
try:
    # Mount static files directory
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    app.mount("/css", StaticFiles(directory="frontend/static/css"), name="css")
    app.mount("/js", StaticFiles(directory="frontend/static/js"), name="js")
    print("✅ Static files mounted successfully")
except (RuntimeError, FileNotFoundError) as e:
    print(f"⚠️  Static files directory not found: {e}")
    pass

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Audio Processing API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

# Health check endpoint for frontend
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "audio-processor"}

# Define directories
DATASET_DIR = "./dataset"
CHUNK_DIR = os.path.join(DATASET_DIR, "chunks")
OUTPUT_JSON = os.path.join(DATASET_DIR, "output", "dataset.json")
SUMMARIZED_JSON = os.path.join(DATASET_DIR, "summarized", "normal", "dataset_summarized.json")
SUMMARIZED_TXT = os.path.join(DATASET_DIR, "summarized", "normal", "dataset_summarized.txt")
BULLET_JSON = os.path.join(DATASET_DIR, "summarized", "bullet", "dataset_bullets.json")
BULLET_TXT = os.path.join(DATASET_DIR, "summarized", "bullet", "dataset_bullets.txt")
TEMP_DIR = os.path.join(os.getcwd(), "temp")  # Custom temp directory in project folder

# Create temp directory if it doesn't exist
os.makedirs(TEMP_DIR, exist_ok=True)

def process_audio(audio_path, output_format="plain", chunk_minutes=5, model_name="base"):
    # Ensure directories exist
    os.makedirs(CHUNK_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    os.makedirs(os.path.dirname(SUMMARIZED_JSON), exist_ok=True)
    os.makedirs(os.path.dirname(BULLET_JSON), exist_ok=True)

    # Step 1: Chunk audio
    chunk_files = chunk_audio(audio_path, CHUNK_DIR, chunk_minutes=chunk_minutes)

    # Step 2: Transcribe chunks with Whisper
    transcripts = transcribe_chunks(chunk_files, model_name=model_name)

    # Step 3: Save dataset
    save_dataset(transcripts, OUTPUT_JSON)

    if output_format == "plain":
        # Step 4: Summarize
        summarize_existing_dataset(OUTPUT_JSON, SUMMARIZED_JSON, chunk_minutes=chunk_minutes)

        # Step 5: Convert to text
        with open(SUMMARIZED_JSON, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        text_content = json_to_text(json_data, title="Summary")
        with open(SUMMARIZED_TXT, "w", encoding="utf-8") as f:
            f.write(text_content)
        return SUMMARIZED_TXT

    elif output_format == "bullet":
        # Step 4: Bulletize
        text_to_bullets(OUTPUT_JSON, BULLET_JSON, chunk_minutes=chunk_minutes)

        # Step 5: Convert to text
        with open(BULLET_JSON, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        text_content = json_bullets_to_text(json_data, title="Bullet Summary")
        with open(BULLET_TXT, "w", encoding="utf-8") as f:
            f.write(text_content)
        return BULLET_TXT

    else:
        raise ValueError("Invalid output_format. Choose 'plain' or 'bullet'.")

@app.post("/process-audio/")
async def process_audio_endpoint(
    file: UploadFile = File(None),
    record: bool = Form(False),
    output_format: str = Form("plain"),
    chunk_minutes: int = Form(5),
    model_name: str = Form("base")
):
    """
    Process audio file or record audio and return processed text file.
    
    - **file**: Audio file to process (optional if record=True)
    - **record**: Whether to record audio instead of using uploaded file
    - **output_format**: 'plain' for summary or 'bullet' for bullet points
    - **chunk_minutes**: Duration of each chunk in minutes (1-30)
    - **model_name**: Whisper model to use ('base', 'small', 'medium', 'large')
    """
    import os

    temp_audio_path = None
    try:
        # Create a temporary file in your TEMP_DIR
        with tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix=".wav") as temp_audio:
            temp_audio_path = temp_audio.name

        # If recording
        if record:
            record_audio(filename=temp_audio_path)
        else:
            if not file:
                return {"error": "No audio file provided and record not enabled"}
            
            # Validate file type
            if not file.content_type.startswith('audio/'):
                return {"error": "Invalid file type. Please upload an audio file."}
            
            # Write uploaded file to temp file
            with open(temp_audio_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        # Process the audio
        output_file = process_audio(temp_audio_path, output_format, chunk_minutes, model_name)

        # Return the result
        return FileResponse(
            path=output_file,
            media_type="text/plain",
            filename=os.path.basename(output_file),
            headers={
                "Access-Control-Expose-Headers": "Content-Disposition",
                "Content-Disposition": f"attachment; filename={os.path.basename(output_file)}"
            }
        )

    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

    finally:
        # Clean up the temporary audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

# Serve the frontend HTML file
@app.get("/app")
async def serve_frontend():
    """Serve the frontend application"""
    try:
        return FileResponse('frontend/main.html', media_type='text/html')
    except FileNotFoundError:
        return {"error": "Frontend not found. Please create 'frontend/index.html' file."}

# Root route can also serve the frontend
@app.get("/")
async def root():
    """Serve the frontend application or API info"""
    try:
        # Try to serve frontend first
        return FileResponse('frontend/main.html', media_type='text/html')
    except FileNotFoundError:
        # Fallback to API info
        return {
            "message": "Audio Processing API is running",
            "status": "healthy", 
            "version": "1.0.0",
            "frontend_url": "/app",
            "docs_url": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)