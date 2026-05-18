# AI Chatbot with RAG and Agentic Capability

A FastAPI-based chatbot that supports three modes of operation:
- **Chat Mode**: Direct conversation with an LLM
- **RAG Mode**: Document-based Q&A using Retrieval-Augmented Generation
- **Agent Mode**: Tool-augmented responses (web search, calculations)

## Table of Contents
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [POST /chat](#post-chat)
  - [POST /upload](#post-upload)
  - [POST /debug/search](#post-debugsearch)
  - [GET /](#get-)
- [Example Requests](#example-requests)

---

## Installation

### Prerequisites
- Python 3.9+
- pip

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Chatbot-with-RAG-and-Agentic-Capability.git
   cd Chatbot-with-RAG-and-Agentic-Capability
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | - | Your Groq API key from [console.groq.com](https://console.groq.com/) |
| `LANGSEARCH_API_KEY` | ✅ Yes* | - | Required for web search in agent mode |
| `GROQ_MODEL` | No | `openai/gpt-oss-120b` | Main chat model |
| `AGENT_MODEL` | No | `llama-3.3-70b-versatile` | Model for agent mode |
| `CHUNK_SIZE` | No | `800` | Document chunk size for RAG |
| `CHUNK_OVERLAP` | No | `200` | Overlap between chunks |
| `TOP_K_RESULTS` | No | `3` | Number of RAG results to retrieve |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | Sentence transformer model |

See `.env.example` for the complete list of configurable options.

---

## Running the Application

Start the server with:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Interactive API docs**: `http://localhost:8000/docs`

---

## API Endpoints

### POST /chat

The main chat endpoint that supports three modes of operation.

#### Request Body

```json
{
  "session_id": "string",
  "message": "string",
  "use_rag": boolean | null,
  "use_agent": boolean | null
}
```

#### Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `session_id` | string | ✅ Yes | - | Unique identifier for the conversation session. Used to maintain chat history. |
| `message` | string | ✅ Yes | - | The user's message/query |
| `use_rag` | boolean \| null | No | `null` | Set to `true` to use RAG mode (document search). Set to `false` or omit for default behavior. |
| `use_agent` | boolean \| null | No | `null` | Set to `true` to use Agent mode (tools like web search). Set to `false` or omit for default behavior. |

#### Mode Selection Logic

| `use_agent` | `use_rag` | Mode | Description |
|-------------|-----------|------|-------------|
| `true` | any | **Agent** | Uses tools (web search, calculator) |
| `false`/`null` | `true` | **RAG** | Searches uploaded documents for context |
| `false`/`null` | `false`/`null` | **Chat** | Direct LLM conversation |

#### Response

Returns a **Server-Sent Events (SSE)** stream with `text/event-stream` content type.

```
data: Hello
data: , how
data:  can I
data:  help you?
data: [DONE]
```

Each `data:` line contains a chunk of the response. The stream ends with `data: [DONE]`.

#### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - streaming response |
| 422 | Validation error - missing required fields |
| 500 | Internal server error |

---

### POST /upload

Upload a document for RAG processing.

#### Request
- **Content-Type**: `multipart/form-data`
- **Body**: File upload (`.pdf` or `.txt` only)

#### Response
```json
{
  "filename": "document.pdf",
  "status": "success",
  "chunks": 15,
  "message": "Document processed successfully. 15 chunks created."
}
```

---

### POST /debug/search

Debug endpoint to test vector search on uploaded documents.

#### Request Body
```json
{
  "query": "your search query",
  "top_k": 5
}
```

#### Response
```json
{
  "query": "your search query",
  "top_k": 5,
  "results": [
    {
      "content": "...",
      "metadata": {...},
      "score": 0.85
    }
  ]
}
```

---

### GET /

Health check endpoint.

#### Response
```json
{
  "status": "healthy",
  "message": "AI Chatbot API is running"
}
```

---

## Example Requests

### 1. Basic Chat (Default Mode)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "Hello, how are you?"
  }'
```

### 2. RAG Mode (Document Q&A)

First, upload a document:
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your_document.pdf"
```

Then query with RAG enabled:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "What is Principal Component Analysis?",
    "use_rag": true
  }'
```

### 3. Agent Mode (Web Search & Tools)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "What is the current price of Bitcoin?",
    "use_agent": true
  }'
```

### 4. Agent Mode (Calculator)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "Calculate 15% of 2500",
    "use_agent": true
  }'
```

### 5. Python Example (with SSE parsing)

```python
import requests

url = "http://localhost:8000/chat"
payload = {
    "session_id": "test-session",
    "message": "Explain machine learning in simple terms",
    "use_rag": False
}

response = requests.post(url, json=payload, stream=True)

for line in response.iter_lines():
    if line:
        decoded = line.decode('utf-8')
        if decoded.startswith('data: '):
            content = decoded[6:]
            if content != '[DONE]':
                print(content, end='', flush=True)
```

### 6. JavaScript/Fetch Example

```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'user-123',
    message: 'What is RAG?',
    use_rag: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ') && line !== 'data: [DONE]') {
      console.log(line.slice(6));
    }
  }
}
```

---

## Project Structure

```
├── app/
│   ├── agent/           # Agent mode with tools
│   ├── chat/            # Chat service and history
│   ├── rag/             # RAG components (embeddings, vector store)
│   ├── utils/           # LLM client, logger
│   ├── config.py        # Settings and environment variables
│   ├── main.py          # FastAPI application
│   └── models.py        # Pydantic models
├── data/                # ChromaDB persistence (auto-created)
├── tests/               # Test files
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Design Decisions & Lessons Learned

This section documents approaches that were tried during development and why the current implementation was chosen.

### 1. Query Router Removed

**What was tried**: An LLM-based query router (`QueryRouter` class) that used `llama-3.1-8b-instant` to classify user queries into three categories: RAG, Agent, or Chat.

**Problem**: The model frequently confused RAG and Agent intents. For example, knowledge-based questions like *"What is Principal Component Analysis?"* were incorrectly routed to Agent mode instead of RAG, even when documents were available.

**Current approach**: Removed the automatic routing logic entirely. Users now explicitly specify the mode via `use_rag` and `use_agent` flags. This makes responses **deterministic and predictable**, eliminating classification errors.

### 2. Model Switch for RAG Generation

**What was tried**: Initially used `llama-3.3-70b-versatile` for generating responses in RAG mode.

**Problem**: The model was not properly utilizing the retrieved document context when answering questions. It would often ignore the augmented documents and respond from its general knowledge instead.

**Current approach**: Switched to `openai/gpt-oss-120b` model which correctly incorporates the retrieved document chunks into its responses, providing accurate document-based answers.

### 3. Evaluator Model Added

**What was tried**: The RAG system initially retrieved documents and passed them directly to the LLM without any relevance check.

**Problem**: The model blindly relied on retrieved documents to answer questions, even when the documents weren't relevant to the query. This resulted in **below-average accuracy** and sometimes incorrect or misleading answers.

**Current approach**: Added an **Evaluator model** (`groq/compound`) that checks whether the retrieved documents are actually relevant for answering the user's question. If documents aren't relevant, the system can fall back to general knowledge or indicate that the information isn't available in the uploaded documents. This makes the RAG system **more accurate and reliable**.

---

## License

MIT License 
