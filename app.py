import requests
import streamlit as st

st.set_page_config(page_title="AI Knowledge Base", page_icon="📚", layout="centered")

BASE_URL = st.secrets["N8N_BASE_URL"].rstrip("/")
HEADERS = {"X-API-Key": st.secrets["N8N_API_KEY"]}

# ---- Custom CSS to match the Upload Files card UI ----
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background-color: #f3f3f5;
    }

    /* Main Card Container */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 18px !important;
        border: 1px solid #ececef !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.06);
        padding: 1.5rem 1.75rem !important;
    }

    /* Card Header */
    .upload-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #f0f0f3;
    }
    .upload-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
    }
    .close-badge {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        background: #f5f5f7;
        color: #6b7280;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }

    /* Dashed Dropzone Visual */
    .dropzone-visual {
        border: 1.5px dashed #d1d5db;
        border-radius: 14px;
        padding: 2rem 1rem 1.5rem 1rem;
        text-align: center;
        background-color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .dropzone-main-text {
        font-size: 1.05rem;
        font-weight: 600;
        color: #111827;
        margin-top: 0.75rem;
        margin-bottom: 0.25rem;
    }
    .dropzone-sub-link {
        font-size: 0.92rem;
        font-weight: 500;
        color: #e11d48;
        text-decoration: underline;
    }

    /* Native Streamlit file uploader styling */
    [data-testid="stFileUploader"] {
        margin-top: -0.5rem;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: #fafafa;
        border: 1px dashed #e5e7eb;
        border-radius: 10px;
        padding: 0.6rem 1rem;
    }
    [data-testid="stFileUploader"] ul {
        display: none;
    }

    /* Meta row under dropzone */
    .meta-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #8c919b;
        margin: 0.35rem 0 1.25rem 0;
    }
    .meta-underline {
        text-decoration: underline;
    }

    /* Uploaded File Row Card */
    .file-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.65rem;
        background: #ffffff;
    }
    .file-left {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }
    .file-badge {
        width: 34px;
        height: 40px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: 700;
        font-size: 0.68rem;
        letter-spacing: 0.03em;
    }
    .badge-pdf { background: linear-gradient(135deg, #ef4444, #dc2626); }
    .badge-doc { background: linear-gradient(135deg, #3b82f6, #2563eb); }
    .badge-txt { background: linear-gradient(135deg, #10b981, #059669); }

    .file-name {
        font-size: 0.92rem;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
    }
    .file-sub {
        font-size: 0.78rem;
        color: #9ca3af;
        margin: 0.15rem 0 0 0;
    }
    .status-uploaded {
        color: #e11d48;
        font-weight: 500;
    }
    .status-ready {
        color: #6b7280;
        font-weight: 500;
    }

    /* Footer Help text */
    .help-text {
        font-size: 0.85rem;
        color: #6b7280;
        padding-top: 0.45rem;
    }

    /* Gradient Primary Button (Save / Ask) */
    button[kind="primary"] {
        background: linear-gradient(90deg, #c026d3 0%, #f97316 100%) !important;
        border: none !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: opacity 0.2s ease;
    }
    button[kind="primary"]:hover {
        opacity: 0.92;
    }

    /* Cancel Button (Secondary) */
    button[kind="secondary"] {
        background: #ffffff !important;
        border: 1px solid #d1d5db !important;
        color: #374151 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Session State ----
if "uploaded_info" not in st.session_state:
    st.session_state.uploaded_info = {}  # {filename: response_json}
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def format_size(num_bytes: int) -> str:
    mb = num_bytes / (1024 * 1024)
    return f"{mb:.1f} MB" if mb >= 0.1 else f"{num_bytes / 1024:.0f} KB"


def get_badge_info(filename: str):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "file"
    if ext == "pdf":
        return "PDF", "badge-pdf"
    if ext in ("doc", "docx"):
        return "DOC", "badge-doc"
    return "TXT", "badge-txt"


st.title("AI Knowledge Base")

tab_ask, tab_upload = st.tabs(["Ask a question", "Upload a document"])

# ---- TAB 1: Ask a question ----
with tab_ask:
    with st.container(border=True):
        st.markdown(
            """
            <div class="upload-header">
                <p class="upload-title">Ask a Question</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        question = st.text_input(
            "Your question",
            placeholder="Type your question about the uploaded documents...",
            label_visibility="collapsed",
        )
        col_spacer, col_ask = st.columns([5, 1.5])
        with col_ask:
            ask_clicked = st.button("Ask", type="primary", use_container_width=True)

        if ask_clicked and question.strip():
            with st.spinner("Thinking..."):
                r = None
                try:
                    r = requests.post(
                        f"{BASE_URL}/kb-ask",
                        headers=HEADERS,
                        json={"question": question},
                        timeout=120,
                    )
                    r.raise_for_status()
                    st.markdown("---")
                    st.write(r.json().get("answer", "No answer returned."))
                except requests.HTTPError:
                    status = r.status_code if r is not None else "Unknown"
                    body = r.text[:300] if r is not None else ""
                    st.error(f"Request failed ({status}): {body}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

# ---- TAB 2: Upload a document (Card UI from image) ----
with tab_upload:
    with st.container(border=True):
        # Card Header
        st.markdown(
            """
            <div class="upload-header">
                <p class="upload-title">Upload Files</p>
                <div class="close-badge">✕</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Dashed Dropzone with 3-Document Illustration
        st.markdown(
            """
            <div class="dropzone-visual">
                <svg width="110" height="82" viewBox="0 0 110 82" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="pinkGrad" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#F472B6"/>
                            <stop offset="100%" stop-color="#C026D3"/>
                        </linearGradient>
                        <linearGradient id="orangeGrad" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#FB923C"/>
                            <stop offset="100%" stop-color="#EA580C"/>
                        </linearGradient>
                        <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#67E8F9"/>
                            <stop offset="100%" stop-color="#3B82F6"/>
                        </linearGradient>
                    </defs>
                    <g transform="rotate(-12 32 45)">
                        <rect x="14" y="14" width="36" height="48" rx="6" fill="url(#pinkGrad)"/>
                        <rect x="20" y="25" width="16" height="3" rx="1.5" fill="white" fill-opacity="0.8"/>
                        <rect x="20" y="32" width="12" height="3" rx="1.5" fill="white" fill-opacity="0.8"/>
                        <rect x="20" y="39" width="14" height="3" rx="1.5" fill="white" fill-opacity="0.8"/>
                    </g>
                    <g transform="rotate(12 78 45)">
                        <rect x="60" y="14" width="36" height="48" rx="6" fill="url(#orangeGrad)"/>
                        <rect x="68" y="25" width="16" height="3" rx="1.5" fill="white" fill-opacity="0.8"/>
                        <rect x="68" y="32" width="12" height="3" rx="1.5" fill="white" fill-opacity="0.8"/>
                        <rect x="68" y="39" width="14" height="3" rx="1.5" fill="white" fill-opacity="0.8"/>
                    </g>
                    <rect x="35" y="8" width="40" height="54" rx="7" fill="url(#blueGrad)"/>
                    <circle cx="55" cy="35" r="9" stroke="white" stroke-width="1.8"/>
                    <path d="M55 31V39M51 35H59" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
                </svg>
                <div class="dropzone-main-text">Drag and drop files here</div>
                <div class="dropzone-sub-link">or choose file below</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        file = st.file_uploader(
            "PDF, DOCX or TXT",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
            key=f"uploader_{st.session_state.uploader_key}",
        )

        # Accepted formats & limit row
        st.markdown(
            """
            <div class="meta-row">
                <span>Accepted formats: pdf, docx, txt</span>
                <span class="meta-underline">Max file size: 200MB</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Custom File Card Row
        if file:
            badge_label, badge_class = get_badge_info(file.name)
            is_uploaded = file.name in st.session_state.uploaded_info
            status_html = (
                '<span class="status-uploaded">Uploaded</span>'
                if is_uploaded
                else '<span class="status-ready">Ready to save</span>'
            )
            st.markdown(
                f"""
                <div class="file-card">
                    <div class="file-left">
                        <div class="file-badge {badge_class}">{badge_label}</div>
                        <div>
                            <p class="file-name">{file.name}</p>
                            <p class="file-sub">{format_size(file.size)} &nbsp;|&nbsp; {status_html}</p>
                        </div>
                    </div>
                    <span style="color:#9ca3af; font-size:13px;">{"✓" if is_uploaded else "✕"}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Bottom Action Row: Help on left, Save & Cancel on right
        col_help, col_save, col_cancel = st.columns([5, 1.5, 1.5])

        with col_help:
            st.markdown('<div class="help-text">ⓘ Help</div>', unsafe_allow_html=True)

        with col_save:
            save_clicked = st.button("Save", type="primary", use_container_width=True)

        with col_cancel:
            cancel_clicked = st.button("Cancel", type="secondary", use_container_width=True)

        # Handle Save (Upload and index)
        if save_clicked:
            if not file:
                st.warning("Please choose a file first.")
            else:
                with st.spinner("Indexing..."):
                    r = None
                    try:
                        r = requests.post(
                            f"{BASE_URL}/kb-upload",
                            headers=HEADERS,
                            files={
                                "data": (
                                    file.name,
                                    file.getvalue(),
                                    file.type or "application/octet-stream",
                                )
                            },
                            timeout=300,
                        )
                        r.raise_for_status()
                        st.session_state.uploaded_info[file.name] = r.json()
                        st.rerun()
                    except requests.HTTPError:
                        status = r.status_code if r is not None else "Unknown"
                        body = r.text[:300] if r is not None else ""
                        st.error(f"Upload failed ({status}): {body}")
                    except Exception as e:
                        st.error(f"Upload failed: {e}")

        # Show confirmation + JSON response after indexing
        if file and file.name in st.session_state.uploaded_info:
            st.success("Document indexed.")
            st.json(st.session_state.uploaded_info[file.name])

        # Handle Cancel (Reset file selection)
        if cancel_clicked:
            st.session_state.uploaded_info.clear()
            st.session_state.uploader_key += 1
            st.rerun()
