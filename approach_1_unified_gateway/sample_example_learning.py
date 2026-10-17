"""
================================================================================
MASTERCLASS: MCP (Model Context Protocol) in Python
File: sample_example_learning.py
================================================================================

INTERVIEW KA DAR KHATAM KARO:
"Agar interviewer bole: 'Python me MCP Client likh ke dikhao' toh kya likhoge?"

Interviewer ko koi complicated code (hasattr, getattr, schema, properties) NAHI chahiye.
MCP ka basic client sirf 4 LINES ka hota hai:

    1. Connect karo:      async with Client(...) as client:
    2. Tools maango:          tools = await client.list_tools()
    3. Tool chalao:           result = await client.call_tool("tool_name", {"arg": "value"})
    4. Result padho:          print(result.content[0].text)

Yeh file 100% self-contained hai. Aap isse bina kisi external server ke direct
run karke dekh sakte hain!
================================================================================
"""

import asyncio
from fastmcp import FastMCP, Client


# ==============================================================================
# LEVEL 1: IN-MEMORY DEMO (Sabse Best tareeka concept samajhne ka!)
# Koi SSMS, koi Fabric, koi URL nahi chahiye. Seedha Python me chalta hai!
# ==============================================================================

# Step A: Server banate hain aur 2 Tools register karte hain
demo_server = FastMCP("Interview-Learning-Server")

@demo_server.tool()
def add_numbers(a: int, b: int) -> int:
    """Do numbers ko add karta hai."""
    return a + b

@demo_server.tool()
def get_user_balance(username: str) -> str:
    """User ka bank balance batata hai."""
    return f"User '{username}' ka balance hai: Rs. 25,000"


# Step B: MCP Client likhte hain jo in tools ko call karega
async def level_1_in_memory_learning():
    print("\n" + "="*50)
    print("--- LEVEL 1: IN-MEMORY MCP CLIENT (Whiteboard Code) ---")
    print("="*50)

    # 1. Connect to Server
    async with Client(demo_server) as client:
        
        # 2. Server se pucho: "Tumhare paas kaunse tools hain?"
        tools = await client.list_tools()
        print(f"\n[Step 1] Server ne {len(tools)} tools diye:")
        for t in tools:
            print(f"    - Tool Name: '{t.name}' | Description: {t.description}")

        # 3. Tool ko Call karo: 'add_numbers' with arguments a=15, b=25
        print("\n[Step 2] Calling tool 'add_numbers' with {'a': 15, 'b': 25}...")
        result1 = await client.call_tool("add_numbers", {"a": 15, "b": 25})
        
        # 4. Result print karo (FastMCP result.content[0].text deta hai)
        print(f"    --> Tool Output: {result1.content[0].text}")

        # Example 2: Call another tool with string parameter
        print("\n[Step 3] Calling tool 'get_user_balance' with {'username': 'vineet'}...")
        result2 = await client.call_tool("get_user_balance", {"username": "vineet"})
        print(f"    --> Tool Output: {result2.content[0].text}")


# ==============================================================================
# LEVEL 2: LOCAL SERVER (HTTP URL se connect karna - jaise SSMS Server)
# ==============================================================================
async def level_2_http_server_concept():
    print("\n" + "="*50)
    print("--- LEVEL 2: LOCAL HTTP SERVER (SSMS Database) ---")
    print("="*50)

    # Jab server alag process me chal raha ho (e.g. server.py on port 8000)
    server_url = "http://127.0.0.1:8000/mcp"

    print("Concept: Client seedha HTTP URL pass karta hai:")
    print(f'   async with Client("{server_url}") as client:')
    print('       tools = await client.list_tools()')
    print('       result = await client.call_tool("list_ssms_tables", {})')
    print('       print(result.content[0].text)')


# ==============================================================================
# LEVEL 3: CLOUD SERVER (Bearer Token ke sath - jaise Microsoft Fabric)
# ==============================================================================
async def level_3_fabric_cloud_concept():
    print("\n" + "="*50)
    print("--- LEVEL 3: CLOUD MCP SERVER (Microsoft Fabric) ---")
    print("="*50)

    print("Concept: Cloud me sirf 1 cheez extra aati hai: Authorization Token!")
    print("""
    from fastmcp.client.transports import StreamableHttpTransport

    # 1. Transport banate hain headers ke sath:
    transport = StreamableHttpTransport(
        url="https://api.fabric.microsoft.com/v1/.../agent",
        headers={"Authorization": "Bearer YOUR_AZURE_TOKEN"}
    )

    # 2. Baki code bilkul Level 1 aur 2 jaisa hi hai:
    async with Client(transport) as client:
        result = await client.call_tool("fabric_data_agent", {"user_question": "Top 5 countries"})
        print(result.content[0].text)
    """)


# ==============================================================================
# MAIN: Run this file directly to test!
# ==============================================================================
if __name__ == "__main__":
    # Level 1 runs live right now without any server or database!
    asyncio.run(level_1_in_memory_learning())

    # Level 2 & 3 print concepts
    asyncio.run(level_2_http_server_concept())
    asyncio.run(level_3_fabric_cloud_concept())

    print("\n" + "="*50)
    print("SUCCESS: MCP bilkul simple hai!")
    print("="*50)
