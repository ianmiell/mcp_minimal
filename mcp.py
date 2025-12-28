import argparse
import json
import socketserver


def process_request(req):
    """Return a JSON-RPC response dict or None if the method is unsupported."""
    method = req.get("method")
    id_ = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "minimal-mcp",
                    "version": "0.1.1"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "tools": [
                    {
                        "name": "hello",
                        "description": "Returns a greeting",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "goodbye",
                        "description": "Says goodbye",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }

    if method == "tools/call":
        name = req["params"]["name"]
        args = req["params"].get("arguments", {})

        if name == "hello":
            result = f"Hello, {args.get('name', 'world')}!"
        elif name == "goodbye":
            result = f"Goodbye, {args.get('name', 'friend')}!"
        else:
            result = "Unknown tool"

        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "content": [
                    {"type": "text", "text": result}
                ]
            }
        }

    return None


class JSONRPCServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


class JSONRPCHandler(socketserver.StreamRequestHandler):
    def handle(self):
        # Each line is a JSON-RPC request; responses are newline-delimited.
        for line in self.rfile:
            raw = line.decode().strip()
            if not raw:
                continue

            try:
                req = json.loads(raw)
            except json.JSONDecodeError:
                continue

            resp = process_request(req)
            if resp is None:
                continue

            payload = json.dumps(resp) + "\n"
            self.wfile.write(payload.encode())
            self.wfile.flush()


def main():
    parser = argparse.ArgumentParser(description="Minimal MCP server over TCP.")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on (default: 8765)")
    args = parser.parse_args()

    with JSONRPCServer((args.host, args.port), JSONRPCHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
