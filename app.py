
import requests
import streamlit as st

BASE_URL = st.secrets["N8N_BASE_URL"].rstrip("/")
HEADERS = {"X-API-Key": st.secrets["N8N_API_KEY"]}

st.set_page_config(page_title="AI Knowledge Base", page_icon="📚")
st.title("AI Knowledge Base")

tab_ask, tab_upload = st.tabs(["Ask a question", "Upload a document"])

with tab_upload:
    file = st.file_uploader("PDF, DOCX or TXT", type=["pdf", "docx", "txt"])
    if file and st.button("Upload and index"):
        with st.spinner("Indexing..."):
            try:
                r = requests.post(
                    f"{BASE_URL}/kb-upload",
                    headers=HEADERS,
                    files={"data": (file.name, file.getvalue(), file.type or "application/octet-stream")},
                    timeout=300,
                )
                r.raise_for_status()
                st.success("Document indexed.")
                st.json(r.json())
            except requests.HTTPError:
                st.error(f"Upload failed ({r.status_code}): {r.text[:300]}")
            except Exception as e:
                st.error(f"Upload failed: {e}")

with tab_ask:
    question = st.text_input("Your question")
    if st.button("Ask") and question.strip():
        with st.spinner("Thinking..."):
            try:
                r = requests.post(
                    f"{BASE_URL}/kb-ask",
                    headers=HEADERS,
                    json={"question": question},
                    timeout=120,
                )
                r.raise_for_status()
                st.write(r.json().get("answer", "No answer returned."))
            except requests.HTTPError:
                st.error(f"Request failed ({r.status_code}): {r.text[:300]}")
            except Exception as e:
                st.error(f"Request failed: {e}")
