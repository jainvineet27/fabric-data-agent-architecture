import os
import json
import base64
from dotenv import load_dotenv, find_dotenv
from azure.identity import InteractiveBrowserCredential
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import asyncio 

load_dotenv(find_dotenv())

WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID", "2e818aee-d04a-458d-ae52-53fed65c8c60")
DATA_AGENT_ID = os.getenv("FABRIC_DATA_AGENT_ID", "f5ef10da-5270-4866-979a-043f55d89f9b")

# Created once so the sign-in popup appears only the first time
_credential = None

def get_fabric_headers():
    global _credential
    # Optional: paste a token in .env instead of signing in
    direct_token = os.getenv("FABRIC_BEARER_TOKEN")
    if direct_token:
        return {"Authorization": f"Bearer {direct_token.strip()}"}

    # Always use the browser popup so the token belongs to the account that owns the Data Agent
    if _credential is None:
        _credential = InteractiveBrowserCredential()
    token = _credential.get_token("https://api.fabric.microsoft.com/.default")

    # Show which account is used; "entity not found" usually means the wrong account
    payload = token.token.split(".")[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    print(f">> Signed in as: {claims.get('upn') or claims.get('unique_name')}")

    return {"Authorization": f"Bearer {token.token}"}

async def query_fabric_via_fastmcp_client(question: str) -> str:
    """
    Uses fastmcp.Client (instead of low-level streamablehttp_client)
    to connect to the Microsoft Fabric Data Agent MCP endpoint.
    """
    if not WORKSPACE_ID or not DATA_AGENT_ID:
        return "Error: FABRIC_WORKSPACE_ID or FABRIC_DATA_AGENT_ID missing in .env"

    mcp_url = (
        f"https://api.fabric.microsoft.com/v1/mcp/workspaces/{WORKSPACE_ID}"
        f"/dataagents/{DATA_AGENT_ID}/agent"
    )

    transport = StreamableHttpTransport(url=mcp_url, headers=get_fabric_headers())
    ## yha pe error aa rhah ha ..

    async with Client(transport) as client:
        tools = await client.list_tools()
        if not tools:
            return "No tools exposed by Fabric Data Agent."

        # Fabric MCP server sirf 1 hi main tool expose karta hai
        fabric_tool = tools[0]

        # Fabric Data Agent expects 'user_question'
        schema = fabric_tool.input_schema if hasattr(fabric_tool, "input_schema") else getattr(fabric_tool, "inputSchema", {})
        props = schema.get("properties", {}) if isinstance(schema, dict) else {}
        param_name = next(iter(props.keys())) if props else "user_question"
        
        print(f">> Calling Fabric Tool: '{fabric_tool.name}' with parameter '{param_name}'")

        # Pass arguments with the discovered parameter name
        args = {param_name: question}
        if "user_question" not in args:
            args["user_question"] = question

        result = await client.call_tool(fabric_tool.name, args)

        # Clean text nikalna (same as my_own_client):
        if hasattr(result, "content") and result.content:
            clean_texts = [b.text for b in result.content if hasattr(b, "text") and b.text]
            if clean_texts:
                return "\n".join(clean_texts)

        return str(result)


if __name__=="__main__":
    query="Tell me top 5 countries with highest active certificates also list down which lakehouse , schema and table have you used to provide this information"
    result = asyncio.run(query_fabric_via_fastmcp_client(query))
    print(result)


