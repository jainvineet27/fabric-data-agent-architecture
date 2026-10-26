import os
import json
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from openai import OpenAI

load_dotenv()

# ==============================================================================
# 1. MCP Server URL
# ==============================================================================
# Hamara Unified Server (server.py) chal raha hai port 8000 par.
# Saare tools (SSMS ke 3 tools + Fabric ka 1 tool) isi ek server ke paas hain!
SERVER_URL = "http://127.0.0.1:8000/mcp"


# ==============================================================================
# 2. Main Client Flow (100% Clean & Standard MCP)
# ==============================================================================
async def main(user_query: str):
    print(f"\n[1/3] Connecting to MCP Server at {SERVER_URL}...")

    # Step 1: Server se connect karo
    async with Client(SERVER_URL) as mcp_client:

        # Step 2: Server se saare available tools maango
        tools = await mcp_client.list_tools()
        print(f"[2/3] Total {len(tools)} tools server se mile:")
        for t in tools:
            print(f"  - {t.name}: {t.description.strip()}")

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("\n[NOTE] OPENAI_API_KEY nahi mila. Direct tool test:")
            result = await mcp_client.call_tool("list_ssms_tables", {})
            print(result.content[0].text)
            return

        # Step 3: Tools ko OpenAI format me convert karo
        openai_tools = []
        for tool in tools:
            parameters = getattr(tool, "input_schema", None) or getattr(tool, "inputSchema", {"type": "object", "properties": {}})
            openai_tools.append({
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": parameters,
            })

        # Step 4: Simple System Prompt
        system_prompt = (
            "You are a helpful Data Assistant with access to tools via MCP:\n"
            "1. For local SQL Server tables and queries, use `list_ssms_tables`, `get_ssms_table_schema`, and `execute_ssms_query`.\n"
            "2. For enterprise lakehouse or active certificates data, use `ask_fabric_agent`.\n"
            "3. If a question needs both, call both tools and combine the answer.\n"
            "Always call the tools to get real data before answering."
        )

        openai_client = OpenAI(api_key=openai_api_key)
        model_name = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

        print(f"\n[3/3] Sending query to OpenAI: '{user_query}'...")
        response = openai_client.responses.create(
            model=model_name,
            instructions=system_prompt,
            input=user_query,
            tools=openai_tools,
        )
        response_id = response.id

        # Step 5: Tool Calling Loop (Pure & Simple!)
        while True:
            tool_outputs = []
            for item in response.output:
                if item.type == "function_call":
                    tool_name = item.name
                    arguments = json.loads(item.arguments)

                    print(f"\n>> OpenAI ne tool maanga: {tool_name}")
                    print(f">> Arguments: {arguments}")

                    # Seedha MCP Server ko call karo (Server khud sambhalega ki SSMS hai ya Fabric!)
                    result = await mcp_client.call_tool(tool_name, arguments)

                    # Result se clean text nikalna
                    clean_text = result.content[0].text if hasattr(result, "content") and result.content else str(result)
                    print(f">> Tool Output:\n{clean_text[:200]}...\n")

                    # Output wapis OpenAI ko bhejo
                    tool_outputs.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": clean_text,
                    })

            # Agar koi tool call nahi bacha, loop khatam
            if not tool_outputs:
                break

            # Next response maango with previous_response_id
            response = openai_client.responses.create(
                model=model_name,
                input=tool_outputs,
                previous_response_id=response_id,
            )
            response_id = response.id

        print("\n" + "="*50)
        print("FINAL ANSWER:")
        print("="*50)
        print(response.output_text)


if __name__ == "__main__":
    user_query = input("Kindly enter your questions: ").strip()
    if not user_query:
        user_query = "Show all tables available in my local database"
    asyncio.run(main(user_query))