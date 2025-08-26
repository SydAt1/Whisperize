
"""
CORS (Cross-Origin Resource Sharing) configuration for the Audio Processing API.
This file manages allowed origins, methods, and headers for cross-origin requests.
"""

import os
from typing import List

# Environment-based configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Development CORS origins
DEVELOPMENT_ORIGINS = [
    "http://localhost:3000",      # Create React App default
    "http://localhost:8080",      # Alternative dev server
    "http://127.0.0.1:3000",     # Local IP for React
    "http://127.0.0.1:8080",     # Local IP alternative
    "http://localhost:5173",      # Vite dev server default
    "http://127.0.0.1:5173",     # Local IP for Vite
    "http://localhost:4200",      # Angular CLI default
    "http://127.0.0.1:4200",     # Local IP for Angular
    "http://localhost:8081",      # Vue CLI default
    "http://127.0.0.1:8081",     # Local IP for Vue
]

# Production CORS origins (add your production domains here)
PRODUCTION_ORIGINS = [
    # "https://yourdomain.com",
    # "https://www.yourdomain.com",
    # "https://app.yourdomain.com",
]

# Staging/Testing origins
STAGING_ORIGINS = [
    # "https://staging.yourdomain.com",
    # "https://test.yourdomain.com",
]

def get_cors_origins() -> List[str]:
    """
    Get CORS origins based on environment.
    
    Returns:
        List[str]: List of allowed origins
    """
    if ENVIRONMENT == "production":
        return PRODUCTION_ORIGINS
    elif ENVIRONMENT == "staging":
        return STAGING_ORIGINS + DEVELOPMENT_ORIGINS
    else:
        # Development environment - allow all development origins
        return DEVELOPMENT_ORIGINS

def get_cors_config() -> dict:
    """
    Get complete CORS configuration.
    
    Returns:
        dict: CORS configuration dictionary
    """
    return {
        "allow_origins": get_cors_origins(),
        "allow_credentials": True,
        "allow_methods": [
            "GET",
            "POST", 
            "PUT",
            "DELETE",
            "OPTIONS",
            "HEAD",
            "PATCH"
        ],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Language", 
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Origin",
            "Cache-Control",
            "Pragma",
            "X-CSRF-Token",
            "X-Forwarded-For",
            "X-Forwarded-Proto",
            "User-Agent",
        ],
        "expose_headers": [
            "Content-Disposition",
            "Content-Length",
            "Content-Type",
        ],
        "max_age": 3600,  # Cache preflight response for 1 hour
    }

# Custom CORS origins from environment variable
CUSTOM_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
if CUSTOM_ORIGINS and CUSTOM_ORIGINS[0]:  # Check if not empty
    DEVELOPMENT_ORIGINS.extend([origin.strip() for origin in CUSTOM_ORIGINS])

# Debug function
def print_cors_info():
    """Print CORS configuration information for debugging."""
    config = get_cors_config()
    print("🔗 CORS Configuration:")
    print(f"   Environment: {ENVIRONMENT}")
    print(f"   Allowed Origins: {len(config['allow_origins'])}")
    for origin in config['allow_origins']:
        print(f"     - {origin}")
    print(f"   Allowed Methods: {', '.join(config['allow_methods'])}")
    print(f"   Max Age: {config['max_age']}s")

if __name__ == "__main__":
    print_cors_info()