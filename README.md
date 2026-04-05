# 🎓 ScholarQA: ML Claim Verification Assistant

ScholarQA is a privacy-first, 100% local Retrieval-Augmented Generation (RAG) application designed for researchers and academics. It allows users to ingest complex PDF documents (like research papers) and rigorously verify claims against the text without sending sensitive, unreleased data to cloud APIs.

## ✨ Key Features
* Utilizes Ollama to run both embedding models and Large Language Models locally, guaranteeing data privacy.
* Converts PDFs into vector embeddings for highly accurate context retrieval.
* The LLM is strictly prompted to return "Not Found" if a claim cannot be explicitly verified by the uploaded text.
* UI that exposes the exact raw text chunks the AI used to verify a claim, ensuring algorithmic transparency.
* Group related papers using unique `Project IDs` and instantly wipe local databases when finished.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Backend:** FastAPI, Uvicorn
* **Database:** ChromaDB (Local Vector Store)
* **AI Models (via Ollama):** * `llama3` (for reasoning and claim verification)
  * `nomic-embed-text` (for hyper-fast local document embeddings)
* **PDF Processing:** Unstructured / PyPDF

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed. You must also install [Ollama](https://ollama.com/) and download the required local models:
```bash
ollama pull llama3
ollama pull nomic-embed-text
```

### 2. Clone the Repository
```bash
git clone https://github.com/UmarNasib/scholarQa.git
cd scholarQa
```

### 3. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the Application
Because this app separates the frontend and backend for better performance, you need to run two terminal windows.

#### Terminal 1: Start the FastAPI Backend
```bash
source venv/bin/activate
python3 -m app.main
```

#### Terminal 2: Start the Streamlit UI
```bash
source venv/bin/activate
streamlit run app/ui.py
```


## 💻 Usage Instructions
* Open the UI in your browser (usually http://localhost:8501).
* Enter a Project ID in the sidebar (e.g., thesis_v1).
* Go to the Upload Documents tab, upload a PDF, and click Process Document.
* Switch to the Verify Claims tab and enter a hypothesis or claim.
* Review the AI's verdict and click "View Raw Extracted Context" to see the exact paragraphs used for the audit.