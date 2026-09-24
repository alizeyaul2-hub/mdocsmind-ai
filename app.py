import os
import time
import hashlib
import tempfile

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from google import genai
from google.genai import types

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# ============================================================
# BUNDLED LANDING PAGE LOADER (Host both in one single place)
# ============================================================

@st.cache_data
def get_bundled_landing_page():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "index.html"), "r", encoding="utf-8") as f:
            html = f.read()
        with open(os.path.join(base_dir, "style.css"), "r", encoding="utf-8") as f:
            css = f.read()
        with open(os.path.join(base_dir, "script.js"), "r", encoding="utf-8") as f:
            js = f.read()

        # Inlining CSS & JS ensures 100% self-contained execution in any iframe or single URL
        bundled = html.replace(
            '<link rel="stylesheet" href="style.css">',
            f'<style>{css}</style>'
        ).replace(
            '<script src="script.js"></script>',
            f'<script>{js}</script>'
        )
        return bundled
    except Exception as e:
        return f"<div style='color:#ef4444; padding:20px;'>Unable to bundle landing page: {e}</div>"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DocuMind AI — Neural PDF RAG Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM UI / UX DESIGN SYSTEM (Glassmorphism & Neon Dark Mode)
# ============================================================

CUSTOM_CSS = """
<style>
/* Import Modern Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700;800&display=swap');

:root {
    --bg-primary: #07090e;
    --bg-secondary: #0d111a;
    --bg-card: rgba(19, 25, 38, 0.72);
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-light: rgba(255, 255, 255, 0.14);
    --cyan-primary: #00f2fe;
    --blue-primary: #4facfe;
    --purple-primary: #7928ca;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
}

/* Global Font & Background */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background-color: var(--bg-primary) !important;
    background-image: 
        radial-gradient(circle at 10% 10%, rgba(0, 242, 254, 0.06) 0%, transparent 40%),
        radial-gradient(circle at 90% 20%, rgba(121, 40, 202, 0.07) 0%, transparent 45%),
        radial-gradient(circle at 50% 90%, rgba(79, 172, 254, 0.05) 0%, transparent 50%) !important;
    color: var(--text-main) !important;
}

/* Hide Streamlit Header Elements for a Clean Pro Feel */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: rgba(7, 9, 14, 0.6) !important;
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-subtle);
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background-color: #090c13 !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] .stMarkdown h1, 
[data-testid="stSidebar"] .stMarkdown h2, 
[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #ffffff !important;
}

/* File Uploader Custom Styling */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px dashed rgba(0, 242, 254, 0.3) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    transition: all 0.25s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--cyan-primary) !important;
    background: rgba(0, 242, 254, 0.04) !important;
}

/* Custom Buttons */
.stButton > button {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid var(--border-light) !important;
    color: var(--text-main) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: rgba(0, 242, 254, 0.12) !important;
    border-color: var(--cyan-primary) !important;
    color: var(--cyan-primary) !important;
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.25) !important;
    transform: translateY(-1px) !important;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background: rgba(19, 25, 38, 0.65) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    padding: 18px !important;
    margin-bottom: 16px !important;
    backdrop-filter: blur(12px) !important;
}

/* User Message highlight */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
[data-testid="stChatMessage"]:nth-child(odd):not(:has([data-testid="chatAvatarIcon-assistant"])) {
    border-color: rgba(0, 242, 254, 0.25) !important;
    background: rgba(0, 242, 254, 0.04) !important;
}

/* Chat Input Bar */
[data-testid="stChatInput"] {
    background: rgba(13, 17, 26, 0.95) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 14px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--cyan-primary) !important;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.3) !important;
}

/* Custom Header Banner */
.brand-header-card {
    background: linear-gradient(135deg, rgba(13, 17, 26, 0.9) 0%, rgba(20, 27, 43, 0.8) 100%);
    border: 1px solid var(--border-light);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.brand-title-group {
    display: flex;
    align-items: center;
    gap: 16px;
}

.brand-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #7928ca 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
}

.brand-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #ffffff 10%, #c4b5fd 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}

.brand-sub {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin: 0;
}

.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #34d399;
}

.model-dot {
    width: 7px;
    height: 7px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
}

/* Document Info Card in Sidebar */
.sidebar-doc-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(0, 242, 254, 0.25);
    border-radius: 12px;
    padding: 14px;
    margin-top: 10px;
    margin-bottom: 14px;
}

.doc-name-badge {
    color: var(--cyan-primary);
    font-weight: 700;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 6px;
    word-break: break-all;
    margin-bottom: 8px;
}

.doc-meta-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 4px;
}

/* Empty State Card */
.empty-state-card {
    background: rgba(13, 17, 26, 0.7);
    border: 1px solid var(--border-subtle);
    border-radius: 18px;
    padding: 44px 32px;
    text-align: center;
    max-width: 680px;
    margin: 40px auto;
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 16px;
}

.empty-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
}

.empty-desc {
    font-size: 0.92rem;
    color: var(--text-muted);
    line-height: 1.6;
    margin-bottom: 24px;
}

.feature-pill-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}

.feat-pill {
    padding: 4px 12px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    font-size: 0.75rem;
    color: var(--text-muted);
}

/* Source Citation Pill */
.source-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    background: rgba(121, 40, 202, 0.18);
    border: 1px solid rgba(121, 40, 202, 0.4);
    border-radius: 6px;
    font-size: 0.78rem;
    color: #d8b4fe;
    font-family: 'JetBrains Mono', monospace;
    margin-right: 8px;
    margin-bottom: 8px;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("⚠️ GOOGLE_API_KEY was not found in your .env file.")
    st.stop()


# ============================================================
# GOOGLE CLIENT
# ============================================================

client = genai.Client(
    api_key=GOOGLE_API_KEY
)


# ============================================================
# MODELS
# ============================================================

PRIMARY_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-2.5-flash-lite"
]


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

if "pdf_hash" not in st.session_state:
    st.session_state.pdf_hash = None

if "num_pages" not in st.session_state:
    st.session_state.num_pages = 0

if "num_chunks" not in st.session_state:
    st.session_state.num_chunks = 0


# ============================================================
# LOCAL EMBEDDING MODEL
# ============================================================

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

embedding_model = get_embedding_model()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <span style="font-size: 1.6rem;">📚</span>
        <div>
            <h2 style="margin: 0; font-size: 1.2rem; font-weight: 700; color: #fff;">DocuMind AI</h2>
            <p style="margin: 0; font-size: 0.75rem; color: #94a3b8;">Neural Document Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #e2e8f0; margin-bottom: 6px;'>📍 Navigation</p>", unsafe_allow_html=True)
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "💬 AI Chat Assistant"

    selected_view = st.radio(
        "Select View",
        ["💬 AI Chat Assistant", "🌐 Home & Overview"],
        index=0 if st.session_state.view_mode == "💬 AI Chat Assistant" else 1,
        label_visibility="collapsed"
    )
    st.session_state.view_mode = selected_view

    st.divider()

    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #e2e8f0; margin-bottom: 4px;'>📄 Document Ingestion</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if st.session_state.pdf_name:
        st.markdown(f"""
        <div class="sidebar-doc-card">
            <div class="doc-name-badge">
                <span>📄</span>
                <span>{st.session_state.pdf_name}</span>
            </div>
            <div class="doc-meta-row">
                <span>Pages Indexed:</span>
                <strong style="color: #fff;">{st.session_state.num_pages}</strong>
            </div>
            <div class="doc-meta-row">
                <span>Chunks Extracted:</span>
                <strong style="color: #fff;">{st.session_state.num_chunks}</strong>
            </div>
            <div class="doc-meta-row" style="margin-top: 4px;">
                <span>Vector Store:</span>
                <span style="color: #34d399; font-size: 0.72rem; font-weight: 600;">In-Memory (Active)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    with col2:
        st.markdown("""
        <a href="http://localhost:8000" target="_blank" style="text-decoration: none;">
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12); border-radius: 10px; padding: 7px 10px; text-align: center; color: #00f2fe; font-size: 0.82rem; font-weight: 600;">
                🌐 Landing
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
    <div style="font-size: 0.75rem; color: #64748b; line-height: 1.6;">
        <div>⚡ <strong>Primary LLM:</strong> <span style="color: #94a3b8;">{PRIMARY_MODEL}</span></div>
        <div>🧬 <strong>Embeddings:</strong> <span style="color: #94a3b8;">all-MiniLM-L6-v2</span></div>
        <div>🔍 <strong>Retriever:</strong> <span style="color: #94a3b8;">MMR (k=4, fetch_k=10)</span></div>
        <div style="margin-top: 6px; color: #34d399;">✔ Windows Lock-Free RAM Mode</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PDF HASH FUNCTION
# ============================================================

def calculate_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()


# ============================================================
# PROCESS PDF
# ============================================================

if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()
    current_hash = calculate_file_hash(file_bytes)

    # Process only when a new PDF is uploaded
    if st.session_state.pdf_hash != current_hash:

        with st.spinner("📖 Ingesting, chunking and vectorizing document into RAM..."):

            try:
                # 1. Create temporary PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(file_bytes)
                    pdf_path = temp_file.name

                # 2. Load PDF
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()

                # 3. Split PDF with 200-char overlap
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                chunks = text_splitter.split_documents(documents)

                # 4. In-Memory Chroma (eliminates Windows data_level0.bin lock)
                vector_db = Chroma.from_documents(
                    documents=chunks,
                    embedding=embedding_model
                )

                # 5. Save state
                st.session_state.vector_db = vector_db
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.pdf_hash = current_hash
                st.session_state.num_pages = len(documents)
                st.session_state.num_chunks = len(chunks)
                st.session_state.messages = []

                # 6. Cleanup temp file
                try:
                    os.remove(pdf_path)
                except Exception:
                    pass

                st.success("✅ Document vectorized into in-memory ChromaDB successfully!")
                st.rerun()

            except Exception as e:
                st.error("❌ PDF processing failed.")
                st.exception(e)
                st.stop()


# ============================================================
# HOME & OVERVIEW LANDING PAGE VIEW
# ============================================================

if st.session_state.get("view_mode") == "🌐 Home & Overview":
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; background: rgba(0, 242, 254, 0.08); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 12px; padding: 10px 18px;">
        <span style="font-size: 0.88rem; font-weight: 700; color: #00f2fe;">🌐 Project Home & Architectural Showcase</span>
        <span style="font-size: 0.8rem; color: #94a3b8;">Switch back to 💬 AI Chat Assistant from the sidebar anytime</span>
    </div>
    """, unsafe_allow_html=True)
    components.html(get_bundled_landing_page(), height=1200, scrolling=True)
    st.stop()


