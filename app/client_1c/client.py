import types
import httpx
from typing import Any, Dict, List, Optional
from mcp import types
from app.config import settings


class OneCClient:

    def __init__(self):
        self.base_url = settings.ones_base_url
        self.auth = httpx.BasicAuth(
            username=settings.ones_username,
            password=settings.ones_password
        )
        self.client = self.create_ini()

    def create_ini(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            auth=self.auth,
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )

    async def health(self):
        url = f"{self.base_url}/mcp/health"

        response = await self.client.get(url)
        response.raise_for_status()

        mcp_response = response.json()

        if "error" in mcp_response:
            error = mcp_response["error"]
            raise Exception(f"JSON-RPC ошибка {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")
        return mcp_response.get("status", {})

    async def call_mcp(self,
                       method: str,
                       params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/mcp"

        mpc_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }

        response = await self.client.post(url, json=mpc_request)
        response.raise_for_status()

        mpc_response = response.json()

        # Проверяем на ошибки JSON-RPC
        if "error" in mpc_response:
            error = mpc_response["error"]
            raise Exception(
            f"JSON-RPC ошибка {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")

        return mpc_response.get("result", {})

    async def tools_list(self):
        result = await self.call_mcp("tools/list")
        tools_data = result.get("tools", [])

        return tools_data

    async def call_tool(self, name: str, arguments: Dict[str, Any]):

        result = await self.call_mcp("tools/call", {
            "name": name,
            "arguments": arguments
        })

        return result

    async def resources_list(self) -> List:
        result = await self.call_mcp("resources/list")
        resources_data = result.get("resources", [])

        resources = []
        for resource_data in resources_data:
            resource = types.Resource(
                uri=resource_data["uri"],
                name=resource_data.get("name", ""),
                description=resource_data.get("description", ""),
                mimeType=resource_data.get("mimeType")
            )
            resources.append(resource)

        return resources