 Local AI News Generator
What Was Built
A fully local, zero-API-key news generation app with a Python ReAct agent loop, DuckDuckGo search, and a Streamlit UI.

Files Created
File	Purpose
requirements.txt	Pins ollama, duckduckgo-search, pydantic, streamlit
models.py	NewsArticle Pydantic schema + JSON schema helper
tools.py	search_web() DuckDuckGo tool + Ollama-compatible TOOLS_SCHEMA
agent.py	NewsAgent class with a raw Python ReAct while loop
app.py	Crisp Streamlit UI — input → spinner → rendered article
Architecture: ReAct Loop
User topic
    │
    ▼
[system prompt + user message]
    │
    ▼
ollama.chat(llama3.1, tools=[search_web])
    │
    ├─── tool_calls? ──► execute search_web(query)
    │                        │
    │        append tool result to history
    │                        │
    │◄───────────────────────┘  (loop back)
    │
    └─── content (JSON)? ──► parse → NewsArticle → return
Max iterations: 10 (safety cap)
Retry logic: if the model returns text that isn't valid JSON, the agent feeds a correction prompt and loops again
JSON extraction: tries 3 strategies — direct parse, fenced code block stripping, and regex brace-hunting
Running the App
Prerequisites
IMPORTANT

You must have Ollama installed on your machine. Before starting Streamlit, open a terminal and run:

ollama run llama3.1
Wait until the model loads (you'll see a >>> prompt). You can then close that terminal — Ollama runs as a background service.

Start the app
Open a new terminal in the project folder and run:

powershell
C:\Users\sambit\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run app.py
Streamlit will open at http://localhost:8501 in your browser.

Validation Results
Check	Result
pip install -r requirements.txt	✅ All packages installed (Python 3.13)
Import check (models, tools, agent)	✅ All imports OK
Troubleshooting
Issue	Fix
Connection refused from Ollama	Make sure ollama run llama3.1 is running
llama3.1 not found	Run ollama pull llama3.1 first
Agent exceeds 10 iterations	The model may be struggling with JSON — try a simpler topic
DuckDuckGo rate limit error	Wait 30 seconds and retry; DDGS has a built-in retry
