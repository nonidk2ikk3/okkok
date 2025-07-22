from fastapi import FastAPI, HTTPException, status, Depends
import json
from datetime import datetime
from check import auth_check

# Global counter configuration
REQUEST_LIMIT = 5000
COUNTER_FILE = "/tmp/request_counter.json"
request_count = 0
last_reset = None

app = FastAPI()

def load_counter():
    """Load counter from file or initialize if doesn't exist"""
    global request_count, last_reset
    try:
        with open(COUNTER_FILE, 'r') as f:
            data = json.load(f)
            request_count = data.get('count', 0)
            last_reset = data.get('last_reset', None)
            print(f"Loaded counter: {request_count}/{REQUEST_LIMIT}")
    except (FileNotFoundError, json.JSONDecodeError):
        request_count = 0
        last_reset = None
        print("Initialized new counter")

def save_counter():
    """Save counter to file"""
    try:
        with open(COUNTER_FILE, 'w') as f:
            json.dump({
                'count': request_count,
                'last_reset': last_reset or datetime.now().isoformat()
            }, f)
    except Exception as e:
        print(f"Warning: Could not save counter: {e}")

async def global_request_limiter():
    """
    Global dependency that limits requests across the entire app
    """
    global request_count
    
    if request_count >= REQUEST_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Global request limit of {REQUEST_LIMIT} reached. Current count: {request_count}"
        )
    
    request_count += 1
    print(f"Global request count: {request_count}/{REQUEST_LIMIT}")
    
    # Save every 10 requests to reduce I/O
    if request_count % 10 == 0:
        save_counter()

# Load counter on startup
load_counter()

@app.get("/")
async def root():
    return {
        "greeting": "Hello, World!", 
        "message": "Welcome to FastAPI!",
        "request_count": request_count,
        "limit": REQUEST_LIMIT
    }

# Global status endpoint
@app.get("/status")
async def get_global_status():
    """Get current global request count status"""
    return {
        "current_count": request_count,
        "limit": REQUEST_LIMIT,
        "remaining": max(0, REQUEST_LIMIT - request_count),
        "status": "active" if request_count < REQUEST_LIMIT else "limit_reached",
        "last_reset": last_reset,
        "platform": "Railway"
    }

# Global reset endpoint
@app.post("/reset")
async def reset_global_counter():
    """Reset the global request counter"""
    global request_count, last_reset
    request_count = 0
    last_reset = datetime.now().isoformat()
    save_counter()
    return {"message": "Global counter reset", "current_count": request_count}

# Health check endpoint for Railway
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "platform": "Railway",
        "counter": request_count,
        "limit": REQUEST_LIMIT
    }

# Apply global limit to auth_check router
auth_check.dependencies.append(Depends(global_request_limiter))

# Include the auth_check router
app.include_router(auth_check)
