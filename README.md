📰 Local AI News Generator

A fully local, zero-API-key news generation app powered by a Python-based ReAct agent loop, DuckDuckGo search, and a Streamlit UI.

🚀 What Was Built

This project implements an autonomous news-writing agent that:

Runs completely locally (no API keys required)
Uses Ollama (llama3.1) for LLM inference
Integrates DuckDuckGo search for real-time information
Generates structured news articles using a Pydantic schema
Provides a clean Streamlit interface
📁 Project Structure
File	Purpose
requirements.txt	Dependency list (ollama, duckduckgo-search, pydantic, streamlit)
models.py	NewsArticle Pydantic schema + JSON schema helper
tools.py	search_web() DuckDuckGo tool + Ollama-compatible TOOLS_SCHEMA
agent.py	NewsAgent class with a raw Python ReAct loop
app.py	Streamlit UI (input → processing → rendered article)
🧠 Architecture: ReAct Loop
User topic
    │
    ▼
[system prompt + user message]
    │
    ▼
ollama.chat(llama3.1, tools=[search_web])
    │
    ├── tool_calls? ──► execute search_web(query)
    │                     │
    │     append tool result to history
    │                     │
    │◄────────────────────┘ (loop back)
    │
    └── content (JSON)? ──► parse → NewsArticle → return
⚙️ Key Behaviors
Max iterations: 10 (safety cap)
Retry logic:
If invalid JSON is returned, the agent:
Sends a correction prompt
Re-enters the loop
JSON extraction strategies:
Direct parsing
Code block stripping
Regex-based brace extraction
▶️ Running the App
🔧 Prerequisites

⚠️ Important: You must have Ollama installed.

Run this in a terminal before starting the app:

ollama run llama3.1

Wait until the model loads (>>> prompt appears), then you can close the terminal. Ollama will continue running in the background.

🖥️ Start the App

Open a new terminal in the project directory and run:

C:\Users\sambit\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run app.py

Then open:

http://localhost:8501
✅ Validation Results
Check	Result
pip install -r requirements.txt	✅ All packages installed (Python 3.13)
Import checks (models, tools, agent)	✅ All imports OK
🛠️ Troubleshooting
Issue	Fix
Connection refused from Ollama	Ensure ollama run llama3.1 is running
llama3.1 not found	Run ollama pull llama3.1
Agent exceeds 10 iterations	Try a simpler topic (model may struggle with JSON)
DuckDuckGo rate limit error	Wait ~30 seconds and retry
