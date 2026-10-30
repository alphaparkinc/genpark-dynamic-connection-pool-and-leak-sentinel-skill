"""MCP server for Dynamic Connection Pool & Leak Sentinel."""
import sys
import json
from client import DynamicConnectionPoolSentinel

def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "acquire_connection",
                    "description": "Acquire or burst-expand database connection from pool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "client_label": {"type": "string"},
                            "active_count": {"type": "integer"},
                            "max_pool_size": {"type": "integer", "default": 10},
                            "burst_limit": {"type": "integer", "default": 15},
                            "dynamic_expand": {"type": "boolean", "default": True}
                        },
                        "required": ["client_label", "active_count"]
                    }
                },
                {
                    "name": "detect_leaks",
                    "description": "Audit active leases for connection leaks and suggest reclaims",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "active_leases": {"type": "array"},
                            "max_idle_seconds": {"type": "number", "default": 30.0}
                        },
                        "required": ["active_leases"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "acquire_connection":
            out = DynamicConnectionPoolSentinel.acquire_connection(
                args.get("client_label", "unknown"),
                int(args.get("active_count", 0)),
                int(args.get("max_pool_size", 10)),
                int(args.get("burst_limit", 15)),
                bool(args.get("dynamic_expand", True))
            )
            return {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]}
        elif name == "detect_leaks":
            out = DynamicConnectionPoolSentinel.detect_leaks(
                args.get("active_leases", []),
                float(args.get("max_idle_seconds", 30.0))
            )
            return {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]}
    return {"error": "Unsupported method or tool"}

if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            print(json.dumps({"id": req.get("id"), "result": res}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
