from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import hashlib
import json

app = FastAPI(title="Live MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMAIL = "24f2006169@ds.study.iitm.ac.in".strip().lower()

TOOLS = [
    {
        "name": "solve_challenge",
        "description": "Solves MCP challenge",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

def compute_hash(challenge: str) -> str:
    hash_input = f"{challenge}:{EMAIL}".encode("utf-8")
    return hashlib.sha256(hash_input).hexdigest()[:16]

def get_challenge_from_request(request: Request, body_data: dict = None) -> str:
    # Check headers first (case-insensitive)
    for k, v in request.headers.items():
        if k.lower() == "x-exam-challenge":
            return v
    # Fallback to body params
    if body_data and isinstance(body_data, dict):
        if "challenge" in body_data:
            return str(body_data["challenge"])
        params = body_data.get("params", {})
        if isinstance(params, dict):
            if "challenge" in params:
                return str(params["challenge"])
            args = params.get("arguments", {})
            if isinstance(args, dict) and "challenge" in args:
                return str(args["challenge"])
    return ""

# --- JSON-RPC 2.0 Handler for MCP Clients ---
async def handle_jsonrpc(request: Request, body: dict):
    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "live-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "notifications/initialized":
        return Response(status_code=204)
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }
    elif method == "tools/call":
        challenge = get_challenge_from_request(request, body)
        solution = compute_hash(challenge)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": solution
                    }
                ]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method {method} not found"
            }
        }

@app.post("/mcp")
@app.post("/")
async def mcp_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    if isinstance(body, dict) and "method" in body:
        res = await handle_jsonrpc(request, body)
        if isinstance(res, Response):
            return res
        return JSONResponse(content=res)
    # If not JSON-RPC, fallback to tool list or tool call if header present
    challenge = get_challenge_from_request(request, body)
    if challenge:
        solution = compute_hash(challenge)
        return {"content": [{"type": "text", "text": solution}]}
    return {"tools": TOOLS}

@app.get("/mcp")
async def mcp_get(request: Request):
    return {"tools": TOOLS}

# --- Direct REST Endpoints ---
@app.get("/tools/list")
@app.post("/tools/list")
@app.get("/mcp/tools/list")
@app.post("/mcp/tools/list")
def list_tools():
    return {"tools": TOOLS}

@app.post("/tools/call")
@app.post("/mcp/tools/call")
async def call_tool(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    challenge = get_challenge_from_request(request, body)
    solution = compute_hash(challenge)
    return {"content": [{"type": "text", "text": solution}]}

@app.post("/initialize")
@app.post("/mcp/initialize")
def initialize(request: Request):
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "live-mcp-server", "version": "1.0.0"}
    }

@app.post("/notifications/initialized")
@app.post("/mcp/notifications/initialized")
def notifications_initialized():
    return Response(status_code=204)