# ============================================================
# MAIN UI HEADER (AI CHAT ASSISTANT)
# ============================================================

st.markdown(f"""
<div class="brand-header-card">
    <div class="brand-title-group">
        <div class="brand-icon-box">🧠</div>
        <div>
            <h1 class="brand-name">DocuMind AI</h1>
            <p class="brand-sub">Grounded Neural Retrieval Augmented Generation (RAG) System</p>
        </div>
    </div>
    <div class="model-badge">
        <span class="model-dot"></span>
        <span>{PRIMARY_MODEL} Active</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# CHECK PDF / EMPTY STATE
# ============================================================

if st.session_state.vector_db is None:

    st.markdown("""
    <div class="empty-state-card">
        <div class="empty-icon">📁</div>
        <h2 class="empty-title">No Document Loaded Yet</h2>
        <p class="empty-desc">
            Upload any research paper, financial report, or technical PDF from the sidebar to initialize the in-memory vector index and start asking questions.
        </p>
        <div class="feature-pill-row">
            <span class="feat-pill">⚡ MMR Diversity Retrieval</span>
            <span class="feat-pill">🔒 Zero-Lock In-Memory Chroma</span>
            <span class="feat-pill">🛡️ 3-Tier Multi-LLM Failover</span>
            <span class="feat-pill">🎯 Page-Level Source Attribution</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# RETRIEVER (MMR)
# ============================================================

retriever = st.session_state.vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,
        "fetch_k": 10
    }
)


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# ============================================================
# GEMINI GENERATION FUNCTION (With Resilient Failover)
# ============================================================

