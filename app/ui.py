import streamlit as st
import httpx

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="ScholarQA", page_icon="🎓", layout="wide")

# --- CUSTOM STYLING (CSS) ---
st.markdown("""
<style>
/* Target strictly the 3-dot menu using its built-in accessibility label */
[data-testid="stToolbar"] button[aria-label="Main menu"] svg {
    display: none !important;
}
[data-testid="stToolbar"] button[aria-label="Main menu"]::before {
    content: "⚙️ Configure Mode" !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding-right: 15px !important;
}
[data-testid="stToolbar"] button[aria-label="Main menu"] {
    width: auto !important;
}

/* Primary Buttons (Process, Verify, Refresh) -> Professional Blue */
button[kind="primary"] {
    background-color: #007bff !important;
    border-color: #007bff !important;
    color: white !important;
}
button[kind="primary"]:hover {
    background-color: #0056b3 !important;
    border-color: #0056b3 !important;
}

/* Sidebar Secondary Button (Delete) -> Danger Red */
[data-testid="stSidebar"] button[kind="secondary"] {
    background-color: #dc3545 !important;
    border-color: #dc3545 !important;
    color: white !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background-color: #c82333 !important;
    border-color: #c82333 !important;
}
</style>
""", unsafe_allow_html=True)

# --- MAIN HEADER ---
st.title("ScholarQA: Claim Verification")
st.markdown("An AI-powered, 100% local Research Assistant.")
st.markdown("---")

# --- SIDEBAR: SETTINGS & DATA MANAGEMENT ---
with st.sidebar:
    st.header("📁 Project Settings")
    project_id = st.text_input("Project ID", value="thesis_v1", help="Group related documents together under one ID.")
    st.info("Documents uploaded to this ID will be searchable together.")
    
    # --- NEW: View Uploaded Documents ---
    st.divider()
    st.header("📄 Uploaded Documents")
    
    # ADDED type="primary" HERE TO MAKE IT BLUE
    if st.button("🔄 Refresh Document List", type="primary", use_container_width=True):
        if project_id:
            try:
                res = httpx.get(f"{BASE_URL}/projects/{project_id}/documents")
                if res.status_code == 200:
                    docs = res.json().get("documents", [])
                    if docs:
                        for doc in docs:
                            st.markdown(f"- `{doc}`")
                    else:
                        st.caption("No documents found in this project.")
                else:
                    st.caption("Project is empty or does not exist.")
            except httpx.RequestError:
                st.error("Backend offline.")
                
    st.divider()
    
    st.header("⚙️ Data Management")
    st.caption("Warning: This action cannot be undone.")
    if st.button("🗑️ Delete Project Data", type="secondary", use_container_width=True):
        if project_id:
            with st.spinner("Deleting vector database..."):
                try:
                    res = httpx.delete(f"{BASE_URL}/projects/{project_id}")
                    if res.status_code == 200:
                        st.success(f"Project '{project_id}' deleted successfully!")
                    else:
                        st.warning("Project not found or already empty.")
                except httpx.RequestError:
                    st.error("Error connecting to the backend. Is FastAPI running?")
    
    

# --- MAIN CONTENT: TABS ---
tab_upload, tab_verify = st.tabs(["📤 Upload Documents", "🔍 Verify Claims"])

# --- 1. UPLOAD TAB ---
with tab_upload:
    st.header("Ingest New Documents")
    uploaded_file = st.file_uploader("Upload a PDF Document", type="pdf")
    
    if st.button("Process Document", type="primary"):
        if not project_id:
            st.warning("Please provide a Project ID in the sidebar.")
        elif not uploaded_file:
            st.warning("Please upload a PDF file first.")
        else:
            with st.spinner(f"Reading '{uploaded_file.name}' using local AI models..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    res = httpx.post(f"{BASE_URL}/ingest/{project_id}", files=files, timeout=None)
                    if res.status_code == 200:
                        chunks = res.json().get('chunks')
                        st.success(f"✅ Successfully ingested! Created {chunks} semantic chunks.")
                    else:
                        st.error(f"Backend Error: {res.text}")
                except httpx.RequestError:
                    st.error("Error connecting to the backend. Is FastAPI running?")

# --- 2. VERIFY TAB ---
with tab_verify:
    st.header("Test a Hypothesis")
    claim = st.text_area(
        "Enter a claim to verify:", 
        placeholder="e.g., The authors state that their new methodology is significantly faster than previous baseline models."
    )
    
    if st.button("Run Verification Audit", type="primary"):
        if not project_id:
            st.warning("Please provide a Project ID in the sidebar.")
        elif not claim:
            st.warning("Please enter a claim to verify.")
        else:
            with st.spinner("Auditing claim against local database with Llama-3..."):
                try:
                    res = httpx.post(f"{BASE_URL}/verify/{project_id}", json={"claim": claim}, timeout=None)
                    if res.status_code == 200:
                        data = res.json()
                        
                        st.markdown("### 📋 Verification Report")
                        st.info(data.get("report"))
                        
                        # Transparency / Traceability Section
                        with st.expander("🔍 View Raw Extracted Context (Traceability)"):
                            st.markdown("These are the exact paragraphs retrieved from your database to answer the claim:")
                            for idx, chunk in enumerate(data.get("raw_chunks", [])):
                                st.text_area(f"Source Chunk {idx + 1}", value=chunk, height=150, disabled=True)
                    else:
                        # --- NEW: Friendly Error Handling ---
                        error_msg = res.text
                        try:
                            error_msg = res.json().get("detail", res.text)
                        except:
                            pass
                        
                        if "does not exist" in error_msg:
                            st.warning(f"⚠️ Project '{project_id}' is empty! Please go to the 'Upload Documents' tab and process a PDF first.")
                        else:
                            st.error(f"An error occurred: {error_msg}")
                except httpx.RequestError:
                    st.error("Error connecting to the backend. Is FastAPI running?")