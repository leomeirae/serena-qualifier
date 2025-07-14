#!/usr/bin/env python3
"""
Coolify MCP Server - Enhanced Debug Version
Provides tools to interact with Coolify self-hosted instance
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/coolify_mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("=" * 50)
logger.info("COOLIFY MCP SERVER STARTING UP")
logger.info("=" * 50)

# Configuration with debug logging
BASE_URL = os.getenv("COOLIFY_BASE_URL", "https://coolify.darwinai.com.br")
TOKEN = os.getenv("COOLIFY_TOKEN", "Q2VEjCscl4DQN2quZLhYKuNgKRMVpV8TbDtjzlUs7ed62b2a")

logger.info(f"Configuration loaded:")
logger.info(f"  BASE_URL: {BASE_URL}")
logger.info(f"  TOKEN: {'*' * 20}...{TOKEN[-10:] if TOKEN else 'NOT SET'}")
logger.info(f"  Python version: {sys.version}")
logger.info(f"  Working directory: {os.getcwd()}")
logger.info(f"  Script path: {__file__}")

# Initialize server
server = Server("coolify")
logger.info("MCP Server initialized with name: coolify")

class CoolifyClient:
    """Client for interacting with Coolify API"""
    
    def __init__(self, base_url: str = BASE_URL, token: str = TOKEN):
        self.base_url = base_url.rstrip('/')
        self.token = token
        logger.info(f"CoolifyClient initialized with base_url: {self.base_url}")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Coolify API"""
        url = f"{self.base_url}/api/v1{endpoint}"
        headers = self._get_headers()
        
        logger.debug(f"Making {method} request to: {url}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=30,
                **kwargs
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"data": response.text}
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {
                "error": "Request failed",
                "message": str(e)
            }

# Initialize client
coolify_client = CoolifyClient()
logger.info("CoolifyClient instance created")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Coolify tools"""
    logger.info("🔧 list_tools() called - returning 8 tools")
    
    tools = [
        Tool(
            name="coolify_health",
            description="Check Coolify health status",
            inputSchema={
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="list_applications",
            description="List all applications",
            inputSchema={
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_application",
            description="Get details of a specific application",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "description": "Application UUID"
                    }
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="start_application",
            description="Start an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "description": "Application UUID"
                    }
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="stop_application",
            description="Stop an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "description": "Application UUID"
                    }
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="restart_application",
            description="Restart an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "description": "Application UUID"
                    }
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="get_application_logs",
            description="Get application logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "description": "Application UUID"
                    }
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="deploy_application",
            description="Deploy an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "description": "Application UUID"
                    }
                },
                "required": ["uuid"]
            }
        ),
    ]
    
    logger.info(f"✅ Returning {len(tools)} tools to MCP client")
    for tool in tools:
        logger.debug(f"  - {tool.name}: {tool.description}")
    
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    logger.info(f"🚀 call_tool() invoked: {name} with arguments: {arguments}")
    
    try:
        # Health check
        if name == "coolify_health":
            logger.info("Executing coolify_health")
            result = coolify_client._make_request("GET", "/health")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # Applications
        elif name == "list_applications":
            logger.info("Executing list_applications")
            result = coolify_client._make_request("GET", "/applications")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_application":
            uuid = arguments.get("uuid")
            logger.info(f"Executing get_application with uuid: {uuid}")
            if not uuid:
                return [TextContent(type="text", text="Error: uuid is required")]
            result = coolify_client._make_request("GET", f"/applications/{uuid}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "start_application":
            uuid = arguments.get("uuid")
            logger.info(f"Executing start_application with uuid: {uuid}")
            if not uuid:
                return [TextContent(type="text", text="Error: uuid is required")]
            result = coolify_client._make_request("POST", f"/applications/{uuid}/start")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "stop_application":
            uuid = arguments.get("uuid")
            logger.info(f"Executing stop_application with uuid: {uuid}")
            if not uuid:
                return [TextContent(type="text", text="Error: uuid is required")]
            result = coolify_client._make_request("POST", f"/applications/{uuid}/stop")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "restart_application":
            uuid = arguments.get("uuid")
            logger.info(f"Executing restart_application with uuid: {uuid}")
            if not uuid:
                return [TextContent(type="text", text="Error: uuid is required")]
            result = coolify_client._make_request("POST", f"/applications/{uuid}/restart")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_application_logs":
            uuid = arguments.get("uuid")
            logger.info(f"Executing get_application_logs with uuid: {uuid}")
            if not uuid:
                return [TextContent(type="text", text="Error: uuid is required")]
            result = coolify_client._make_request("GET", f"/applications/{uuid}/logs")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "deploy_application":
            uuid = arguments.get("uuid")
            logger.info(f"Executing deploy_application with uuid: {uuid}")
            if not uuid:
                return [TextContent(type="text", text="Error: uuid is required")]
            result = coolify_client._make_request("POST", f"/applications/{uuid}/deploy")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            logger.error(f"Unknown tool requested: {name}")
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        logger.error(f"Tool call failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point"""
    logger.info("🎯 Starting Coolify MCP Server main()")
    logger.info(f"Base URL: {BASE_URL}")
    logger.info(f"Token configured: {'Yes' if TOKEN else 'No'}")
    
    # Test API connection
    try:
        logger.info("Testing API connection...")
        test_result = coolify_client._make_request("GET", "/health")
        logger.info(f"API test result: {test_result}")
    except Exception as e:
        logger.error(f"API test failed: {e}")
    
    logger.info("🚀 Entering stdio_server context...")
    
    # Run the server
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✅ stdio_server context entered successfully")
            logger.info("🔄 Starting server.run()...")
            
            await server.run(
                read_stream, 
                write_stream, 
                server.create_initialization_options()
            )
            
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("🎬 Script started as main module")
    logger.info(f"Command line args: {sys.argv}")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        sys.exit(1) 