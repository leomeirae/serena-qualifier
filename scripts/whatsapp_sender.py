"""
WhatsApp Sender Module
Módulo para envio de mensagens template do WhatsApp Business API
"""

import os
import logging
from typing import List, Dict, Any, Optional
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp Sender Service",
    description="Service for sending WhatsApp template messages",
    version="1.0.0"
)

# Pydantic models
class WhatsAppWelcomeRequest(BaseModel):
    phone: str = Field(..., description="Phone number with country code (e.g., +5511999999999)")
    name: str = Field(..., description="Lead name for personalization")

class WhatsAppProsseguirRequest(BaseModel):
    phone: str = Field(..., description="Phone number with country code (e.g., +5511999999999)")
    lead_name: str = Field(..., description="Lead name for {{1}} parameter in template")

class WhatsAppResponse(BaseModel):
    success: bool
    message: str
    phone: str
    message_id: Optional[str] = None

# Environment variables
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_WELCOME_TEMPLATE_NAME = os.getenv("WHATSAPP_WELCOME_TEMPLATE_NAME")

# Validate required environment variables
if not WHATSAPP_API_TOKEN:
    logger.error("WHATSAPP_API_TOKEN environment variable is required")
    raise ValueError("WHATSAPP_API_TOKEN environment variable is required")

if not WHATSAPP_PHONE_NUMBER_ID:
    logger.error("WHATSAPP_PHONE_NUMBER_ID environment variable is required")
    raise ValueError("WHATSAPP_PHONE_NUMBER_ID environment variable is required")

if not WHATSAPP_WELCOME_TEMPLATE_NAME:
    logger.error("WHATSAPP_WELCOME_TEMPLATE_NAME environment variable is required")
    raise ValueError("WHATSAPP_WELCOME_TEMPLATE_NAME environment variable is required")


async def send_whatsapp_template_message(
    phone: str, 
    template_name: str, 
    components: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Send WhatsApp template message using Meta Business API
    
    Args:
        phone: Phone number with country code (e.g., +5511999999999)
        template_name: Name of the approved WhatsApp template
        components: List of template components (parameters, buttons, etc.)
    
    Returns:
        Dict containing success status and message_id if successful
    """
    try:
        # WhatsApp Business API endpoint (v19.0 as per official docs)
        url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        # Headers with Bearer token
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Message payload following official API structure
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": "pt_BR"  # Portuguese Brazil
                },
                "components": components
            }
        }
        
        logger.info(f"Sending WhatsApp template message to {phone}")
        logger.debug(f"Payload: {payload}")
        
        # Send POST request to WhatsApp API
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Check response status
        if response.status_code == 200:
            response_data = response.json()
            message_id = response_data.get("messages", [{}])[0].get("id")
            logger.info(f"✅ WhatsApp message sent successfully to {phone}, message_id: {message_id}")
            return {
                "success": True,
                "message_id": message_id,
                "response": response_data
            }
        else:
            logger.error(f"❌ Failed to send WhatsApp message to {phone}")
            logger.error(f"Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return {
                "success": False,
                "error": f"API Error {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request exception when sending WhatsApp message to {phone}: {str(e)}")
        return {
            "success": False,
            "error": f"Request exception: {str(e)}"
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error when sending WhatsApp message to {phone}: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


@app.post("/whatsapp/send_welcome", response_model=WhatsAppResponse)
async def send_welcome_message(request: WhatsAppWelcomeRequest):
    """
    FastAPI endpoint to send welcome message to WhatsApp
    
    Args:
        request: WhatsAppWelcomeRequest with phone and name
    
    Returns:
        WhatsAppResponse: Success status and details
    """
    try:
        logger.info(f"📱 Received welcome message request for {request.phone}")
        
        # Validate phone number format (basic validation)
        if not request.phone.startswith('+'):
            raise HTTPException(
                status_code=400, 
                detail="Phone number must include country code (e.g., +5511999999999)"
            )
        
        # Extrair o primeiro nome do lead
        first_name = request.name.split()[0] if request.name else ""
        # Montar components para template com {{1}}
        components = [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": first_name
                    }
                ]
            }
        ]
        
        # Send WhatsApp template message
        result = await send_whatsapp_template_message(
            phone=request.phone,
            template_name=WHATSAPP_WELCOME_TEMPLATE_NAME,
            components=components
        )
        
        if result["success"]:
            return WhatsAppResponse(
                success=True,
                message=f"Welcome message sent successfully to {request.phone}",
                phone=request.phone,
                message_id=result.get("message_id")
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send welcome message: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in send_welcome_message endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing welcome message request: {str(e)}"
        )


@app.post("/whatsapp/send_prosseguir", response_model=WhatsAppResponse)
async def send_prosseguir_message(request: WhatsAppProsseguirRequest):
    """
    FastAPI endpoint to send "prosseguir_com_solicitacao" template message
    
    Template content:
    Olá, {{1}}.
    
    Cadastro recebido! ✅
    
    Para ativar seu perfil, só precisamos confirmar alguns dados com você. É super rápido.
    
    Clique abaixo para dar o último passo.
    
    Args:
        request: WhatsAppProsseguirRequest with phone and lead_name
    
    Returns:
        WhatsAppResponse: Success status and details
    """
    try:
        logger.info(f"📱 Received prosseguir message request for {request.phone} (Lead: {request.lead_name})")
        
        # Validate phone number format (basic validation)
        if not request.phone.startswith('+'):
            raise HTTPException(
                status_code=400, 
                detail="Phone number must include country code (e.g., +5511999999999)"
            )
        
        # Template components with lead name for {{1}} parameter
        components = [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": request.lead_name
                    }
                ]
            }
        ]
        
        # Send WhatsApp template message using "prosseguir_com_solicitacao" template
        result = await send_whatsapp_template_message(
            phone=request.phone,
            template_name="prosseguir_com_solicitacao",
            components=components
        )
        
        if result["success"]:
            return WhatsAppResponse(
                success=True,
                message=f"Prosseguir message sent successfully to {request.phone} for lead {request.lead_name}",
                phone=request.phone,
                message_id=result.get("message_id")
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send prosseguir message: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in send_prosseguir_message endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing prosseguir message request: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "whatsapp-sender",
        "version": "1.0.0",
        "config": {
            "phone_number_id": WHATSAPP_PHONE_NUMBER_ID,
            "template_name": WHATSAPP_WELCOME_TEMPLATE_NAME,
            "api_token_configured": bool(WHATSAPP_API_TOKEN)
        }
    }


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "WhatsApp Sender Service",
        "version": "1.0.0",
        "description": "Service for sending WhatsApp template messages",
        "endpoints": {
            "send_welcome": "/whatsapp/send_welcome",
            "send_prosseguir": "/whatsapp/send_prosseguir",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting WhatsApp Sender Service on port 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001) 