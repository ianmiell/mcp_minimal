import socket
import json
import requests

OLLAMA_MODEL = "qwen2.5:7b-instruct"
OLLAMA_URL = "http://localhost:11434/api/chat"

# ---- connect to MCP server over TCP ----
sock = socket.create_connection(("localhost", 8765))
sock_file = sock.makefile("rwb")

def mcp_call(method, params=None, id_=1):
    req = {
        "jsonrpc": "2.0",
        "id": id_,
        "method": method,
    }
    if params:
        req["params"] = params

    sock_file.write((json.dumps(req) + "\n").encode())
    sock_file.flush()

    return json.loads(sock_file.readline())

# ---- MCP handshake ----
mcp_call("initialize")
tools = mcp_call("tools/list")["result"]["tools"]

tool_desc = "\n".join(
    f"- {t['name']}: {t['description']}" for t in tools
)

system_prompt = f"""
You are an assistant that can call tools.

Available tools:
{tool_desc}

If a tool is useful, respond ONLY with JSON:
{{"tool": "<name>", "arguments": {{...}}}}

Otherwise respond normally.
""".strip()

user_prompt = "Say hello to Ian"

# ---- ask Ollama ----
resp = requests.post(
    OLLAMA_URL,
    json={
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    },
).json()

assistant_text = resp["message"]["content"]
print("MODEL:", assistant_text)

# ---- detect tool call ----
try:
    tool_call = json.loads(assistant_text)
except json.JSONDecodeError:
    print("FINAL:", assistant_text)
    exit(0)

# ---- call MCP tool ----
result = mcp_call(
    "tools/call",
    {
        "name": tool_call["tool"],
        "arguments": tool_call.get("arguments", {}),
    },
)

tool_output = result["result"]["content"][0]["text"]

# ---- send tool result back to model ----
resp = requests.post(
    OLLAMA_URL,
    json={
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": assistant_text},
            {"role": "tool", "content": tool_output},
        ],
        "stream": False,
    },
).json()

print("FINAL:", resp["message"]["content"])

