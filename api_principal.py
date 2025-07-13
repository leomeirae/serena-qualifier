from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Serena Qualifier API",
    description="API principal do sistema Serena Qualifier",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
KESTRA_API_URL = os.getenv("KESTRA_API_URL", "http://kestra:8081")
WEBHOOK_SERVICE_URL = os.getenv("WEBHOOK_SERVICE_URL", "http://webhook-service:8001")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Serena Qualifier API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "api": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Check Kestra connection
    try:
        response = requests.get(f"{KESTRA_API_URL}/api/v1/stats", timeout=5)
        health_status["services"]["kestra"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        health_status["services"]["kestra"] = f"error: {str(e)}"
    
    # Check webhook service connection
    try:
        response = requests.get(f"{WEBHOOK_SERVICE_URL}/", timeout=5)
        health_status["services"]["webhook"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        health_status["services"]["webhook"] = f"error: {str(e)}"
    
    return health_status

@app.post("/api/v1/lead/create")
async def create_lead(lead_data: dict):
    """Create a new lead and trigger the activation flow"""
    try:
        # Forward to webhook service for processing
        webhook_url = f"{WEBHOOK_SERVICE_URL}/webhook/lead/create"
        
        logger.info(f"Forwarding lead creation to webhook service: {webhook_url}")
        
        response = requests.post(
            webhook_url,
            json=lead_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Webhook service error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to process lead")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service communication error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/kestra/flows")
async def list_kestra_flows():
    """List all Kestra flows"""
    try:
        response = requests.get(f"{KESTRA_API_URL}/api/v1/flows", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch Kestra flows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch flows: {str(e)}")

@app.get("/api/v1/kestra/executions")
async def list_kestra_executions():
    """List recent Kestra executions"""
    try:
        response = requests.get(f"{KESTRA_API_URL}/api/v1/executions", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch Kestra executions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch executions: {str(e)}")

@app.get("/api/v1/system/info")
async def system_info():
    """Get system information"""
    return {
        "service": "Serena Qualifier API",
        "version": "1.0.0",
        "environment": {
            "kestra_url": KESTRA_API_URL,
            "webhook_url": WEBHOOK_SERVICE_URL
        },
        "domains": {
            "kestra": "https://kestra.darwinai.com.br",
            "webhook": "https://webhookkestra.darwinai.com.br",
            "api": "https://api.darwinai.com.br"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001) 