#!/usr/bin/env python3
"""
Working MCP Server for Coolify API
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
    CallToolRequest,
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://coolify.darwinai.com.br"
TOKEN = "Q2VEjCscl4DQN2quZLhYKuNgKRMVpV8TbDtjzlUs7ed62b2a"

class CoolifyClient:
    """Client for interacting with Coolify API"""
    
    def __init__(self, base_url: str = BASE_URL, token: str = TOKEN):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.api_base = f"{self.base_url}/api/v1"
        self.timeout = 30
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Coolify API"""
        url = f"{self.api_base}{endpoint}"
        headers = self._get_headers()
        
        logger.info(f"Making {method} request to {url}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Request failed with status {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}", "message": response.text}
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": "Request failed", "message": str(e)}

# Initialize server and client
server = Server("coolify")
coolify_client = CoolifyClient()

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available Coolify tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="coolify_health",
                description="Check Coolify health status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="list_applications",
                description="List all applications",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_application",
                description="Get application details by UUID",
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
            )
        ]
    )

@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls"""
    try:
        name = request.params.name
        arguments = request.params.arguments or {}
        
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        
        # Health check
        if name == "coolify_health":
            result = coolify_client._make_request("GET", "/health")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Applications
        elif name == "list_applications":
            result = coolify_client._make_request("GET", "/applications")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_application":
            uuid = arguments.get("uuid")
            if not uuid:
                return CallToolResult(content=[TextContent(type="text", text="Error: uuid is required")])
            result = coolify_client._make_request("GET", f"/applications/{uuid}")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "start_application":
            uuid = arguments.get("uuid")
            if not uuid:
                return CallToolResult(content=[TextContent(type="text", text="Error: uuid is required")])
            result = coolify_client._make_request("GET", f"/applications/{uuid}/start")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "stop_application":
            uuid = arguments.get("uuid")
            if not uuid:
                return CallToolResult(content=[TextContent(type="text", text="Error: uuid is required")])
            result = coolify_client._make_request("GET", f"/applications/{uuid}/stop")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "restart_application":
            uuid = arguments.get("uuid")
            if not uuid:
                return CallToolResult(content=[TextContent(type="text", text="Error: uuid is required")])
            result = coolify_client._make_request("GET", f"/applications/{uuid}/restart")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_application_logs":
            uuid = arguments.get("uuid")
            if not uuid:
                return CallToolResult(content=[TextContent(type="text", text="Error: uuid is required")])
            result = coolify_client._make_request("GET", f"/applications/{uuid}/logs")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "deploy_application":
            uuid = arguments.get("uuid")
            if not uuid:
                return CallToolResult(content=[TextContent(type="text", text="Error: uuid is required")])
            result = coolify_client._make_request("GET", f"/applications/{uuid}/deploy")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
            
    except Exception as e:
        logger.error(f"Error in call_tool: {e}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])

async def main():
    """Run the server"""
    logger.info("Starting Coolify MCP Server")
    logger.info(f"Base URL: {BASE_URL}")
    logger.info(f"Token configured: {'Yes' if TOKEN else 'No'}")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main()) 