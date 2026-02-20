import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.environ.get("PORT", 8080))
    
    # Run uvicorn using the string reference to the app
    # This allows for more robust importing in various environments
    print(f"🚀 Starting server on port {port}...")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
