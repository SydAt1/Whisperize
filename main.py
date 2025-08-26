import uvicorn
import os
import sys

def main():
    """
    Main entry point for the audio-to-text-summarizer backend.
    """
    print("🎵 Starting Audio-to-Text-Summarizer Backend...")
    print("=" * 50)
    
    # Environment configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"📝 Log Level: {log_level}")
    print("=" * 50)
    
    # CORS origins info
    print("🔗 CORS enabled for:")
    print("   - http://localhost:3000 (React)")
    print("   - http://localhost:8080 (Alt dev)")
    print("   - http://localhost:5173 (Vite)")
    print("   - http://127.0.0.1:* (Local IPs)")
    print("=" * 50)
    
    # API endpoints info
    print("🚀 Available endpoints:")
    print(f"   - GET  http://{host}:{port}/")
    print(f"   - GET  http://{host}:{port}/health") 
    print(f"   - POST http://{host}:{port}/process-audio/")
    print(f"   - GET  http://{host}:{port}/docs (API docs)")
    print(f"   - GET  http://{host}:{port}/app (Frontend)")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "backend.routes.endpoints:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True,
            # Additional uvicorn configuration for production
            workers=1 if reload else 4,  # Multiple workers in production
            # SSL configuration (uncomment for HTTPS)
            # ssl_keyfile="path/to/keyfile.key",
            # ssl_certfile="path/to/certfile.crt",
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()