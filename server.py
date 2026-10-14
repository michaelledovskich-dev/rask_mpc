import os
import httpx
from fastmcp import FastMCP

# Load credentials from environment variables
CLIENT_ID = os.getenv("RASK_CLIENT_ID")
CLIENT_SECRET = os.getenv("RASK_CLIENT_SECRET")

TOKEN_URL = "https://rask-prod.auth.us-east-2.amazoncognito.com/oauth2/token"
API_BASE = "https://api.rask.ai"

mcp = FastMCP("Rask AI")

async def get_access_token() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("Missing RASK_CLIENT_ID or RASK_CLIENT_SECRET environment variables")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={
                "grant_type": "client_credentials",
                "scope": "api/source api/input api/output api/limit"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()["access_token"]

@mcp.tool
async def list_projects(name: str = "", limit: int = 10, offset: int = 0) -> dict:
    """List Rask projects. Optionally filter by name."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        params = {"limit": limit, "offset": offset}
        if name:
            params["name"] = name
        response = await client.get(
            f"{API_BASE}/v2/projects",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
        response.raise_for_status()
        return response.json()

@mcp.tool
async def get_project(project_id: str) -> dict:
    """Get details of a specific project (status + video/audio links)."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/v2/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

@mcp.tool
async def get_transcription(project_id: str) -> dict:
    """Get the full transcript segments (source + translated text, speakers, timestamps)."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/v2/projects/{project_id}/transcription",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

@mcp.tool
async def get_credits() -> dict:
    """Check remaining Rask credits."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/v2/credits",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
