import os
from dotenv import load_dotenv, find_dotenv
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import asyncio 

load_dotenv(find_dotenv())

WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID", "2e818aee-d04a-458d-ae52-53fed65c8c60")
DATA_AGENT_ID = os.getenv("FABRIC_DATA_AGENT_ID", "1457ceb4-59c4-451b-9781-57acaae18357")

def get_fabric_headers():
    # 1. Agar user ne direct .env me FABRIC_BEARER_TOKEN diya hai:
    direct_token = os.getenv("FABRIC_BEARER_TOKEN")
    if direct_token:
        return {"Authorization": f"Bearer {direct_token.strip()}"}

    # 2. Azure Identity se token lena:
    try:
        cred = DefaultAzureCredential()
        token = cred.get_token("https://api.fabric.microsoft.com/.default")
        return {"Authorization": f"Bearer {token.token}"}
    except Exception:
        # 3. Fallback: Browser login popup
        cred = InteractiveBrowserCredential()
        token = cred.get_token("https://api.fabric.microsoft.com/.default")
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
    query="Tell me top 5 countries with highes active certificates also list down which lakehouse , schema and table have you used to provide this information "
    result = asyncio.run(query_fabric_via_fastmcp_client(query))
    print(result)


