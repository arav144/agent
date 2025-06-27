import streamlit as st
import PyPDF2
import docx
import pandas as pd
import openai
import os
from io import StringIO

def extract_text_from_txt(file):
    return file.read().decode('utf-8')

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_excel(file):
    dfs = pd.read_excel(file, sheet_name=None)
    text = ""
    for sheet, df in dfs.items():
        text += f"Sheet: {sheet}\n"
        text += df.to_string(index=False)
        text += "\n"
    return text

def get_file_text(uploaded_file):
    if uploaded_file.type == "text/plain":
        return extract_text_from_txt(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        return extract_text_from_docx(uploaded_file)
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        return extract_text_from_excel(uploaded_file)
    else:
        return None

def search_context(question, documents):
    # Simple keyword search for context
    question_words = set(question.lower().split())
    best_score = 0
    best_doc = ""
    for doc in documents:
        doc_words = set(doc.lower().split())
        score = len(question_words & doc_words)
        if score > best_score:
            best_score = score
            best_doc = doc
    return best_doc[:1500]  # Limit context size

def ask_gpt(question, context, openai_api_key):
    openai.api_key = openai_api_key
    prompt = f"You are a helpful assistant. Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

st.set_page_config(page_title="Document Q&A Chatbot", layout="wide")
st.title("📄 Document Q&A Chatbot")

st.sidebar.header("Upload your files")
uploaded_files = st.sidebar.file_uploader(
    "Upload TXT, PDF, DOCX, or Excel files", type=["txt", "pdf", "docx", "xlsx"], accept_multiple_files=True
)

openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

if 'documents' not in st.session_state:
    st.session_state['documents'] = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            text = get_file_text(uploaded_file)
            if text:
                st.session_state['documents'].append(text)
                st.success(f"Uploaded and processed: {uploaded_file.name}")
            else:
                st.error(f"Unsupported file type: {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

st.write("### Ask a question about your documents:")
question = st.text_input("Your question:")

if st.button("Ask") and question and openai_api_key:
    if not st.session_state['documents']:
        st.warning("Please upload at least one document.")
    else:
        context = search_context(question, st.session_state['documents'])
        if not context:
            st.info("No relevant context found in your documents. The answer may be generic.")
        with st.spinner("Thinking..."):
            answer = ask_gpt(question, context, openai_api_key)
        st.markdown(f"**Answer:** {answer}") 