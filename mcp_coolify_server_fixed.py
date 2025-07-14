#!/usr/bin/env python3
"""
Fixed MCP Server for Coolify API
Provides tools to interact with Coolify self-hosted instance
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urljoin

import httpx
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

# Default configuration
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 30

class CoolifyClient:
    """Client for interacting with Coolify API"""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL, token: str = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.api_base = f"{self.base_url}/api/v1"
        self.timeout = DEFAULT_TIMEOUT
        
        # Configure httpx client
        self.client = httpx.Client(
            timeout=self.timeout,
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Coolify API"""
        url = urljoin(self.api_base + "/", endpoint.lstrip("/"))
        
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204:
                return {"success": True, "message": "Operation completed successfully"}
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Request failed: {error_msg}")
            return {"error": error_msg, "status_code": e.response.status_code}
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(f"Request failed: {error_msg}")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Request failed: {error_msg}")
            return {"error": error_msg}


# Initialize server
server = Server("coolify")
coolify_client = None

def get_coolify_client():
    """Get or create Coolify client"""
    global coolify_client
    if coolify_client is None:
        base_url = os.getenv("COOLIFY_BASE_URL", DEFAULT_BASE_URL)
        token = os.getenv("COOLIFY_TOKEN")
        if not token:
            raise ValueError("COOLIFY_TOKEN environment variable is required")
        coolify_client = CoolifyClient(base_url, token)
    return coolify_client


@server.list_tools()
async def handle_list_tools():
    """List available Coolify tools"""
    tools = [
        # General
        Tool(
            name="coolify_health",
            description="Check Coolify health status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # Applications
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
                    "uuid": {"type": "string", "description": "Application UUID"}
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
                    "uuid": {"type": "string", "description": "Application UUID"}
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
                    "uuid": {"type": "string", "description": "Application UUID"}
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
                    "uuid": {"type": "string", "description": "Application UUID"}
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
                    "uuid": {"type": "string", "description": "Application UUID"}
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
                    "uuid": {"type": "string", "description": "Application UUID"}
                },
                "required": ["uuid"]
            }
        ),
        
        # Databases
        Tool(
            name="list_databases",
            description="List all databases",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_database",
            description="Get database details by UUID",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Database UUID"}
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="start_database",
            description="Start a database",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Database UUID"}
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="stop_database",
            description="Stop a database",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Database UUID"}
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="restart_database",
            description="Restart a database",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Database UUID"}
                },
                "required": ["uuid"]
            }
        ),
        
        # Services
        Tool(
            name="list_services",
            description="List all services",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_service",
            description="Get service details by UUID",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Service UUID"}
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="start_service",
            description="Start a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Service UUID"}
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="stop_service",
            description="Stop a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Service UUID"}
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="restart_service",
            description="Restart a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Service UUID"}
                },
                "required": ["uuid"]
            }
        ),
        
        # Servers
        Tool(
            name="list_servers",
            description="List all servers",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_server",
            description="Get server details by UUID",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Server UUID"}
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="get_server_resources",
            description="Get server resources",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Server UUID"}
                },
                "required": ["uuid"]
            }
        ),
        Tool(
            name="validate_server",
            description="Validate server connection",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Server UUID"}
                },
                "required": ["uuid"]
            }
        ),
        
        # Projects
        Tool(
            name="list_projects",
            description="List all projects",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_project",
            description="Get project details by UUID",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Project UUID"}
                },
                "required": ["uuid"]
            }
        ),
        
        # Deployments
        Tool(
            name="list_deployments",
            description="List all deployments",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_deployment",
            description="Get deployment details by UUID",
            inputSchema={
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Deployment UUID"}
                },
                "required": ["uuid"]
            }
        ),
        
        # Teams
        Tool(
            name="list_teams",
            description="List all teams",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_team",
            description="Get team details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Team ID"}
                },
                "required": ["id"]
            }
        ),
        
        # Resources
        Tool(
            name="list_resources",
            description="List all resources",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]
    
    return tools


@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls"""
    try:
        client = get_coolify_client()
        name = request.params.name
        arguments = request.params.arguments or {}
        
        # General endpoints
        if name == "coolify_health":
            result = client._make_request("GET", "/health")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Applications
        elif name == "list_applications":
            result = client._make_request("GET", "/applications")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_application":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/applications/{uuid}")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "start_application":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/applications/{uuid}/start")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "stop_application":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/applications/{uuid}/stop")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "restart_application":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/applications/{uuid}/restart")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_application_logs":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/applications/{uuid}/logs")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "deploy_application":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/applications/{uuid}/deploy")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Databases
        elif name == "list_databases":
            result = client._make_request("GET", "/databases")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_database":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/databases/{uuid}")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "start_database":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/databases/{uuid}/start")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "stop_database":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/databases/{uuid}/stop")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "restart_database":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/databases/{uuid}/restart")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Services
        elif name == "list_services":
            result = client._make_request("GET", "/services")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_service":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/services/{uuid}")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "start_service":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/services/{uuid}/start")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "stop_service":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/services/{uuid}/stop")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "restart_service":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/services/{uuid}/restart")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Servers
        elif name == "list_servers":
            result = client._make_request("GET", "/servers")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_server":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/servers/{uuid}")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_server_resources":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/servers/{uuid}/resources")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "validate_server":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/servers/{uuid}/validate")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Projects
        elif name == "list_projects":
            result = client._make_request("GET", "/projects")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_project":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/projects/{uuid}")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Deployments
        elif name == "list_deployments":
            result = client._make_request("GET", "/deployments")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_deployment":
            uuid = arguments.get("uuid")
            result = client._make_request("GET", f"/deployments/{uuid}")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Teams
        elif name == "list_teams":
            result = client._make_request("GET", "/teams")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "get_team":
            team_id = arguments.get("id")
            result = client._make_request("GET", f"/teams/{team_id}")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        # Resources
        elif name == "list_resources":
            result = client._make_request("GET", "/resources")
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
    
    except Exception as e:
        logger.error(f"Error in tool call '{request.params.name}': {str(e)}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    """Run the MCP server"""
    logger.info("Starting Coolify MCP Server")
    
    # Log configuration
    base_url = os.getenv("COOLIFY_BASE_URL", DEFAULT_BASE_URL)
    token = os.getenv("COOLIFY_TOKEN", "NOT_SET")
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Token configured: {'Yes' if token != 'NOT_SET' else 'No'}")
    
    # Initialize server options
    init_options = server.create_initialization_options()
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 