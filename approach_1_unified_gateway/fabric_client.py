import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

load_dotenv()

WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID")
DATA_AGENT_ID = os.getenv("FABRIC_DATA_AGENT_ID")
credential = DefaultAzureCredential()

def get_fabric_headers():
    token = credential.get_token("https://api.fabric.microsoft.com/.default")
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

    async with Client(transport) as client:
        tools = await client.list_tools()
        if not tools:
            return "No tools exposed by Fabric Data Agent."
        
        target_tool = tools[0]
        # Discover the input parameter name dynamically (usually 'question' or 'query')
        props = target_tool.inputSchema.get("properties", {})
        question_arg = next(iter(props)) if props else "question"

        result = await client.call_tool(target_tool.name, {question_arg: question})
        
        # Extract text blocks from response
        answers = [block.text for block in result.content if getattr(block, "type", "") == "text"]
        return "\n".join(answers) if answers else str(result)
