#!/usr/bin/env python3

"""
Metabase MCP Server for Docker
A clean implementation of a Metabase MCP server using the standard MCP SDK.
Designed to run in a Docker container with stdio transport for Claude Desktop.
"""

import os
import json
import sys
import logging
from typing import Dict, List, Optional

# Import MCP SDK components
from mcp.server.fastmcp import FastMCP
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("metabase-server")

METABASE_URL = os.environ.get("METABASE_URL")
METABASE_USERNAME = os.environ.get("METABASE_USERNAME")
METABASE_PASSWORD = os.environ.get("METABASE_PASSWORD")

if not METABASE_URL or not METABASE_USERNAME or not METABASE_PASSWORD:
    raise ValueError("METABASE_URL, METABASE_USERNAME, and METABASE_PASSWORD environment variables are required")

mcp = FastMCP("metabase-server")

http_client = httpx.AsyncClient(
    base_url=METABASE_URL,
    headers={"Content-Type": "application/json"}
)
session_token = None

async def get_session_token():
    """Authenticate with Metabase and get a session token"""
    global session_token
    
    if session_token:
        return session_token
    
    logger.info("Authenticating with Metabase...")
    try:
        response = await http_client.post(
            "/api/session",
            json={
                "username": METABASE_USERNAME,
                "password": METABASE_PASSWORD
            }
        )
        response.raise_for_status()
        data = response.json()
        
        session_token = data["id"]
        
        http_client.headers["X-Metabase-Session"] = session_token
        
        logger.info("Successfully authenticated with Metabase")
        return session_token
    except Exception as error:
        logger.error(f"Authentication failed: {str(error)}")
        raise Exception(f"Failed to authenticate with Metabase: {str(error)}")

# ===== TOOLS =====

@mcp.tool()
async def list_dashboards() -> str:
    """List all dashboards in Metabase"""
    await get_session_token()
    
    try:
        response = await http_client.get("/api/dashboard")
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as error:
        logger.error(f"Failed to list dashboards: {str(error)}")
        raise Exception(f"Failed to list dashboards: {str(error)}")

@mcp.tool()
async def list_cards() -> str:
    """List all questions/cards in Metabase"""
    await get_session_token()
    
    try:
        response = await http_client.get("/api/card")
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as error:
        logger.error(f"Failed to list cards: {str(error)}")
        raise Exception(f"Failed to list cards: {str(error)}")

@mcp.tool()
async def list_databases() -> str:
    """List all databases in Metabase"""
    await get_session_token()
    
    try:
        response = await http_client.get("/api/database")
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as error:
        logger.error(f"Failed to list databases: {str(error)}")
        raise Exception(f"Failed to list databases: {str(error)}")

@mcp.tool()
async def execute_card(card_id: int, parameters: Optional[Dict] = None) -> str:
    """Execute a Metabase question/card and get results
    
    Args:
        card_id: ID of the card/question to execute
        parameters: Optional parameters for the query
    """
    await get_session_token()
    
    if parameters is None:
        parameters = {}
    
    try:
        response = await http_client.post(
            f"/api/card/{card_id}/query",
            json={"parameters": parameters}
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as error:
        logger.error(f"Failed to execute card {card_id}: {str(error)}")
        raise Exception(f"Failed to execute card: {str(error)}")

@mcp.tool()
async def get_dashboard_cards(dashboard_id: int) -> str:
    """Get all cards in a dashboard
    
    Args:
        dashboard_id: ID of the dashboard
    """
    await get_session_token()
    
    try:
        response = await http_client.get(f"/api/dashboard/{dashboard_id}")
        response.raise_for_status()
        data = response.json()
        return json.dumps(data.get("cards", []), indent=2)
    except Exception as error:
        logger.error(f"Failed to get dashboard cards for {dashboard_id}: {str(error)}")
        raise Exception(f"Failed to get dashboard cards: {str(error)}")

@mcp.tool()
async def execute_query(database_id: int, query: str, native_parameters: Optional[List[Dict]] = None) -> str:
    """Execute a SQL query against a Metabase database
    
    Args:
        database_id: ID of the database to query
        query: SQL query to execute
        native_parameters: Optional parameters for the query
    """
    await get_session_token()
    
    if native_parameters is None:
        native_parameters = []
    
    # Build query request body
    query_data = {
        "type": "native",
        "native": {
            "query": query,
            "template_tags": {}
        },
        "parameters": native_parameters,
        "database": database_id
    }
    
    try:
        response = await http_client.post(
            "/api/dataset",
            json=query_data
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as error:
        logger.error(f"Failed to execute query on database {database_id}: {str(error)}")
        raise Exception(f"Failed to execute query: {str(error)}")

# ===== RESOURCES =====

@mcp.resource("metabase://dashboard/{id}")
async def get_dashboard(id: str) -> str:
    """Get a Metabase dashboard by its ID"""
    await get_session_token()
    
    try:
        response = await http_client.get(f"/api/dashboard/{id}")
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as error:
        logger.error(f"Failed to get dashboard {id}: {str(error)}")
        raise Exception(f"Failed to get dashboard: {str(error)}")

@mcp.resource("metabase://card/{id}")
async def get_card(id: str) -> str:
    """Get a Metabase question/card by its ID"""
    await get_session_token()
    
    try:
        response = await http_client.get(f"/api/card/{id}")
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as error:
        logger.error(f"Failed to get card {id}: {str(error)}")
        raise Exception(f"Failed to get card: {str(error)}")

@mcp.resource("metabase://database/{id}")
async def get_database(id: str) -> str:
    """Get a Metabase database by its ID"""
    await get_session_token()
    
    try:
        response = await http_client.get(f"/api/database/{id}")
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as error:
        logger.error(f"Failed to get database {id}: {str(error)}")
        raise Exception(f"Failed to get database: {str(error)}")

if __name__ == "__main__":
    logger.info("Starting Metabase MCP server (Docker version)")
    mcp.run()
