# Hello World MCP Server & Client — Step-by-Step Guide

## What you'll build

This project shows two ways to run an MCP server and client:

1. **STDIO (recommended first)** — One command runs the client; it starts the server automatically.
2. **Standalone HTTP** — You start the server in one terminal, then run the client in another.

---

## File structure

```
hello_world_mcp/
├── server.py              ← MCP server (STDIO; exposes say_hello, get_time)
├── client.py              ← MCP client (STDIO; starts server as subprocess)
├── server_standalone.py    ← MCP server over HTTP (port 8000)
├── clientstandalone.py     ← MCP client over HTTP (connects to running server)
├── requirements.txt       ← Python dependencies
└── README.md
```

---

# Example 1 — STDIO (run this first)

This is the **simplest way** to try MCP: run the client once; it launches the server for you.

```
┌─────────────┐   MCP over STDIO   ┌─────────────┐
│  client.py  │ ◄────────────────► │  server.py  │
│  (MCP Client)│   (subprocess)     │  (MCP Server)│
└─────────────┘                    └─────────────┘
```

### Step 1 — Prerequisites

Use **Python 3.10 or newer**:

```bash
python --version
# Should print: Python 3.10.x  or higher
```

> **Windows:** Use `python` instead of `python3` in the commands below.

### Step 2 — Virtual environment (recommended)

```bash
python -m venv venv

# Activate
# macOS / Linux:
source venv/bin/activate

# Windows (Command Prompt):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1
```

You should see `(venv)` in your prompt.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

Check:

```bash
pip show mcp
# Version should be >= 1.0.0
```

### Step 4 — Run the client (server starts automatically)

With **STDIO**, the client starts the server as a subprocess. You do **not** start the server yourself.

```bash
cd hello_world_mcp
python client.py
```

**Expected output:**

```
✅ Connected to MCP server!

🔧 Available tools:
  • say_hello: Returns a friendly Hello World greeting. Optionally personalise it with a name.
  • get_time: Returns the current date and time in ISO format.

📞 Calling say_hello() with no arguments...
   Server replied: Hello, World! 👋 Welcome to your first MCP server!

📞 Calling say_hello(name='Prakash')...
   Server replied: Hello, Prakash! 👋 Welcome to your first MCP server!

📞 Calling get_time()...
   Server replied: Current time: 2026-02-22T...

🎉 Done! Your first MCP server and client are working.
```

### Step 5 — Test the server alone (optional)

In a **second** terminal (venv activated), run:

```bash
python server.py
```

The server waits for JSON-RPC on stdin. Press `Ctrl+C` to stop. It is meant to be driven by a client.

### Step 6 — Add your own tools

In **server.py**:

1. In `list_tools()`, add a new `Tool(...)` with `name`, `description`, and `inputSchema`.
2. In `call_tool()`, add an `elif name == "your_tool":` branch and return `[TextContent(...)]`.
3. Run `python client.py` and call `session.call_tool(name="your_tool", arguments={...})`.

---

# Example 2 — Standalone HTTP (server and client separate)

Here the server runs as an **HTTP server** on port 8000. You start the server first, then run the client in another terminal. The client does **not** start the server.

```
Terminal 1                    Terminal 2
┌─────────────────────┐      ┌─────────────────────┐
│ server_standalone.py │      │ clientstandalone.py  │
│ (HTTP on :8000)      │◄────►│ (connects to :8000)  │
└─────────────────────┘      └─────────────────────┘
```

### Prerequisites

Same as Example 1: Python 3.10+, virtual environment, and `pip install -r requirements.txt`.

### Step 1 — Start the server (first terminal)

Open a terminal, activate the venv, and run:

```bash
cd hello_world_mcp
source venv/bin/activate          # Windows: venv\Scripts\activate
python server_standalone.py
```

Leave this running. You should see something like:

