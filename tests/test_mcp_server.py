import pytest
import subprocess
import json
import os
import time
import sys
from pathlib import Path

def get_project_root(start: Path = None) -> Path:
    current = start or Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("❌ Could not find project root (no pyproject.toml found)")

PROJECT_ROOT = get_project_root()
SRC_DIR = PROJECT_ROOT / "src"

@pytest.fixture(scope="module")
def mcp_server():
    cmd = [sys.executable, "-m", "mcp_amazon_asin.server"]

    # Whether or not editable-installed, this ensures it works
    env = {**os.environ, "PYTHONPATH": str(SRC_DIR)}

    process = subprocess.Popen(
        cmd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    def send_message(msg):
        process.stdin.write(json.dumps(msg) + "\n")
        process.stdin.flush()

    def read_response(timeout=5):
        start = time.time()
        while True:
            if time.time() - start > timeout:
                break
            line = process.stdout.readline()
            if line.strip():
                return json.loads(line.strip())
        return None

    yield send_message, read_response

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

@pytest.mark.parametrize("asin", ["B0CGXY13QW"])
def test_mcp_server_interaction(mcp_server, asin):
    send, receive = mcp_server

    # Step 1: Initialize
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "pytest-client", "version": "1.0.0"}
        }
    }
    send(init_msg)
    init_resp = receive()
    assert init_resp is not None and init_resp.get("id") == 1

    # Step 2: Initialized notification
    send({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    })
    time.sleep(0.5)

    # Step 3: List tools
    send({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    })
    tools_resp = receive()
    assert tools_resp is not None
    assert tools_resp.get("id") == 2

    # Step 4: Call get_product_info
    send({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_product_info",
            "arguments": {"asin": asin}
        }
    })
    tool_resp = receive()
    assert tool_resp is not None
    assert tool_resp.get("id") == 3
    assert "result" in tool_resp or "error" in tool_resp