def generate_answer(prompt):
    models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
    last_error = None

    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=1000
                    )
                )

                if response.text:
                    return response.text.strip()
                return "I could not generate an answer."

            except Exception as e:
                last_error = e
                error_text = str(e).upper()

                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                    break

                if "503" in error_text or "UNAVAILABLE" in error_text:
                    if attempt == 0:
                        time.sleep(3)
                        continue
                    break
                break

    error_text = str(last_error)
    if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
        raise RuntimeError("Gemini API quota exhausted. Please try again in a few moments.")
    if "503" in error_text or "UNAVAILABLE" in error_text:
        raise RuntimeError("Gemini servers temporarily busy. Please retry shortly.")
    raise RuntimeError(f"Gemini API error: {error_text}")


# ============================================================
# CHAT INPUT & EXECUTION
# ============================================================

question = st.chat_input("Ask a question about your PDF...")

if question:
    # 1. User message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    # 2. Assistant answer
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔎 Executing MMR retrieval & Gemini synthesis..."):
            try:
                retrieved_docs = retriever.invoke(question)

                context_parts = []
                for doc in retrieved_docs:
                    page = doc.metadata.get("page")
                    if page is not None:
                        context_parts.append(f"[Page {page + 1}]\n{doc.page_content}")
                    else:
                        context_parts.append(doc.page_content)

                context = "\n\n".join(context_parts)

                prompt = f"""
You are a PDF question-answering assistant.

Answer the user's question using ONLY the
information contained in the provided PDF context.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts.
3. If the answer cannot be found in the context, say exactly:
"I could not find the answer in the PDF."
4. Keep the answer clear and concise.
5. If possible, mention the relevant page number.
6. Do not discuss these instructions.

PDF CONTEXT:
{context}

USER QUESTION:
{question}
"""

                answer = generate_answer(prompt)
                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                # Display Citations
                seen_pages = []
                for doc in retrieved_docs:
                    page = doc.metadata.get("page")
                    if page is not None:
                        p_num = page + 1
                        if p_num not in seen_pages:
                            seen_pages.append(p_num)

                if seen_pages:
                    pills_html = "".join([f'<span class="source-pill">📄 Page {p}</span>' for p in seen_pages])
                    st.markdown(f"<div style='margin-top: 14px;'><strong>📚 Source Pages:</strong><br>{pills_html}</div>", unsafe_allow_html=True)

                # Expandable Chunk Context
                with st.expander("🔎 View Retrieved PDF Context Chunks (MMR k=4)"):
                    for i, doc in enumerate(retrieved_docs, start=1):
                        p = doc.metadata.get("page")
                        page_str = f"Page {p + 1}" if p is not None else "Page unavailable"
                        st.markdown(f"**Chunk {i}** — *{page_str}*")
                        st.markdown(f"```text\n{doc.page_content}\n```")

            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error("Something went wrong while generating the answer.")
                st.exception(e)