```
INFO:     Started server process ...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2 — Run the client (second terminal)

Open a **new** terminal, activate the same venv, and run:

```bash
cd hello_world_mcp
source venv/bin/activate          # Windows: venv\Scripts\activate
python clientstandalone.py
```

### Step 3 — Expected client output

The client connects to `http://127.0.0.1:8000/mcp` and calls the same tools:

```
✅ Connected to MCP server!

🔧 Available tools:
  • say_hello: ...
  • get_time: ...

📞 Calling say_hello() with no arguments...
   Server replied: Hello, World! 👋 ...

📞 Calling say_hello(name='Prakash')...
   Server replied: Hello, Prakash! 👋 ...

📞 Calling get_time()...
   Server replied: Current time: ...

🎉 Done! Standalone client and server are working.
```

### Step 4 — Stop the server

In the first terminal, press `Ctrl+C` to stop `server_standalone.py`.

### Troubleshooting (standalone)

| Problem | Fix |
|--------|-----|
| `Connection refused` / client cannot connect | Start `server_standalone.py` first and leave it running. |
| Port 8000 in use | Change the port in `server_standalone.py` and in `clientstandalone.py` (`MCP_SERVER_URL`). |
| `ModuleNotFoundError: mcp` | Activate the venv and run `pip install -r requirements.txt`. |

---

# Troubleshooting (general)

| Problem | Fix |
|--------|-----|
| `ModuleNotFoundError: mcp` | Run `pip install -r requirements.txt` with your venv active. |
| `python: command not found` | Use `python3` instead of `python`. |
| `FileNotFoundError: server.py` | Run commands from inside the `hello_world_mcp/` directory. |
| Handshake timeout | Ensure `server.py` is not crashing; run from the project folder. |

---

# How MCP works (quick mental model)

```
Client                          Server
  │                               │
  │──── initialize ──────────────►│   "Hi, I'm a client"
  │◄─── initialize result ────────│   "Hi, here are my capabilities"
  │──── initialized ─────────────►│   "Got it, let's go"
  │                               │
  │──── tools/list ──────────────►│   "What tools do you have?"
  │◄─── tools/list result ────────│   [{ name: "say_hello", … }]
  │                               │
  │──── tools/call (say_hello) ──►│   "Call say_hello for me"
  │◄─── tools/call result ────────│   "Hello, World! 👋 …"
```

Messages are **JSON-RPC 2.0** over the transport (STDIO or HTTP). The `mcp` SDK handles serialization.

---

# Git instructions

Use these steps to put this project on GitHub (or another remote) and keep it in sync.

## 1. Initialize the repository

```bash
cd hello_world_mcp
git init
```

## 2. Add the remote

```bash
git remote add origin git@github.com:prakash3210/hello_world_mcp.git
```

Use your own repo URL if different.

## 3. Stage and commit

```bash
git add .
git status
git branch -M main
git commit -m "Initial commit: Hello World MCP server and client"
```

## 4. Push to GitHub

If the remote already has commits (e.g. README or license), rebase then push:

```bash
git pull origin main --rebase
# Resolve any conflicts (e.g. in .gitignore), then:
git add .
GIT_EDITOR="true" git rebase --continue
git push -u origin main
```

If the remote is empty:

```bash
git push -u origin main
```

## 5. Later: commit and push changes

```bash
git add .
git commit -m "Your message"
git push
```

## Summary of commands (in order)

| Step | Command |
|------|--------|
| Create repo | `git init` |
| Add remote | `git remote add origin git@github.com:prakash3210/hello_world_mcp.git` |
| Stage files | `git add .` |
| Check status | `git status` |
| Use main branch | `git branch -M main` |
| First commit | `git commit -m "Initial commit: Hello World MCP server and client"` |
| Sync with remote (if needed) | `git pull origin main --rebase` |
| After fixing conflicts | `git add .` then `GIT_EDITOR="true" git rebase --continue` |
| Push | `git push -u origin main` |
