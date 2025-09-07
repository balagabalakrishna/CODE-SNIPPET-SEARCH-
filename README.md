# 🔍 AI-Powered Code Snippet Search Engine

An intelligent and developer-friendly code snippet search engine that leverages **semantic search**, **natural language processing**, and **AI-powered assistance** to improve coding productivity.

---

## 🚀 Features

- 🧠 **AI-Powered Search**: Use natural language to search through 500+ code snippets across multiple domains like Web Development, Machine Learning, and System Design.
- 🤖 **Gemini AI Integration**: 
  - Code explanation
  - Debugging suggestions
  - Code translation (e.g., Python → JavaScript)
  - Auto code builder from natural prompts
- ⚡ **Semantic Search with FAISS**:
  - Embedding-based similarity search
  - Highly relevant and fast snippet retrieval
- 🌐 **Web Interface with Streamlit**:
  - Intuitive, responsive UI
  - Easy to deploy and use locally or on the cloud

---

## 🧑‍💻 Tech Stack

| Category        | Tools / Libraries |
|----------------|-------------------|
| **Language**    | Python |
| **AI/ML**       | Google Gemini API, FAISS (Facebook AI Similarity Search), NLP |
| **Frontend**    | Streamlit, HTML, CSS |
| **Data Format** | JSON (for snippet metadata and embeddings) |

---

## 📅 Project Timeline

**Jan 2025 – Mar 2025**

- Designed and deployed an AI-powered code search engine using Streamlit.
- Indexed 500+ JSON-based code snippets across various domains.
- Integrated Google Gemini AI for intelligent code explanation, debugging help, and natural language interaction.
- Used FAISS for high-speed semantic search with embedding similarity.
- Optimized backend for fast, scalable performance.

---

## 🛠️ Installation & Usage

### 1. Clone the repository

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
# check_models.py
GEMINI_API_KEY = "your_google_gemini_api_key"

streamlit run app.py

🤖 Example Use Cases

“Find me a Python function for JWT authentication”

“Explain this React snippet”

“Convert this Python code to Java”

“Suggest how to optimize this database query”

```bash



git clone https://github.com/your-username/code-snippet-search.git
cd code-snippet-search
