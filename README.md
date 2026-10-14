# Hybrid MCP Architecture: Local SSMS + Microsoft Fabric Data Agent

Is project mein **2 अलग-अलग Approaches** ke folders hain, jisse aap apni pasand ke hisaab se setup chala sakein:

1. **`approach_1_unified_gateway/`**: 
   - Isme aapka Local Python Server **SSMS** se bhi juda hai aur `fastmcp.Client` (StreamableHttpTransport) ke zariye **Fabric Data Agent** ko bhi ek `@mcp.tool` banata hai.
   - VS Code Copilot (ya koi bhi MCP UI) sirf is **ek server** se baat karta hai.

2. **`approach_2_parallel_copilot_ui/`**:
   - Kyunki aapka Fabric Data Agent publish hone ke baad **Copilot UI mein pehle se available hai**, is approach mein Python server **sirf SSMS tools** (`list_ssms_tables`, `execute_ssms_query`, etc.) expose karta hai.
   - Copilot UI (VS Code Copilot Chat ya Copilot Studio) mein aap **Fabric Agent** aur **SSMS MCP Server** dono ko ek saath (parallel) use karte hain.

---

## Quick Start Steps

1. Dependencies install karein:
   ```bash
   pip install -r requirements.txt
   ```
2. Apni pasand ke folder (`approach_1_unified_gateway` ya `approach_2_parallel_copilot_ui`) mein jayein.
3. `.env.example` ko `.env` mein rename karein aur apni SQL Server / Fabric details bharein.
4. Server run karein:
   ```bash
   python server.py
   ```
5. Doosre terminal mein ngrok run karein (agar remote proxy chahiye):
   ```bash
   ngrok http 8000
   ```
