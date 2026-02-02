from fastmcp import FastMCP
from main import app # Import your logic

# This converts your entire FastAPI app into an MCP server automatically
mcp = FastMCP.from_fastapi(app)

if __name__ == "__main__":
    mcp.run()