import requests
import streamlit as st

N8N_BASE = st.secrets["https://malik070.app.n8n.cloud/webhook"]   # https://malik070.app.n8n.cloud/webhook
HEADERS = {"X-API-Key": st.secrets["Vp3UL4nvXhG4jscab0tfrnd8HSgrB-reBzrMoyRIJxM"]}

st.set_page_config(page_title="AI Knowledge Base", page_icon="📚")
st.title("AI Knowledge Base")

# ---- Upload documents ----
with st.sidebar:
    st.header("Add documents")
    files = st.file_uploader("PDF, DOCX or TXT", type=["pdf", "docx", "txt"],
                             accept_multiple_files=True)
    if files and st.button("Index documents"):
        for f in files:
            with st.spinner(f"Indexing {f.name}..."):
                r = requests.post(
                    f"{N8N_BASE}/kb-upload",
                    headers=HEADERS,
                    files={"data": (f.name, f.getvalue())},
                    timeout=300,
                )
            if r.ok:
                st.success(f"{f.name} indexed")
            else:
                st.error(f"{f.name} failed: {r.status_code} {r.text[:200]}")

# ---- Chat ----
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

if question := st.chat_input("Ask your knowledge base"):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(f"{N8N_BASE}/kb-ask", headers=HEADERS,
                                  json={"question": question}, timeout=120)
                r.raise_for_status()
                answer = r.json().get("answer", "No answer returned.")
            except Exception as e:
                answer = f"Error: {e}"
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
